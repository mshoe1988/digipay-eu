"""
Billing service for PayGateway merchant billing system
"""

from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, and_
from src.database import db
from src.models.billing import (
    MerchantBilling, Invoice, InvoiceItem, FeeTransaction, 
    RevenueReport, FeeType, BillingStatus, BillingCycle
)
from src.models.payment import Payment
from src.models.user import Merchant
import uuid

class BillingService:
    """Service for handling merchant billing operations"""
    
    def __init__(self):
        self.session = db.session
    
    def calculate_transaction_fee(self, amount, is_european_card=True, merchant_billing=None):
        """Calculate transaction fee based on amount and card type"""
        if merchant_billing is None:
            # Use default rates
            if is_european_card:
                percentage = 0.5  # 0.5%
                fixed_fee = 0.10  # €0.10
            else:
                percentage = 2.4  # 2.4%
                fixed_fee = 0.20  # €0.20
        else:
            if is_european_card:
                percentage = merchant_billing.european_card_percentage
                fixed_fee = merchant_billing.european_card_fixed_fee
            else:
                percentage = merchant_billing.non_european_card_percentage
                fixed_fee = merchant_billing.non_european_card_fixed_fee
        
        # Calculate fee
        percentage_fee = Decimal(str(amount)) * Decimal(str(percentage)) / Decimal('100')
        total_fee = percentage_fee + Decimal(str(fixed_fee))
        
        # Round to 2 decimal places
        return float(total_fee.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    def record_transaction_fee(self, payment_transaction, is_european_card=True):
        """Record a transaction fee for a payment"""
        try:
            # Get merchant billing configuration
            merchant_billing = self.get_or_create_merchant_billing(payment_transaction.merchant_id)
            
            # Calculate fee
            fee_amount = self.calculate_transaction_fee(
                payment_transaction.amount, 
                is_european_card, 
                merchant_billing
            )
            
            # Create fee transaction record
            fee_transaction = FeeTransaction(
                merchant_billing_id=merchant_billing.id,
                payment_transaction_id=payment_transaction.transaction_id,
                fee_type=FeeType.TRANSACTION_FEE,
                fee_amount=fee_amount,
                fee_percentage=merchant_billing.european_card_percentage if is_european_card else merchant_billing.non_european_card_percentage,
                fixed_fee=merchant_billing.european_card_fixed_fee if is_european_card else merchant_billing.non_european_card_fixed_fee,
                original_amount=payment_transaction.amount,
                currency=payment_transaction.currency,
                is_european_card=is_european_card
            )
            
            self.session.add(fee_transaction)
            self.session.commit()
            
            return fee_transaction
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def record_chargeback_fee(self, payment_transaction):
        """Record a chargeback fee"""
        try:
            merchant_billing = self.get_or_create_merchant_billing(payment_transaction.merchant_id)
            
            fee_transaction = FeeTransaction(
                merchant_billing_id=merchant_billing.id,
                payment_transaction_id=payment_transaction.transaction_id,
                fee_type=FeeType.CHARGEBACK_FEE,
                fee_amount=merchant_billing.chargeback_fee,
                original_amount=payment_transaction.amount,
                currency=payment_transaction.currency
            )
            
            self.session.add(fee_transaction)
            self.session.commit()
            
            return fee_transaction
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def record_refund_fee(self, payment_transaction):
        """Record a refund fee"""
        try:
            merchant_billing = self.get_or_create_merchant_billing(payment_transaction.merchant_id)
            
            fee_transaction = FeeTransaction(
                merchant_billing_id=merchant_billing.id,
                payment_transaction_id=payment_transaction.transaction_id,
                fee_type=FeeType.REFUND_FEE,
                fee_amount=merchant_billing.refund_fee,
                original_amount=payment_transaction.amount,
                currency=payment_transaction.currency
            )
            
            self.session.add(fee_transaction)
            self.session.commit()
            
            return fee_transaction
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_or_create_merchant_billing(self, merchant_id):
        """Get or create merchant billing configuration"""
        merchant_billing = self.session.query(MerchantBilling).filter_by(merchant_id=merchant_id).first()
        
        if not merchant_billing:
            merchant_billing = MerchantBilling(
                merchant_id=merchant_id,
                billing_email=f"{merchant_id}@example.com"  # Default, should be updated
            )
            self.session.add(merchant_billing)
            self.session.commit()
        
        return merchant_billing
    
    def generate_invoice(self, merchant_id, period_start, period_end):
        """Generate an invoice for a merchant for a specific period"""
        try:
            merchant_billing = self.get_or_create_merchant_billing(merchant_id)
            
            # Get all uninvoiced fee transactions for the period
            fee_transactions = self.session.query(FeeTransaction).filter(
                and_(
                    FeeTransaction.merchant_billing_id == merchant_billing.id,
                    FeeTransaction.created_at >= period_start,
                    FeeTransaction.created_at <= period_end,
                    FeeTransaction.is_invoiced == False
                )
            ).all()
            
            if not fee_transactions:
                return None  # No fees to invoice
            
            # Create invoice
            invoice_number = self.generate_invoice_number()
            invoice = Invoice(
                invoice_number=invoice_number,
                merchant_billing_id=merchant_billing.id,
                billing_period_start=period_start,
                billing_period_end=period_end,
                due_date=datetime.utcnow() + timedelta(days=30)  # 30 days payment terms
            )
            
            self.session.add(invoice)
            self.session.flush()  # Get invoice ID
            
            # Group fee transactions by type
            fee_groups = {}
            for fee_tx in fee_transactions:
                fee_type = fee_tx.fee_type
                if fee_type not in fee_groups:
                    fee_groups[fee_type] = []
                fee_groups[fee_type].append(fee_tx)
            
            # Create invoice items
            subtotal = 0
            for fee_type, transactions in fee_groups.items():
                if fee_type == FeeType.TRANSACTION_FEE:
                    # Group transaction fees by card type
                    european_fees = [tx for tx in transactions if tx.is_european_card]
                    non_european_fees = [tx for tx in transactions if not tx.is_european_card]
                    
                    if european_fees:
                        total_amount = sum(tx.fee_amount for tx in european_fees)
                        item = InvoiceItem(
                            invoice_id=invoice.id,
                            description=f"European Card Transaction Fees ({len(european_fees)} transactions)",
                            fee_type=fee_type,
                            quantity=len(european_fees),
                            unit_price=total_amount / len(european_fees),
                            total_price=total_amount
                        )
                        self.session.add(item)
                        subtotal += total_amount
                    
                    if non_european_fees:
                        total_amount = sum(tx.fee_amount for tx in non_european_fees)
                        item = InvoiceItem(
                            invoice_id=invoice.id,
                            description=f"Non-European Card Transaction Fees ({len(non_european_fees)} transactions)",
                            fee_type=fee_type,
                            quantity=len(non_european_fees),
                            unit_price=total_amount / len(non_european_fees),
                            total_price=total_amount
                        )
                        self.session.add(item)
                        subtotal += total_amount
                else:
                    # Other fee types
                    total_amount = sum(tx.fee_amount for tx in transactions)
                    description_map = {
                        FeeType.CHARGEBACK_FEE: "Chargeback Fees",
                        FeeType.REFUND_FEE: "Refund Fees",
                        FeeType.MONTHLY_FEE: "Monthly Fees",
                        FeeType.SETUP_FEE: "Setup Fees"
                    }
                    
                    item = InvoiceItem(
                        invoice_id=invoice.id,
                        description=f"{description_map.get(fee_type, 'Other Fees')} ({len(transactions)} items)",
                        fee_type=fee_type,
                        quantity=len(transactions),
                        unit_price=total_amount / len(transactions),
                        total_price=total_amount
                    )
                    self.session.add(item)
                    subtotal += total_amount
            
            # Calculate tax (assuming 0% for now, can be configured)
            tax_rate = 0.0
            tax_amount = subtotal * tax_rate
            total_amount = subtotal + tax_amount
            
            # Update invoice totals
            invoice.subtotal = subtotal
            invoice.tax_amount = tax_amount
            invoice.total_amount = total_amount
            
            # Mark fee transactions as invoiced
            for fee_tx in fee_transactions:
                fee_tx.is_invoiced = True
                fee_tx.invoice_id = invoice.id
            
            self.session.commit()
            
            return invoice
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def generate_invoice_number(self):
        """Generate a unique invoice number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"INV-{timestamp}-{random_suffix}"
    
    def get_merchant_revenue_summary(self, merchant_id, period_start=None, period_end=None):
        """Get revenue summary for a merchant"""
        if period_start is None:
            period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if period_end is None:
            period_end = datetime.utcnow()
        
        merchant_billing = self.get_or_create_merchant_billing(merchant_id)
        
        # Get fee transactions for the period
        fee_transactions = self.session.query(FeeTransaction).filter(
            and_(
                FeeTransaction.merchant_billing_id == merchant_billing.id,
                FeeTransaction.created_at >= period_start,
                FeeTransaction.created_at <= period_end
            )
        ).all()
        
        # Calculate summary
        summary = {
            'total_revenue': sum(tx.fee_amount for tx in fee_transactions),
            'transaction_fees': sum(tx.fee_amount for tx in fee_transactions if tx.fee_type == FeeType.TRANSACTION_FEE),
            'chargeback_fees': sum(tx.fee_amount for tx in fee_transactions if tx.fee_type == FeeType.CHARGEBACK_FEE),
            'refund_fees': sum(tx.fee_amount for tx in fee_transactions if tx.fee_type == FeeType.REFUND_FEE),
            'transaction_count': len([tx for tx in fee_transactions if tx.fee_type == FeeType.TRANSACTION_FEE]),
            'european_transactions': len([tx for tx in fee_transactions if tx.fee_type == FeeType.TRANSACTION_FEE and tx.is_european_card]),
            'non_european_transactions': len([tx for tx in fee_transactions if tx.fee_type == FeeType.TRANSACTION_FEE and not tx.is_european_card]),
            'period_start': period_start,
            'period_end': period_end
        }
        
        return summary
    
    def get_total_revenue_summary(self, period_start=None, period_end=None):
        """Get total revenue summary across all merchants"""
        if period_start is None:
            period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if period_end is None:
            period_end = datetime.utcnow()
        
        # Get all fee transactions for the period
        fee_transactions = self.session.query(FeeTransaction).filter(
            and_(
                FeeTransaction.created_at >= period_start,
                FeeTransaction.created_at <= period_end
            )
        ).all()
        
        # Calculate summary
        summary = {
            'total_revenue': sum(tx.fee_amount for tx in fee_transactions),
            'transaction_fees': sum(tx.fee_amount for tx in fee_transactions if tx.fee_type == FeeType.TRANSACTION_FEE),
            'chargeback_fees': sum(tx.fee_amount for tx in fee_transactions if tx.fee_type == FeeType.CHARGEBACK_FEE),
            'refund_fees': sum(tx.fee_amount for tx in fee_transactions if tx.fee_type == FeeType.REFUND_FEE),
            'total_transactions': len([tx for tx in fee_transactions if tx.fee_type == FeeType.TRANSACTION_FEE]),
            'european_transactions': len([tx for tx in fee_transactions if tx.fee_type == FeeType.TRANSACTION_FEE and tx.is_european_card]),
            'non_european_transactions': len([tx for tx in fee_transactions if tx.fee_type == FeeType.TRANSACTION_FEE and not tx.is_european_card]),
            'active_merchants': len(set(tx.merchant_billing.merchant_id for tx in fee_transactions)),
            'period_start': period_start,
            'period_end': period_end
        }
        
        return summary
    
    def process_automatic_billing(self):
        """Process automatic billing for all merchants with auto-billing enabled"""
        today = datetime.utcnow().date()
        
        # Get all merchant billings with auto-billing enabled
        merchant_billings = self.session.query(MerchantBilling).filter(
            MerchantBilling.auto_billing_enabled == True
        ).all()
        
        invoices_generated = []
        
        for merchant_billing in merchant_billings:
            # Check if it's time to generate an invoice
            if self.should_generate_invoice(merchant_billing, today):
                period_start, period_end = self.get_billing_period(merchant_billing, today)
                
                try:
                    invoice = self.generate_invoice(
                        merchant_billing.merchant_id,
                        period_start,
                        period_end
                    )
                    if invoice:
                        invoices_generated.append(invoice)
                except Exception as e:
                    print(f"Error generating invoice for merchant {merchant_billing.merchant_id}: {e}")
        
        return invoices_generated
    
    def should_generate_invoice(self, merchant_billing, today):
        """Check if an invoice should be generated for a merchant"""
        if merchant_billing.billing_cycle == BillingCycle.MONTHLY:
            return today.day == merchant_billing.billing_day
        elif merchant_billing.billing_cycle == BillingCycle.WEEKLY:
            return today.weekday() == merchant_billing.billing_day
        elif merchant_billing.billing_cycle == BillingCycle.DAILY:
            return True
        
        return False
    
    def get_billing_period(self, merchant_billing, today):
        """Get the billing period for a merchant"""
        if merchant_billing.billing_cycle == BillingCycle.MONTHLY:
            # Previous month
            if today.month == 1:
                period_start = datetime(today.year - 1, 12, 1)
                period_end = datetime(today.year, 1, 1) - timedelta(seconds=1)
            else:
                period_start = datetime(today.year, today.month - 1, 1)
                period_end = datetime(today.year, today.month, 1) - timedelta(seconds=1)
        elif merchant_billing.billing_cycle == BillingCycle.WEEKLY:
            # Previous week
            period_end = datetime.combine(today, datetime.min.time()) - timedelta(seconds=1)
            period_start = period_end - timedelta(days=6)
            period_start = period_start.replace(hour=0, minute=0, second=0, microsecond=0)
        else:  # DAILY
            # Previous day
            period_start = datetime.combine(today - timedelta(days=1), datetime.min.time())
            period_end = datetime.combine(today, datetime.min.time()) - timedelta(seconds=1)
        
        return period_start, period_end

