import re
import base64
import datetime
import uuid
import requests
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from requests.auth import HTTPBasicAuth
from werkzeug.security import generate_password_hash
from database import db
from models import Payment, User, Order, OrderItem, Products

payment_bp = Blueprint('payments', __name__)

# ----------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------

def sanitize_phone_number(phone_str: str) -> str:
    """
    Formats phone numbers to Safaricom's required format (254XXXXXXXXX).
    """
    phone = re.sub(r'\D', '', phone_str)
    if phone.startswith('0'):
        phone = '254' + phone[1:]
    elif phone.startswith('7') or phone.startswith('1'):
        phone = '254' + phone
    return phone


def get_daraja_access_token():
    """
    Retrieves OAuth access token from Safaricom Daraja API.
    """
    consumer_key = current_app.config.get('DARAJA_CONSUMER_KEY')
    consumer_secret = current_app.config.get('DARAJA_CONSUMER_SECRET')
    
    if not consumer_key or not consumer_secret:
        return None, "Daraja consumer credentials missing"

    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    try:
        res = requests.get(
            auth_url,
            auth=HTTPBasicAuth(consumer_key, consumer_secret),
            timeout=10
        )
        if res.status_code == 200:
            return res.json().get('access_token'), None
        return None, f"OAuth HTTP {res.status_code}: {res.text}"
    except Exception as e:
        return None, f"OAuth Connection Error: {str(e)}"


# ----------------------------------------------------
# ENDPOINTS
# ----------------------------------------------------

@payment_bp.route('/stk-push', methods=['POST'])
def stk_push_payment():
    try:
        current_user_id = None
        try:
            verify_jwt_in_request(optional=True)
            current_user_id = get_jwt_identity()
        except Exception:
            current_user_id = None

        data = request.get_json() or {}
        raw_phone = str(data.get('phone', '')).strip()
        raw_amount = str(data.get('amount', '')).strip()
        name = str(data.get('name', 'Guest')).strip()
        order_id = data.get('order_id')
        items = data.get('items', [])

        # 1. Sanitize Amount and Phone Number
        cleaned_amount = re.sub(r'[^\d.]', '', raw_amount)
        if not cleaned_amount:
            return jsonify({'success': False, 'message': 'Invalid payment amount'}), 400
        
        parsed_amount = float(cleaned_amount)
        numeric_amount_int = int(round(parsed_amount))
        phone = sanitize_phone_number(raw_phone)

        if not re.match(r'^254[71]\d{8}$', phone):
            return jsonify({'success': False, 'message': 'Invalid Kenyan phone number format. Use 07XX or 01XX.'}), 400

        if parsed_amount <= 0:
            return jsonify({'success': False, 'message': 'Amount must be greater than 0'}), 400

        # 2. Resolve User / Guest User
        if not current_user_id:
            user = User.query.filter_by(phone=phone).first()
            if not user:
                user = User(
                    username=f"{name}_{phone[-4:]}",
                    email=f"guest_{phone}_{uuid.uuid4().hex[:4]}@sokocommerce.local",
                    phone=phone,
                    password_hash=generate_password_hash(uuid.uuid4().hex),
                    is_admin=False,
                    role='GUEST'
                )
                db.session.add(user)
                db.session.flush()
            current_user_id = user.id

        # 3. Create or Resolve Order
        if not order_id:
            generated_tracking = f"TRK-{uuid.uuid4().hex[:8].upper()}"
            new_order = Order(
                user_id=current_user_id,
                total_amount=parsed_amount,
                status='PENDING',
                tracking_number=generated_tracking
            )
            db.session.add(new_order)
            db.session.flush()
            order_id = new_order.id

            if isinstance(items, list) and len(items) > 0:
                for item in items:
                    p_id = item.get('id') or item.get('product_id')
                    qty = item.get('quantity', 1)
                    price = item.get('price', 0.0)
                    if p_id:
                        db.session.add(OrderItem(
                            order_id=order_id,
                            product_id=p_id,
                            quantity=qty,
                            price=float(price)
                        ))

        db.session.commit()

        # 4. Fetch Config & Access Token
        passkey = current_app.config.get('DARAJA_PASSKEY')
        business_short_code = current_app.config.get('DARAJA_BUSINESS_SHORT_CODE', '174379')
        callback_url = current_app.config.get('DARAJA_CALLBACK_URL')

        if not passkey or not callback_url:
            return jsonify({'success': False, 'message': 'M-Pesa service configuration missing on server.'}), 500

        access_token, err = get_daraja_access_token()
        if not access_token:
            return jsonify({'success': False, 'message': f'Gateway auth error: {err}'}), 500

        # 5. Security Password & STK Payload Creation
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        data_to_encode = f"{business_short_code}{passkey}{timestamp}"
        password = base64.b64encode(data_to_encode.encode()).decode('utf-8')

        payload = {
            "BusinessShortCode": business_short_code,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": numeric_amount_int,
            "PartyA": phone,
            "PartyB": business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": callback_url,
            "AccountReference": "Fanya haraka mschana Comrade atakufa njaa",
            # "AccountReference": f"Order-{order_id}",
            # "TransactionDesc": f"Payment for Order #{order_id}"
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        stk_res = requests.post(stk_url, json=payload, headers=headers, timeout=12)
        res_data = stk_res.json()

        if res_data.get('ResponseCode') == '0':
            checkout_id = res_data.get('CheckoutRequestID')
            merchant_id = res_data.get('MerchantRequestID')

            new_payment = Payment(
                user_id=current_user_id,
                order_id=order_id,
                checkout_request_id=checkout_id,
                merchant_request_id=merchant_id,
                phone_number=phone,
                amount=parsed_amount,
                status='PENDING'
            )
            db.session.add(new_payment)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'STK Push sent. Please enter your M-Pesa PIN on your phone.',
                'checkoutRequestId': checkout_id,
                'order_id': order_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': res_data.get('CustomerMessage', 'Failed to initiate STK Push payment.')
            }), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f"Server Error: {str(e)}"}), 500


@payment_bp.route('/callback', methods=['POST'])
def mpesa_callback():
    """
    Handles background webhook payloads sent by Safaricom Daraja API.
    """
    try:
        data = request.get_json(force=True) or {}
        stk_callback = data.get('Body', {}).get('stkCallback', {})
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')

        payment = Payment.query.filter_by(checkout_request_id=checkout_request_id).first()

        if payment:
            payment.result_desc = result_desc
            order = Order.query.get(payment.order_id) if payment.order_id else None

            if result_code == 0:
                payment.status = 'COMPLETED'
                items = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                for item in items:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        payment.mpesa_receipt_number = item.get('Value')

                if order:
                    order.status = 'PAID'
            else:
                # Handle cancelled or failed transactions
                payment.status = 'FAILED'
                if order:
                    order.status = 'CANCELLED'
                    # Restore stock levels if order was cancelled
                    if hasattr(order, 'items') and order.items:
                        for order_item in order.items:
                            product = Products.query.get(order_item.product_id)
                            if product:
                                product.stock = (product.stock or 0) + order_item.quantity

            db.session.commit()

        # Always respond with ResultCode 0 to acknowledge receipt to Safaricom
        return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"ResultCode": 0, "ResultDesc": f"Error handled: {str(e)}"}), 200


@payment_bp.route('/status/<checkout_id>', methods=['GET'])
def check_payment_status(checkout_id):
    """
    Polling endpoint for front-end clients to check transaction status.
    """
    payment = Payment.query.filter_by(checkout_request_id=checkout_id).first()
    if not payment:
        return jsonify({'success': False, 'message': 'Transaction not found'}), 404

    tracking_number = None
    if payment.order_id:
        order = Order.query.get(payment.order_id)
        if order:
            tracking_number = getattr(order, 'tracking_number', f"TRK-{order.id}")

    return jsonify({
        'success': True,
        'status': payment.status,
        'receipt': getattr(payment, 'mpesa_receipt_number', None),
        'tracking_number': tracking_number or f"TRK-{payment.id}",
        'message': payment.result_desc or 'Processing payment'
    }), 200