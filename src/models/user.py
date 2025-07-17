from src.database import db
from datetime import datetime
from sqlalchemy.orm import relationship

class User(db.Model):
    """User model for admin accounts"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

class Merchant(db.Model):
    """Merchant model for business accounts"""
    __tablename__ = 'merchants'
    
    id = db.Column(db.Integer, primary_key=True)
    merchant_id = db.Column(db.String(100), unique=True, nullable=False)
    business_name = db.Column(db.String(255), nullable=False)
    contact_email = db.Column(db.String(255), nullable=False)
    contact_phone = db.Column(db.String(50))
    business_address = db.Column(db.Text)
    business_type = db.Column(db.String(100))
    website_url = db.Column(db.String(255))
    
    # Status and verification
    status = db.Column(db.String(50), default='pending')  # pending, active, suspended
    is_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    billing = relationship("MerchantBilling", back_populates="merchant", uselist=False)
    payments = relationship("Payment", back_populates="merchant")
    auth_records = relationship("MerchantAuth", back_populates="merchant")
    
    def to_dict(self):
        return {
            'id': self.id,
            'merchant_id': self.merchant_id,
            'business_name': self.business_name,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'business_address': self.business_address,
            'business_type': self.business_type,
            'website_url': self.website_url,
            'status': self.status,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

