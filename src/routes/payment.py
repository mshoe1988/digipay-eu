from flask import Blueprint, jsonify, request
from flask_babel import gettext, ngettext
from src.database import db
from src.models.payment import Payment, TransactionLog, PaymentStatus, PaymentMethod
from src.models.user import Merchant
from src.services.payment_processor import PaymentProcessor
from src.services.fraud_detection import FraudDetectionService
from src.services.encryption import EncryptionService
from src.services.compliance import ComplianceService
from src.services.security import SecurityService, require_auth, rate_limit
import uuid
from datetime import datetime
import logging

payment_bp = Blueprint('payment', __name__)
logger = logging.getLogger(__name__)

# Initialize services
compliance_service = ComplianceService()
security_service = SecurityService()

@payment_bp.route('/payments', methods=['POST'])
@require_auth
@rate_limit(max_requests=50, window_minutes=60)
def create_payment():
    """
    Create a new payment transaction
    """
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['merchant_id', 'amount', 'currency', 'payment_method']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': gettext('Missing required field: %(field)s', field=field)}), 400
        
        # Validate merchant
        merchant = Merchant.query.filter_by(merchant_id=data['merchant_id']).first()
        if not merchant or not merchant.is_active:
            return jsonify({'error': gettext('Invalid or inactive merchant')}), 401
        
        # Create payment record
        payment = Payment(
            transaction_id=str(uuid.uuid4()),
            merchant_id=data['merchant_id'],
            amount=data['amount'],
            currency=data['currency'],
            payment_method=PaymentMethod(data['payment_method']),
            customer_email=data.get('customer_email'),
            customer_name=data.get('customer_name'),
            description=data.get('description'),
            reference_number=data.get('reference_number'),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        # Handle card information (tokenization)
        if 'card_number' in data:
            encryption_service = EncryptionService()
            payment.card_token = encryption_service.tokenize_card(data['card_number'])
            payment.card_last_four = data['card_number'][-4:]
            payment.card_brand = data.get('card_brand', 'Unknown')
        
        # Fraud detection
        fraud_service = FraudDetectionService()
        fraud_score = fraud_service.analyze_transaction(payment, data)
        payment.fraud_score = fraud_score
        
        if fraud_score > 0.8:  # High fraud risk
            payment.status = PaymentStatus.FAILED
            log_entry = TransactionLog(
                transaction_id=payment.transaction_id,
                event_type='fraud_detected',
                message=f'High fraud score: {fraud_score}',
                response_code='FRAUD'
            )
            db.session.add(log_entry)
        
        db.session.add(payment)
        db.session.commit()
        
        # Log transaction creation
        log_entry = TransactionLog(
            transaction_id=payment.transaction_id,
            event_type='created',
            message='Payment transaction created',
            response_code='200'
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify(payment.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@payment_bp.route('/payments/<transaction_id>/process', methods=['POST'])
def process_payment(transaction_id):
    """
    Process a payment transaction
    """
    try:
        payment = Payment.query.filter_by(transaction_id=transaction_id).first()
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        if payment.status != PaymentStatus.PENDING:
            return jsonify({'error': 'Payment cannot be processed'}), 400
        
        # Update status to processing
        payment.status = PaymentStatus.PROCESSING
        payment.updated_at = datetime.utcnow()
        
        # Process payment through payment processor
        processor = PaymentProcessor()
        result = processor.process_payment(payment)
        
        if result['success']:
            payment.status = PaymentStatus.COMPLETED
            payment.processed_at = datetime.utcnow()
            
            log_entry = TransactionLog(
                transaction_id=payment.transaction_id,
                event_type='completed',
                message='Payment processed successfully',
                response_code=result.get('response_code', '200'),
                gateway_response=str(result)
            )
        else:
            payment.status = PaymentStatus.FAILED
            
            log_entry = TransactionLog(
                transaction_id=payment.transaction_id,
                event_type='failed',
                message=result.get('error', 'Payment processing failed'),
                response_code=result.get('response_code', '500'),
                gateway_response=str(result)
            )
        
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify(payment.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@payment_bp.route('/payments/<transaction_id>', methods=['GET'])
def get_payment(transaction_id):
    """
    Get payment details by transaction ID
    """
    try:
        payment = Payment.query.filter_by(transaction_id=transaction_id).first()
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        return jsonify(payment.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error retrieving payment: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@payment_bp.route('/payments', methods=['GET'])
def get_payments():
    """
    Get payments with optional filtering
    """
    try:
        merchant_id = request.args.get('merchant_id')
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        query = Payment.query
        
        if merchant_id:
            query = query.filter_by(merchant_id=merchant_id)
        
        if status:
            query = query.filter_by(status=PaymentStatus(status))
        
        payments = query.order_by(Payment.created_at.desc()).offset(offset).limit(limit).all()
        
        return jsonify([payment.to_dict() for payment in payments]), 200
        
    except Exception as e:
        logger.error(f"Error retrieving payments: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@payment_bp.route('/payments/<transaction_id>/refund', methods=['POST'])
def refund_payment(transaction_id):
    """
    Refund a payment transaction
    """
    try:
        payment = Payment.query.filter_by(transaction_id=transaction_id).first()
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        if payment.status != PaymentStatus.COMPLETED:
            return jsonify({'error': 'Payment cannot be refunded'}), 400
        
        data = request.json
        refund_amount = data.get('amount', payment.amount)
        
        if refund_amount > payment.amount:
            return jsonify({'error': 'Refund amount cannot exceed payment amount'}), 400
        
        # Process refund
        processor = PaymentProcessor()
        result = processor.refund_payment(payment, refund_amount)
        
        if result['success']:
            payment.status = PaymentStatus.REFUNDED
            payment.updated_at = datetime.utcnow()
            
            log_entry = TransactionLog(
                transaction_id=payment.transaction_id,
                event_type='refunded',
                message=f'Payment refunded: {refund_amount}',
                response_code=result.get('response_code', '200'),
                gateway_response=str(result)
            )
        else:
            log_entry = TransactionLog(
                transaction_id=payment.transaction_id,
                event_type='refund_failed',
                message=result.get('error', 'Refund processing failed'),
                response_code=result.get('response_code', '500'),
                gateway_response=str(result)
            )
        
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify(payment.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error processing refund: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@payment_bp.route('/payments/<transaction_id>/logs', methods=['GET'])
def get_payment_logs(transaction_id):
    """
    Get transaction logs for a payment
    """
    try:
        logs = TransactionLog.query.filter_by(transaction_id=transaction_id).order_by(TransactionLog.created_at.desc()).all()
        
        return jsonify([log.to_dict() for log in logs]), 200
        
    except Exception as e:
        logger.error(f"Error retrieving payment logs: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

