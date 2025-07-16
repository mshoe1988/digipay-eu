from flask import Blueprint, jsonify, request
from src.database import db
from src.models.user import Merchant
import uuid
import hashlib
import secrets
import logging

merchant_bp = Blueprint('merchant', __name__)
logger = logging.getLogger(__name__)

@merchant_bp.route('/merchants', methods=['POST'])
def create_merchant():
    """
    Create a new merchant account
    """
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['business_name', 'contact_email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if merchant already exists
        existing_merchant = Merchant.query.filter_by(contact_email=data['contact_email']).first()
        if existing_merchant:
            return jsonify({'error': 'Merchant with this email already exists'}), 409
        
        # Generate API credentials
        api_key = f"pk_{'test' if data.get('test_mode', True) else 'live'}_{secrets.token_urlsafe(32)}"
        api_secret = f"sk_{'test' if data.get('test_mode', True) else 'live'}_{secrets.token_urlsafe(32)}"
        
        # Create merchant
        merchant = Merchant(
            merchant_id=f"merchant_{uuid.uuid4().hex[:12]}",
            business_name=data['business_name'],
            contact_email=data['contact_email'],
            api_key=api_key,
            api_secret=hashlib.sha256(api_secret.encode()).hexdigest(),  # Store hashed secret
            business_type=data.get('business_type'),
            country=data.get('country', 'DE'),  # Default to Germany for EU compliance
            currency=data.get('currency', 'EUR')
        )
        
        db.session.add(merchant)
        db.session.commit()
        
        # Return merchant data with unhashed API secret (only time it's shown)
        merchant_data = merchant.to_dict()
        merchant_data['api_secret'] = api_secret  # Show unhashed secret only once
        
        return jsonify(merchant_data), 201
        
    except Exception as e:
        logger.error(f"Error creating merchant: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@merchant_bp.route('/merchants/<merchant_id>', methods=['GET'])
def get_merchant(merchant_id):
    """
    Get merchant details by merchant ID
    """
    try:
        merchant = Merchant.query.filter_by(merchant_id=merchant_id).first()
        if not merchant:
            return jsonify({'error': 'Merchant not found'}), 404
        
        return jsonify(merchant.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error retrieving merchant: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@merchant_bp.route('/merchants', methods=['GET'])
def get_merchants():
    """
    Get all merchants with optional filtering
    """
    try:
        is_active = request.args.get('is_active')
        is_verified = request.args.get('is_verified')
        country = request.args.get('country')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        query = Merchant.query
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active.lower() == 'true')
        
        if is_verified is not None:
            query = query.filter_by(is_verified=is_verified.lower() == 'true')
        
        if country:
            query = query.filter_by(country=country.upper())
        
        merchants = query.order_by(Merchant.created_at.desc()).offset(offset).limit(limit).all()
        
        return jsonify([merchant.to_dict() for merchant in merchants]), 200
        
    except Exception as e:
        logger.error(f"Error retrieving merchants: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@merchant_bp.route('/merchants/<merchant_id>', methods=['PUT'])
def update_merchant(merchant_id):
    """
    Update merchant information
    """
    try:
        merchant = Merchant.query.filter_by(merchant_id=merchant_id).first()
        if not merchant:
            return jsonify({'error': 'Merchant not found'}), 404
        
        data = request.json
        
        # Update allowed fields
        updatable_fields = ['business_name', 'contact_email', 'business_type', 'country', 'currency']
        for field in updatable_fields:
            if field in data:
                setattr(merchant, field, data[field])
        
        db.session.commit()
        
        return jsonify(merchant.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error updating merchant: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@merchant_bp.route('/merchants/<merchant_id>/verify', methods=['POST'])
def verify_merchant(merchant_id):
    """
    Verify a merchant account (admin function)
    """
    try:
        merchant = Merchant.query.filter_by(merchant_id=merchant_id).first()
        if not merchant:
            return jsonify({'error': 'Merchant not found'}), 404
        
        data = request.json
        
        # Update verification status
        merchant.is_verified = data.get('is_verified', True)
        merchant.pci_compliant = data.get('pci_compliant', False)
        merchant.kyc_verified = data.get('kyc_verified', False)
        
        db.session.commit()
        
        return jsonify(merchant.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error verifying merchant: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@merchant_bp.route('/merchants/<merchant_id>/activate', methods=['POST'])
def activate_merchant(merchant_id):
    """
    Activate or deactivate a merchant account
    """
    try:
        merchant = Merchant.query.filter_by(merchant_id=merchant_id).first()
        if not merchant:
            return jsonify({'error': 'Merchant not found'}), 404
        
        data = request.json
        merchant.is_active = data.get('is_active', True)
        
        db.session.commit()
        
        return jsonify(merchant.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error updating merchant status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@merchant_bp.route('/merchants/<merchant_id>/regenerate-keys', methods=['POST'])
def regenerate_api_keys(merchant_id):
    """
    Regenerate API keys for a merchant
    """
    try:
        merchant = Merchant.query.filter_by(merchant_id=merchant_id).first()
        if not merchant:
            return jsonify({'error': 'Merchant not found'}), 404
        
        # Generate new API credentials
        api_key = f"pk_live_{secrets.token_urlsafe(32)}"
        api_secret = f"sk_live_{secrets.token_urlsafe(32)}"
        
        merchant.api_key = api_key
        merchant.api_secret = hashlib.sha256(api_secret.encode()).hexdigest()
        
        db.session.commit()
        
        # Return new credentials (api_secret shown only once)
        return jsonify({
            'merchant_id': merchant.merchant_id,
            'api_key': api_key,
            'api_secret': api_secret,
            'message': 'API keys regenerated successfully. Please store the secret key securely.'
        }), 200
        
    except Exception as e:
        logger.error(f"Error regenerating API keys: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

