import logging
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.order import Order, OrderItem
from app.services.mpesa import MpesaService

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')
mpesa = MpesaService()
logger = logging.getLogger(__name__)


@payments_bp.route('/stk-push', methods=['POST'])
def stk_push():
    """
    Initiate M-Pesa STK Push payment
    ---
    tags:
      - Payments
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - customer_name
            - customer_email
            - customer_phone
            - delivery_address
            - items
            - total_amount
          properties:
            customer_name:
              type: string
              example: "Jane Wanjiru"
            customer_email:
              type: string
              example: "jane@example.com"
            customer_phone:
              type: string
              example: "254712345678"
            delivery_address:
              type: string
              example: "Kilimani, Nairobi"
            total_amount:
              type: number
              example: 1500.00
            items:
              type: array
              items:
                type: object
                required:
                  - product_id
                  - product_name
                  - quantity
                  - unit_price
                properties:
                  product_id:
                    type: integer
                    example: 1
                  product_name:
                    type: string
                    example: "Chocolate Cake"
                  quantity:
                    type: integer
                    example: 2
                  unit_price:
                    type: number
                    example: 750.00
    responses:
      200:
        description: STK Push sent successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            checkout_request_id:
              type: string
            merchant_request_id:
              type: string
            order_id:
              type: integer
      400:
        description: Missing required field
      500:
        description: Failed to initiate payment
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
    Handle M-Pesa callback from Safaricom
    ---
    tags:
      - Payments
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          description: M-Pesa callback payload from Safaricom
    responses:
      200:
        description: Callback accepted
        schema:
          type: object
          properties:
            ResultCode:
              type: integer
              example: 0
            ResultDesc:
              type: string
              example: "Accepted"
      400:
        description: Invalid callback data
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
    Check payment status by CheckoutRequestID
    ---
    tags:
      - Payments
    parameters:
      - in: path
        name: checkout_request_id
        required: true
        type: string
        description: The M-Pesa CheckoutRequestID
    responses:
      200:
        description: Payment status details
        schema:
          type: object
          properties:
            success:
              type: boolean
            status:
              type: string
            order_id:
              type: integer
            receipt_number:
              type: string
            amount:
              type: number
      404:
        description: Order not found
      500:
        description: Failed to check status
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