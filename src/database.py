import os
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """Initialize database with Flask app - SQLite optimized"""
    
    # Use SQLite for maximum compatibility and simplicity
    # SQLite is perfect for payment processing platforms and scales well
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///digipay_eu.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    print("Using SQLite database - optimized for Digipay EU")
    
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
                print("Created default admin user")
                
            print("Database initialized successfully")
                
        except Exception as e:
            print(f"Database initialization error: {e}")
            print("Attempting basic database setup...")
            try:
                # Try basic setup without relationships
                db.create_all()
                print("Basic database setup completed")
            except Exception as e2:
                print(f"Basic database setup failed: {e2}")
                print("Application will continue with limited functionality")

