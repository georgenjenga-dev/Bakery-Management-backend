import logging
from flask import Blueprint, request, jsonify
from app import db
from app.models.order import Order, OrderItem
from app.services.mpesa import MpesaService

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')
mpesa = MpesaService()
logger = logging.getLogger(__name__)


@payments_bp.route('/stk-push', methods=['POST'])
def stk_push():
    """
    Initiate M-Pesa STK Push payment.
    Expects JSON with customer details and order items.
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['customer_name', 'customer_email', 'customer_phone', 
                          'delivery_address', 'items', 'total_amount']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        items = data.get('items', [])
        if not items or not isinstance(items, list):
            return jsonify({'success': False, 'message': 'Order items are required'}), 400
        
        # Create order record (status: Pending)
        order = Order(
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_phone=data['customer_phone'],
            delivery_address=data['delivery_address'],
            total_amount=float(data['total_amount']),
            payment_status='Pending'
        )
        db.session.add(order)
        db.session.flush()  # Get order.id without committing
        
        # Add order items
        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product_id'],
                product_name=item['product_name'],
                quantity=item['quantity'],
                unit_price=float(item['unit_price']),
                subtotal=float(item['unit_price']) * int(item['quantity'])
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        # Initiate STK Push
        phone = data['customer_phone']
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        amount = data['total_amount']
        account_ref = f"ORDER-{order.id}"
        
        stk_response = mpesa.initiate_stk_push(
            phone_number=phone,
            amount=amount,
            account_reference=account_ref,
            transaction_desc=f"Cake Bakery Order #{order.id}"
        )
        
        # Update order with M-Pesa request IDs
        order.checkout_request_id = stk_response.get('CheckoutRequestID')
        order.merchant_request_id = stk_response.get('MerchantRequestID')
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'STK Push sent successfully. Check your phone.',
            'checkout_request_id': stk_response.get('CheckoutRequestID'),
            'merchant_request_id': stk_response.get('MerchantRequestID'),
            'order_id': order.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"STK Push error: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e) or 'Failed to initiate payment'
        }), 500


@payments_bp.route('/callback', methods=['POST'])
def mpesa_callback():
    """
    Handle M-Pesa callback from Safaricom.
    This endpoint must be publicly accessible.
    """
    try:
        callback_data = request.get_json()
        logger.info(f"M-Pesa callback received: {callback_data}")
        
        if not callback_data:
            return jsonify({'ResultCode': 1, 'ResultDesc': 'Invalid callback data'}), 400
        
        result = mpesa.validate_callback(callback_data)
        
        if result is None:
            return jsonify({'ResultCode': 1, 'ResultDesc': 'Invalid callback format'}), 400
        
        checkout_request_id = result.get('checkout_request_id')
        
        # Find order by checkout_request_id
        order = Order.query.filter_by(checkout_request_id=checkout_request_id).first()
        
        if not order:
            logger.error(f"Order not found for CheckoutRequestID: {checkout_request_id}")
            return jsonify({'ResultCode': 0, 'ResultDesc': 'Accepted'}), 200
        
        if result['success']:
            # Payment successful
            order.payment_status = 'Paid'
            order.mpesa_receipt_number = result.get('mpesa_receipt_number')
            order.transaction_date = str(result.get('transaction_date', ''))
            logger.info(f"Payment successful for Order #{order.id}: {result.get('mpesa_receipt_number')}")
        else:
            # Payment failed
            order.payment_status = 'Cancelled'
            logger.warning(f"Payment failed for Order #{order.id}: {result.get('result_desc')}")
        
        db.session.commit()
        
        # M-Pesa expects this response
        return jsonify({'ResultCode': 0, 'ResultDesc': 'Accepted'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Callback processing error: {str(e)}")
        return jsonify({'ResultCode': 0, 'ResultDesc': 'Accepted'}), 200


@payments_bp.route('/status/<checkout_request_id>', methods=['GET'])
def check_payment_status(checkout_request_id):
    """
    Check payment status by CheckoutRequestID.
    Frontend polls this endpoint.
    """
    try:
        order = Order.query.filter_by(checkout_request_id=checkout_request_id).first()
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            }), 404
        
        return jsonify({
            'success': True,
            'status': order.payment_status,
            'order_id': order.id,
            'receipt_number': order.mpesa_receipt_number,
            'amount': order.total_amount
        }), 200
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to check status'
        }), 500