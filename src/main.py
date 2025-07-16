"""
Digipay EU - Payment Gateway Platform
A secure, scalable payment processing platform for European businesses
"""

import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, session, jsonify
from flask_cors import CORS
from src.database import init_db
from src.i18n import init_babel
from src.routes.user import user_bp
from src.routes.payment import payment_bp
from src.routes.merchant import merchant_bp
from src.routes.billing import billing_bp
from src.routes.auth import auth_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'digipay-eu-secret-key-change-in-production')

# Enable CORS for all routes
CORS(app)

# Initialize internationalization
babel = init_babel(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(payment_bp, url_prefix='/api')
app.register_blueprint(merchant_bp, url_prefix='/api')
app.register_blueprint(billing_bp)
app.register_blueprint(auth_bp, url_prefix='/api')

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///" + os.path.join(os.path.dirname(__file__), "database", "app.db"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create database directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(__file__), 'database'), exist_ok=True)

# Initialize database
init_db(app)

# Language switching endpoint
@app.route('/api/set-language', methods=['POST'])
def set_language():
    """Set the user's preferred language."""
    data = request.get_json()
    language = data.get('language', 'en')
    
    # Validate language
    if language in app.config['LANGUAGES']:
        session['language'] = language
        return jsonify({'status': 'success', 'language': language})
    else:
        return jsonify({'status': 'error', 'message': 'Unsupported language'}), 400

# Get available languages endpoint
@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get list of available languages."""
    return jsonify(app.config['LANGUAGES'])

# Get current language endpoint
@app.route('/api/current-language', methods=['GET'])
def get_current_language():
    """Get the current language setting."""
    from flask_babel import get_locale
    current_locale = str(get_locale())
    return jsonify({'language': current_locale})

# Main routes
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/merchant-auth.html')
def merchant_auth():
    return send_from_directory(app.static_folder, 'merchant-auth.html')

@app.route('/merchant-dashboard.html')
def merchant_dashboard():
    return send_from_directory(app.static_folder, 'merchant-dashboard.html')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

