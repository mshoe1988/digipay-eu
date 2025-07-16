import os
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """Initialize database with Flask app"""
    
    # Configure database URL with fallback to SQLite
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Handle PostgreSQL URL format for newer SQLAlchemy versions
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Fallback to SQLite for development/testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///digipay_eu.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        try:
            # Import all models to ensure they are registered
            from src.models.user import User, Merchant
            from src.models.payment import Payment, TransactionLog
            from src.models.billing import MerchantBilling, Invoice, InvoiceItem, FeeTransaction, RevenueReport, setup_billing_relationships
            
            # Setup relationships
            setup_billing_relationships()
            db.create_all()
            
            # Create default admin user if it doesn't exist
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@digipay.eu'
                )
                db.session.add(admin_user)
                db.session.commit()
                
        except Exception as e:
            print(f"Database initialization error: {e}")
            # Continue with basic setup even if there are issues
            db.create_all()

