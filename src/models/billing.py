"""
Billing models for PayGateway merchant billing system
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from src.database import db
import enum

class BillingCycle(enum.Enum):
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    DAILY = "daily"

class FeeType(enum.Enum):
    TRANSACTION_FEE = "transaction_fee"
    CHARGEBACK_FEE = "chargeback_fee"
    REFUND_FEE = "refund_fee"
    MONTHLY_FEE = "monthly_fee"
    SETUP_FEE = "setup_fee"

class BillingStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class MerchantBilling(db.Model):
    """Merchant billing configuration and settings"""
    __tablename__ = 'merchant_billing'
    
    id = Column(Integer, primary_key=True)
    merchant_id = Column(String(100), ForeignKey('merchants.merchant_id'), nullable=False, unique=True)
    
    # Fee structure
    european_card_percentage = Column(Float, default=0.5)  # 0.5%
    european_card_fixed_fee = Column(Float, default=0.10)  # €0.10
    non_european_card_percentage = Column(Float, default=2.4)  # 2.4%
    non_european_card_fixed_fee = Column(Float, default=0.20)  # €0.20
    chargeback_fee = Column(Float, default=9.00)  # €9.00
    refund_fee = Column(Float, default=0.05)  # €0.05
    
    # Billing settings
    billing_cycle = Column(Enum(BillingCycle), default=BillingCycle.MONTHLY)
    billing_day = Column(Integer, default=1)  # Day of month for monthly billing
    auto_billing_enabled = Column(Boolean, default=True)
    
    # Contact and payment info
    billing_email = Column(String(255))
    billing_address = Column(Text)
    payment_method = Column(String(50))  # bank_transfer, card, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    merchant = relationship("Merchant", back_populates="billing")
    invoices = relationship("Invoice", back_populates="merchant_billing")
    fee_transactions = relationship("FeeTransaction", back_populates="merchant_billing")

class Invoice(db.Model):
    """Billing invoices for merchants"""
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    merchant_billing_id = Column(Integer, ForeignKey('merchant_billing.id'), nullable=False)
    
    # Invoice details
    billing_period_start = Column(DateTime, nullable=False)
    billing_period_end = Column(DateTime, nullable=False)
    
    # Amounts
    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    
    # Status and dates
    status = Column(Enum(BillingStatus), default=BillingStatus.PENDING)
    issued_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    paid_date = Column(DateTime)
    
    # Payment details
    payment_reference = Column(String(100))
    payment_method = Column(String(50))
    
    # Additional info
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    merchant_billing = relationship("MerchantBilling", back_populates="invoices")
    invoice_items = relationship("InvoiceItem", back_populates="invoice")

class InvoiceItem(db.Model):
    """Individual line items on invoices"""
    __tablename__ = 'invoice_items'
    
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    
    # Item details
    description = Column(String(255), nullable=False)
    fee_type = Column(Enum(FeeType), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Reference to original transaction if applicable
    transaction_id = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="invoice_items")

class FeeTransaction(db.Model):
    """Individual fee transactions for tracking revenue"""
    __tablename__ = 'fee_transactions'
    
    id = Column(Integer, primary_key=True)
    merchant_billing_id = Column(Integer, ForeignKey('merchant_billing.id'), nullable=False)
    
    # Transaction reference
    payment_transaction_id = Column(String(100), ForeignKey('payments.transaction_id'))
    
    # Fee details
    fee_type = Column(Enum(FeeType), nullable=False)
    fee_amount = Column(Float, nullable=False)
    fee_percentage = Column(Float)
    fixed_fee = Column(Float)
    
    # Transaction details
    original_amount = Column(Float)  # Original transaction amount
    currency = Column(String(3), default='EUR')
    is_european_card = Column(Boolean, default=True)
    
    # Status
    is_invoiced = Column(Boolean, default=False)
    invoice_id = Column(Integer, ForeignKey('invoices.id'))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    merchant_billing = relationship("MerchantBilling", back_populates="fee_transactions")
    payment_transaction = relationship("Payment")

class RevenueReport(db.Model):
    """Revenue reporting and analytics"""
    __tablename__ = 'revenue_reports'
    
    id = Column(Integer, primary_key=True)
    
    # Report details
    report_type = Column(String(50), nullable=False)  # daily, weekly, monthly, yearly
    report_date = Column(DateTime, nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Revenue metrics
    total_revenue = Column(Float, default=0.0)
    transaction_fee_revenue = Column(Float, default=0.0)
    chargeback_fee_revenue = Column(Float, default=0.0)
    refund_fee_revenue = Column(Float, default=0.0)
    other_fee_revenue = Column(Float, default=0.0)
    
    # Transaction metrics
    total_transactions = Column(Integer, default=0)
    total_transaction_volume = Column(Float, default=0.0)
    european_transactions = Column(Integer, default=0)
    non_european_transactions = Column(Integer, default=0)
    
    # Merchant metrics
    active_merchants = Column(Integer, default=0)
    new_merchants = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Add billing relationship to existing Merchant model
def setup_billing_relationships():
    """Add billing relationship to existing Merchant model"""
    from src.models.user import Merchant
    from sqlalchemy.orm import relationship
    
    # Add the relationship if it doesn't exist
    if not hasattr(Merchant, 'billing'):
        Merchant.billing = relationship("MerchantBilling", back_populates="merchant", uselist=False)

