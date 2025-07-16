from src.database import db
from datetime import datetime, timedelta
import hashlib
import secrets
from werkzeug.security import generate_password_hash, check_password_hash

class MerchantAuth(db.Model):
    """Authentication model for merchant accounts"""
    __tablename__ = 'merchant_auth'
    
    id = db.Column(db.Integer, primary_key=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255))
    
    # Security
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    # API access
    api_key = db.Column(db.String(255), unique=True)
    api_secret = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    merchant = db.relationship('Merchant', backref='auth', lazy=True)
    
    def __init__(self, email, password, merchant_id):
        self.email = email
        self.set_password(password)
        self.merchant_id = merchant_id
        self.generate_api_credentials()
        self.verification_token = secrets.token_urlsafe(32)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def generate_api_credentials(self):
        """Generate API key and secret for merchant"""
        self.api_key = f"pk_{'live' if self.is_verified else 'test'}_{secrets.token_urlsafe(24)}"
        self.api_secret = f"sk_{'live' if self.is_verified else 'test'}_{secrets.token_urlsafe(32)}"
    
    def is_account_locked(self):
        """Check if account is locked due to failed login attempts"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def increment_failed_login(self):
        """Increment failed login attempts and lock if necessary"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            # Lock account for 30 minutes
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
    
    def reset_failed_login(self):
        """Reset failed login attempts on successful login"""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'merchant_id': self.merchant_id,
            'email': self.email,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'api_key': self.api_key,
            'created_at': self.created_at.isoformat()
        }

class LoginSession(db.Model):
    """Track active login sessions"""
    __tablename__ = 'login_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    merchant_auth_id = db.Column(db.Integer, db.ForeignKey('merchant_auth.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    # Session management
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship
    merchant_auth = db.relationship('MerchantAuth', backref='sessions', lazy=True)
    
    def __init__(self, merchant_auth_id, ip_address=None, user_agent=None):
        self.merchant_auth_id = merchant_auth_id
        self.session_token = secrets.token_urlsafe(32)
        self.ip_address = ip_address
        self.user_agent = user_agent
        # Session expires in 24 hours
        self.expires_at = datetime.utcnow() + timedelta(hours=24)
    
    def is_expired(self):
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def extend_session(self):
        """Extend session by 24 hours"""
        self.expires_at = datetime.utcnow() + timedelta(hours=24)
        db.session.commit()
    
    def deactivate(self):
        """Deactivate session (logout)"""
        self.is_active = False
        db.session.commit()

