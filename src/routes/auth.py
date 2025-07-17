from flask import Blueprint, request, jsonify, session
from src.database import db
from src.models.user import Merchant
from src.models.auth import MerchantAuth, LoginSession
from src.models.payment import Payment
from datetime import datetime, timedelta
import secrets
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

@auth_bp.route('/register', methods=['POST'])
def register_merchant():
    """Register a new merchant account"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['business_name', 'contact_email', 'password', 'contact_phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email format
        if not validate_email(data['contact_email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if email already exists
        existing_auth = MerchantAuth.query.filter_by(email=data['contact_email']).first()
        if existing_auth:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create merchant record
        merchant = Merchant(
            merchant_id=f"merchant_{secrets.token_hex(8)}",
            business_name=data['business_name'],
            contact_email=data['contact_email'],
            contact_phone=data['contact_phone'],
            business_address=data.get('business_address', ''),
            business_type=data.get('business_type', ''),
            website_url=data.get('website_url', ''),
            status='pending'
        )
        
        db.session.add(merchant)
        db.session.flush()  # Get merchant ID
        
        # Create authentication record
        merchant_auth = MerchantAuth(
            email=data['contact_email'],
            password=data['password'],
            merchant_id=merchant.id
        )
        
        db.session.add(merchant_auth)
        db.session.commit()
        
        return jsonify({
            'message': 'Merchant account created successfully',
            'merchant_id': merchant.merchant_id,
            'email': merchant_auth.email,
            'api_key': merchant_auth.api_key,
            'verification_required': True
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login_merchant():
    """Login merchant and create session"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find merchant auth record
        merchant_auth = MerchantAuth.query.filter_by(email=data['email']).first()
        
        if not merchant_auth:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if account is locked
        if merchant_auth.is_account_locked():
            return jsonify({'error': 'Account is temporarily locked due to failed login attempts'}), 423
        
        # Check password
        if not merchant_auth.check_password(data['password']):
            merchant_auth.increment_failed_login()
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if account is active
        if not merchant_auth.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Reset failed login attempts
        merchant_auth.reset_failed_login()
        
        # Create login session
        session_record = LoginSession(
            merchant_auth_id=merchant_auth.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        db.session.add(session_record)
        db.session.commit()
        
        # Set session data
        session['merchant_id'] = merchant_auth.merchant_id
        session['session_token'] = session_record.session_token
        session['is_authenticated'] = True
        
        return jsonify({
            'message': 'Login successful',
            'merchant_id': merchant_auth.merchant.merchant_id,
            'business_name': merchant_auth.merchant.business_name,
            'session_token': session_record.session_token,
            'api_key': merchant_auth.api_key
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout_merchant():
    """Logout merchant and deactivate session"""
    try:
        session_token = session.get('session_token')
        
        if session_token:
            # Deactivate session
            session_record = LoginSession.query.filter_by(session_token=session_token).first()
            if session_record:
                session_record.deactivate()
        
        # Clear session
        session.clear()
        
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Logout failed', 'details': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
def get_merchant_profile():
    """Get current merchant profile"""
    try:
        if not session.get('is_authenticated'):
            return jsonify({'error': 'Not authenticated'}), 401
        
        session_token = session.get('session_token')
        session_record = LoginSession.query.filter_by(
            session_token=session_token,
            is_active=True
        ).first()
        
        if not session_record or session_record.is_expired():
            return jsonify({'error': 'Session expired'}), 401
        
        merchant_auth = session_record.merchant_auth
        merchant = merchant_auth.merchant
        
        return jsonify({
            'merchant_id': merchant.merchant_id,
            'business_name': merchant.business_name,
            'contact_email': merchant.contact_email,
            'contact_phone': merchant.contact_phone,
            'business_address': merchant.business_address,
            'business_type': merchant.business_type,
            'website_url': merchant.website_url,
            'status': merchant.status,
            'is_verified': merchant.is_verified,
            'api_key': merchant_auth.api_key,
            'created_at': merchant.created_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get profile', 'details': str(e)}), 500

@auth_bp.route('/transactions', methods=['GET'])
def get_merchant_transactions():
    """Get transactions for the authenticated merchant"""
    try:
        if not session.get('is_authenticated'):
            return jsonify({'error': 'Not authenticated'}), 401
        
        session_token = session.get('session_token')
        session_record = LoginSession.query.filter_by(
            session_token=session_token,
            is_active=True
        ).first()
        
        if not session_record or session_record.is_expired():
            return jsonify({'error': 'Session expired'}), 401
        
        merchant = session_record.merchant_auth.merchant
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = Payment.query.filter_by(merchant_id=merchant.merchant_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if start_date:
            start_date = datetime.fromisoformat(start_date)
            query = query.filter(Payment.created_at >= start_date)
        
        if end_date:
            end_date = datetime.fromisoformat(end_date)
            query = query.filter(Payment.created_at <= end_date)
        
        # Order by most recent first
        query = query.order_by(Payment.created_at.desc())
        
        # Paginate
        transactions = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'transactions': [transaction.to_dict() for transaction in transactions.items],
            'total': transactions.total,
            'pages': transactions.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get transactions', 'details': str(e)}), 500

@auth_bp.route('/dashboard-stats', methods=['GET'])
def get_merchant_dashboard_stats():
    """Get dashboard statistics for the authenticated merchant"""
    try:
        if not session.get('is_authenticated'):
            return jsonify({'error': 'Not authenticated'}), 401
        
        session_token = session.get('session_token')
        session_record = LoginSession.query.filter_by(
            session_token=session_token,
            is_active=True
        ).first()
        
        if not session_record or session_record.is_expired():
            return jsonify({'error': 'Session expired'}), 401
        
        merchant = session_record.merchant_auth.merchant
        
        # Calculate date ranges
        today = datetime.utcnow().date()
        last_30_days = today - timedelta(days=30)
        last_7_days = today - timedelta(days=7)
        
        # Get transactions for this merchant
        all_transactions = Payment.query.filter_by(merchant_id=merchant.merchant_id)
        recent_transactions = all_transactions.filter(Payment.created_at >= last_30_days)
        
        # Calculate statistics
        total_transactions = all_transactions.count()
        total_revenue = sum([t.amount for t in all_transactions if t.status == 'completed'])
        
        recent_count = recent_transactions.count()
        recent_revenue = sum([t.amount for t in recent_transactions if t.status == 'completed'])
        
        success_rate = 0
        if total_transactions > 0:
            successful = all_transactions.filter_by(status='completed').count()
            success_rate = (successful / total_transactions) * 100
        
        return jsonify({
            'total_transactions': total_transactions,
            'total_revenue': total_revenue,
            'recent_transactions_30d': recent_count,
            'recent_revenue_30d': recent_revenue,
            'success_rate': round(success_rate, 1),
            'merchant_status': merchant.status,
            'is_verified': merchant.is_verified
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get dashboard stats', 'details': str(e)}), 500

