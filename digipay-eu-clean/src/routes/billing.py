"""
Billing API routes for PayGateway
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.services.billing_service import BillingService
from src.models.billing import MerchantBilling, Invoice, FeeTransaction, BillingStatus
from src.database import db
from src.services.security import require_auth
import traceback

billing_bp = Blueprint('billing', __name__)
billing_service = BillingService()

@billing_bp.route('/api/billing/merchants/<merchant_id>/config', methods=['GET'])
@require_auth
def get_merchant_billing_config(merchant_id):
    """Get merchant billing configuration"""
    try:
        merchant_billing = billing_service.get_or_create_merchant_billing(merchant_id)
        
        return jsonify({
            'success': True,
            'data': {
                'merchant_id': merchant_billing.merchant_id,
                'european_card_percentage': merchant_billing.european_card_percentage,
                'european_card_fixed_fee': merchant_billing.european_card_fixed_fee,
                'non_european_card_percentage': merchant_billing.non_european_card_percentage,
                'non_european_card_fixed_fee': merchant_billing.non_european_card_fixed_fee,
                'chargeback_fee': merchant_billing.chargeback_fee,
                'refund_fee': merchant_billing.refund_fee,
                'billing_cycle': merchant_billing.billing_cycle.value,
                'billing_day': merchant_billing.billing_day,
                'auto_billing_enabled': merchant_billing.auto_billing_enabled,
                'billing_email': merchant_billing.billing_email,
                'billing_address': merchant_billing.billing_address,
                'payment_method': merchant_billing.payment_method
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/api/billing/merchants/<merchant_id>/config', methods=['PUT'])
@require_auth
def update_merchant_billing_config(merchant_id):
    """Update merchant billing configuration"""
    try:
        data = request.get_json()
        merchant_billing = billing_service.get_or_create_merchant_billing(merchant_id)
        
        # Update fields if provided
        if 'european_card_percentage' in data:
            merchant_billing.european_card_percentage = data['european_card_percentage']
        if 'european_card_fixed_fee' in data:
            merchant_billing.european_card_fixed_fee = data['european_card_fixed_fee']
        if 'non_european_card_percentage' in data:
            merchant_billing.non_european_card_percentage = data['non_european_card_percentage']
        if 'non_european_card_fixed_fee' in data:
            merchant_billing.non_european_card_fixed_fee = data['non_european_card_fixed_fee']
        if 'chargeback_fee' in data:
            merchant_billing.chargeback_fee = data['chargeback_fee']
        if 'refund_fee' in data:
            merchant_billing.refund_fee = data['refund_fee']
        if 'billing_email' in data:
            merchant_billing.billing_email = data['billing_email']
        if 'billing_address' in data:
            merchant_billing.billing_address = data['billing_address']
        if 'payment_method' in data:
            merchant_billing.payment_method = data['payment_method']
        if 'auto_billing_enabled' in data:
            merchant_billing.auto_billing_enabled = data['auto_billing_enabled']
        
        merchant_billing.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Billing configuration updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/api/billing/merchants/<merchant_id>/revenue', methods=['GET'])
@require_auth
def get_merchant_revenue(merchant_id):
    """Get merchant revenue summary"""
    try:
        # Get date range from query parameters
        period = request.args.get('period', 'month')  # month, week, day, custom
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if period == 'custom' and start_date and end_date:
            period_start = datetime.fromisoformat(start_date)
            period_end = datetime.fromisoformat(end_date)
        elif period == 'week':
            period_end = datetime.utcnow()
            period_start = period_end - timedelta(days=7)
        elif period == 'day':
            period_end = datetime.utcnow()
            period_start = period_end - timedelta(days=1)
        else:  # month
            period_end = datetime.utcnow()
            period_start = period_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        summary = billing_service.get_merchant_revenue_summary(merchant_id, period_start, period_end)
        
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/api/billing/revenue/total', methods=['GET'])
@require_auth
def get_total_revenue():
    """Get total revenue summary across all merchants"""
    try:
        # Get date range from query parameters
        period = request.args.get('period', 'month')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if period == 'custom' and start_date and end_date:
            period_start = datetime.fromisoformat(start_date)
            period_end = datetime.fromisoformat(end_date)
        elif period == 'week':
            period_end = datetime.utcnow()
            period_start = period_end - timedelta(days=7)
        elif period == 'day':
            period_end = datetime.utcnow()
            period_start = period_end - timedelta(days=1)
        else:  # month
            period_end = datetime.utcnow()
            period_start = period_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        summary = billing_service.get_total_revenue_summary(period_start, period_end)
        
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/api/billing/merchants/<merchant_id>/invoices', methods=['GET'])
@require_auth
def get_merchant_invoices(merchant_id):
    """Get invoices for a merchant"""
    try:
        merchant_billing = billing_service.get_or_create_merchant_billing(merchant_id)
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        status = request.args.get('status')
        
        # Build query
        query = db.session.query(Invoice).filter(Invoice.merchant_billing_id == merchant_billing.id)
        
        if status:
            query = query.filter(Invoice.status == BillingStatus(status))
        
        # Order by most recent first
        query = query.order_by(Invoice.created_at.desc())
        
        # Paginate
        invoices = query.offset((page - 1) * per_page).limit(per_page).all()
        total = query.count()
        
        invoice_data = []
        for invoice in invoices:
            invoice_data.append({
                'id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'billing_period_start': invoice.billing_period_start.isoformat(),
                'billing_period_end': invoice.billing_period_end.isoformat(),
                'subtotal': invoice.subtotal,
                'tax_amount': invoice.tax_amount,
                'total_amount': invoice.total_amount,
                'status': invoice.status.value,
                'issued_date': invoice.issued_date.isoformat(),
                'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
                'paid_date': invoice.paid_date.isoformat() if invoice.paid_date else None,
                'payment_reference': invoice.payment_reference,
                'payment_method': invoice.payment_method
            })
        
        return jsonify({
            'success': True,
            'data': {
                'invoices': invoice_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/api/billing/invoices/<int:invoice_id>', methods=['GET'])
@require_auth
def get_invoice_details(invoice_id):
    """Get detailed invoice information"""
    try:
        invoice = db.session.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            return jsonify({
                'success': False,
                'error': 'Invoice not found'
            }), 404
        
        # Get invoice items
        items = []
        for item in invoice.invoice_items:
            items.append({
                'id': item.id,
                'description': item.description,
                'fee_type': item.fee_type.value,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'total_price': item.total_price,
                'transaction_id': item.transaction_id
            })
        
        invoice_data = {
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'merchant_id': invoice.merchant_billing.merchant_id,
            'billing_period_start': invoice.billing_period_start.isoformat(),
            'billing_period_end': invoice.billing_period_end.isoformat(),
            'subtotal': invoice.subtotal,
            'tax_amount': invoice.tax_amount,
            'total_amount': invoice.total_amount,
            'status': invoice.status.value,
            'issued_date': invoice.issued_date.isoformat(),
            'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
            'paid_date': invoice.paid_date.isoformat() if invoice.paid_date else None,
            'payment_reference': invoice.payment_reference,
            'payment_method': invoice.payment_method,
            'notes': invoice.notes,
            'items': items
        }
        
        return jsonify({
            'success': True,
            'data': invoice_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/api/billing/invoices/<int:invoice_id>/pay', methods=['POST'])
@require_auth
def mark_invoice_paid(invoice_id):
    """Mark an invoice as paid"""
    try:
        data = request.get_json()
        invoice = db.session.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            return jsonify({
                'success': False,
                'error': 'Invoice not found'
            }), 404
        
        invoice.status = BillingStatus.PAID
        invoice.paid_date = datetime.utcnow()
        invoice.payment_reference = data.get('payment_reference')
        invoice.payment_method = data.get('payment_method')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Invoice marked as paid'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/api/billing/merchants/<merchant_id>/generate-invoice', methods=['POST'])
@require_auth
def generate_merchant_invoice(merchant_id):
    """Generate an invoice for a merchant"""
    try:
        data = request.get_json()
        
        # Get date range
        period_start = datetime.fromisoformat(data['period_start'])
        period_end = datetime.fromisoformat(data['period_end'])
        
        invoice = billing_service.generate_invoice(merchant_id, period_start, period_end)
        
        if not invoice:
            return jsonify({
                'success': False,
                'error': 'No fees to invoice for the specified period'
            }), 400
        
        return jsonify({
            'success': True,
            'data': {
                'invoice_id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'total_amount': invoice.total_amount
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/api/billing/fee-calculator', methods=['POST'])
@require_auth
def calculate_fee():
    """Calculate fee for a given amount and card type"""
    try:
        data = request.get_json()
        amount = data['amount']
        is_european_card = data.get('is_european_card', True)
        merchant_id = data.get('merchant_id')
        
        merchant_billing = None
        if merchant_id:
            merchant_billing = billing_service.get_or_create_merchant_billing(merchant_id)
        
        fee = billing_service.calculate_transaction_fee(amount, is_european_card, merchant_billing)
        
        return jsonify({
            'success': True,
            'data': {
                'amount': amount,
                'fee': fee,
                'net_amount': amount - fee,
                'is_european_card': is_european_card
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/api/billing/fee-transactions', methods=['GET'])
@require_auth
def get_fee_transactions():
    """Get fee transactions with filtering"""
    try:
        # Get query parameters
        merchant_id = request.args.get('merchant_id')
        fee_type = request.args.get('fee_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Build query
        query = db.session.query(FeeTransaction)
        
        if merchant_id:
            merchant_billing = billing_service.get_or_create_merchant_billing(merchant_id)
            query = query.filter(FeeTransaction.merchant_billing_id == merchant_billing.id)
        
        if fee_type:
            query = query.filter(FeeTransaction.fee_type == fee_type)
        
        if start_date:
            query = query.filter(FeeTransaction.created_at >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(FeeTransaction.created_at <= datetime.fromisoformat(end_date))
        
        # Order by most recent first
        query = query.order_by(FeeTransaction.created_at.desc())
        
        # Paginate
        fee_transactions = query.offset((page - 1) * per_page).limit(per_page).all()
        total = query.count()
        
        transaction_data = []
        for fee_tx in fee_transactions:
            transaction_data.append({
                'id': fee_tx.id,
                'merchant_id': fee_tx.merchant_billing.merchant_id,
                'payment_transaction_id': fee_tx.payment_transaction_id,
                'fee_type': fee_tx.fee_type.value,
                'fee_amount': fee_tx.fee_amount,
                'fee_percentage': fee_tx.fee_percentage,
                'fixed_fee': fee_tx.fixed_fee,
                'original_amount': fee_tx.original_amount,
                'currency': fee_tx.currency,
                'is_european_card': fee_tx.is_european_card,
                'is_invoiced': fee_tx.is_invoiced,
                'invoice_id': fee_tx.invoice_id,
                'created_at': fee_tx.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': {
                'fee_transactions': transaction_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

