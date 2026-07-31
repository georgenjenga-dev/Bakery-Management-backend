import base64
import json
import logging
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth

from config import Config

logger = logging.getLogger(__name__)

class MpesaService:
    def __init__(self):
        self.base_url = Config.MPESA_BASE_URL
        self.consumer_key = Config.MPESA_CONSUMER_KEY
        self.consumer_secret = Config.MPESA_CONSUMER_SECRET
        self.shortcode = Config.MPESA_BUSINESS_SHORTCODE
        self.passkey = Config.MPESA_PASSKEY
        self.callback_url = Config.MPESA_CALLBACK_URL

    def _get_access_token(self):
        """Fetch OAuth access token from Safaricom."""
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        try:
            response = requests.get(
                url,
                auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret),
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get('access_token')
        except requests.RequestException as e:
            logger.error(f"Failed to get M-Pesa access token: {str(e)}")
            raise Exception("Unable to connect to M-Pesa. Please try again later.")

    def _generate_password(self, timestamp):
        """Generate the password for STK push."""
        data_string = f"{self.shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(data_string.encode()).decode('utf-8')

    def initiate_stk_push(self, phone_number, amount, account_reference, transaction_desc, callback_url=None):
        """
        Initiate an STK Push request to customer's phone.
        
        Args:
            phone_number: Customer phone in format 2547XXXXXXXX
            amount: Amount to charge
            account_reference: Order ID or reference
            transaction_desc: Description of transaction
            callback_url: Optional override for callback URL
        
        Returns:
            dict: Response from Safaricom including CheckoutRequestID
        """
        access_token = self._get_access_token()
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = self._generate_password(timestamp)
        
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(amount),
            'PartyA': phone_number,
            'PartyB': self.shortcode,
            'PhoneNumber': phone_number,
            'CallBackURL': callback_url or self.callback_url,
            'AccountReference': str(account_reference),
            'TransactionDesc': transaction_desc
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"STK Push initiated: {result.get('CheckoutRequestID')}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"STK Push failed: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise Exception("Failed to initiate M-Pesa payment. Please try again.")

    def validate_callback(self, callback_data):
        """
        Validate and extract data from M-Pesa callback.
        
        Args:
            callback_data: The raw JSON payload from Safaricom
        
        Returns:
            dict: Extracted payment details or None if failed
        """
        try:
            stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
            
            result_code = stk_callback.get('ResultCode')
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            merchant_request_id = stk_callback.get('MerchantRequestID')
            result_desc = stk_callback.get('ResultDesc')
            
            if result_code != 0:
                logger.warning(f"Payment failed: {result_desc} (Code: {result_code})")
                return {
                    'success': False,
                    'checkout_request_id': checkout_request_id,
                    'merchant_request_id': merchant_request_id,
                    'result_code': result_code,
                    'result_desc': result_desc
                }
            
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            metadata = {item['Name']: item.get('Value') for item in callback_metadata}
            
            return {
                'success': True,
                'checkout_request_id': checkout_request_id,
                'merchant_request_id': merchant_request_id,
                'mpesa_receipt_number': metadata.get('MpesaReceiptNumber'),
                'transaction_date': metadata.get('TransactionDate'),
                'phone_number': metadata.get('PhoneNumber'),
                'amount': metadata.get('Amount'),
                'result_desc': result_desc
            }
            
        except Exception as e:
            logger.error(f"Callback validation error: {str(e)}")
            return None