from flask import request, session
from flask_babel import Babel, get_locale
import os

def get_locale():
    """Determine the best language to use for the user."""
    # Check if language is set in session
    if 'language' in session:
        return session['language']
    
    # Check if language is provided in URL parameter
    if request.args.get('lang'):
        session['language'] = request.args.get('lang')
        return session['language']
    
    # Use browser's preferred language
    return request.accept_languages.best_match(['en', 'es', 'fr', 'de', 'it', 'pt']) or 'en'

def init_babel(app):
    """Initialize Babel with the Flask app."""
    # Configure supported languages
    app.config['LANGUAGES'] = {
        'en': 'English',
        'es': 'Español',
        'fr': 'Français', 
        'de': 'Deutsch',
        'it': 'Italiano',
        'pt': 'Português'
    }
    
    # Initialize Babel
    babel = Babel(app, locale_selector=get_locale)
    
    return babel

