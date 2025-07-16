from src.database import db
from datetime import datetime
import uuid
from enum import Enum

class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    merchant_id = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='EUR')
    status = db.Column(db.Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    payment_method = db.Column(db.Enum(PaymentMethod), nullable=False)
    
    # Customer information (tokenized/encrypted)
    customer_email = db.Column(db.String(255))
    customer_name = db.Column(db.String(255))
    
    # Card information (tokenized)
    card_token = db.Column(db.String(255))  # Tokenized card number
    card_last_four = db.Column(db.String(4))  # Last 4 digits for display
    card_brand = db.Column(db.String(50))  # Visa, Mastercard, etc.
    
    # Transaction details
    description = db.Column(db.Text)
    reference_number = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    # Security and compliance
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    user_agent = db.Column(db.Text)
    fraud_score = db.Column(db.Float)
    
    # Settlement information
    settlement_date = db.Column(db.Date)
    settlement_amount = db.Column(db.Numeric(10, 2))
    fees = db.Column(db.Numeric(10, 2))
    
    def __repr__(self):
        return f'<Payment {self.transaction_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'merchant_id': self.merchant_id,
            'amount': float(self.amount),
            'currency': self.currency,
            'status': self.status.value,
            'payment_method': self.payment_method.value,
            'customer_email': self.customer_email,
            'customer_name': self.customer_name,
            'card_last_four': self.card_last_four,
            'card_brand': self.card_brand,
            'description': self.description,
            'reference_number': self.reference_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'fraud_score': self.fraud_score,
            'settlement_date': self.settlement_date.isoformat() if self.settlement_date else None,
            'settlement_amount': float(self.settlement_amount) if self.settlement_amount else None,
            'fees': float(self.fees) if self.fees else None
        }

class TransactionLog(db.Model):
    __tablename__ = 'transaction_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(36), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # created, authorized, captured, failed, etc.
    message = db.Column(db.Text)
    response_code = db.Column(db.String(10))
    gateway_response = db.Column(db.Text)  # JSON response from payment gateway
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TransactionLog {self.transaction_id}:{self.event_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'event_type': self.event_type,
            'message': self.message,
            'response_code': self.response_code,
            'gateway_response': self.gateway_response,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

