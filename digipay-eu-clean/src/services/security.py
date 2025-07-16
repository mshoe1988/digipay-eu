import hashlib
import secrets
import jwt
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from functools import wraps
from flask import request, jsonify, current_app
import re

logger = logging.getLogger(__name__)

class SecurityService:
    """
    Security service for authentication, authorization, and security monitoring
    """
    
    def __init__(self):
        self.jwt_secret = secrets.token_urlsafe(32)
        self.token_expiry_hours = 24
        self.max_login_attempts = 5
        self.lockout_duration_minutes = 30
        self.password_min_length = 8
        self.failed_attempts = {}  # In production, use Redis or database
        
    def hash_password(self, password: str, salt: str = None) -> tuple:
        """
        Hash password with salt using PBKDF2
        """
        try:
            if salt is None:
                salt = secrets.token_hex(32)
            
            # Use PBKDF2 with SHA-256
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000  # 100,000 iterations
            )
            
            return password_hash.hex(), salt
            
        except Exception as e:
            logger.error(f"Error hashing password: {str(e)}")
            raise
    
    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """
        Verify password against stored hash
        """
        try:
            password_hash, _ = self.hash_password(password, salt)
            return secrets.compare_digest(password_hash, stored_hash)
            
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """
        Validate password strength according to security requirements
        """
        result = {
            'valid': True,
            'issues': [],
            'strength_score': 0
        }
        
        # Check minimum length
        if len(password) < self.password_min_length:
            result['valid'] = False
            result['issues'].append(f'Password must be at least {self.password_min_length} characters long')
        else:
            result['strength_score'] += 1
        
        # Check for uppercase letters
        if not re.search(r'[A-Z]', password):
            result['valid'] = False
            result['issues'].append('Password must contain at least one uppercase letter')
        else:
            result['strength_score'] += 1
        
        # Check for lowercase letters
        if not re.search(r'[a-z]', password):
            result['valid'] = False
            result['issues'].append('Password must contain at least one lowercase letter')
        else:
            result['strength_score'] += 1
        
        # Check for numbers
        if not re.search(r'\d', password):
            result['valid'] = False
            result['issues'].append('Password must contain at least one number')
        else:
            result['strength_score'] += 1
        
        # Check for special characters
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result['valid'] = False
            result['issues'].append('Password must contain at least one special character')
        else:
            result['strength_score'] += 1
        
        # Check for common passwords (simplified)
        common_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if password.lower() in common_passwords:
            result['valid'] = False
            result['issues'].append('Password is too common')
            result['strength_score'] = 0
        
        return result
    
    def generate_jwt_token(self, user_id: str, role: str = 'user', additional_claims: Dict = None) -> str:
        """
        Generate JWT token for authentication
        """
        try:
            payload = {
                'user_id': user_id,
                'role': role,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
            }
            
            if additional_claims:
                payload.update(additional_claims)
            
            token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
            
            logger.info(f"JWT token generated for user {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Error generating JWT token: {str(e)}")
            raise
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # Check if token is expired
            if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
                return {'valid': False, 'error': 'Token expired'}
            
            return {'valid': True, 'payload': payload}
            
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'Invalid token'}
        except Exception as e:
            logger.error(f"Error verifying JWT token: {str(e)}")
            return {'valid': False, 'error': 'Token verification failed'}
    
    def check_rate_limit(self, identifier: str, max_requests: int = 100, window_minutes: int = 60) -> Dict[str, Any]:
        """
        Check rate limiting for API requests
        """
        try:
            current_time = datetime.utcnow()
            window_start = current_time - timedelta(minutes=window_minutes)
            
            # In production, use Redis for distributed rate limiting
            # For demo, use in-memory storage
            if identifier not in self.failed_attempts:
                self.failed_attempts[identifier] = []
            
            # Remove old attempts outside the window
            self.failed_attempts[identifier] = [
                attempt for attempt in self.failed_attempts[identifier]
                if attempt > window_start
            ]
            
            current_requests = len(self.failed_attempts[identifier])
            
            if current_requests >= max_requests:
                return {
                    'allowed': False,
                    'current_requests': current_requests,
                    'max_requests': max_requests,
                    'reset_time': (window_start + timedelta(minutes=window_minutes)).isoformat()
                }
            
            # Record this request
            self.failed_attempts[identifier].append(current_time)
            
            return {
                'allowed': True,
                'current_requests': current_requests + 1,
                'max_requests': max_requests,
                'remaining_requests': max_requests - current_requests - 1
            }
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            return {'allowed': True, 'error': str(e)}
    
    def validate_api_key(self, api_key: str, merchant_id: str = None) -> Dict[str, Any]:
        """
        Validate API key for merchant authentication
        """
        try:
            # In production, this would check against a database
            # For demo, use a simple validation
            if not api_key or len(api_key) < 32:
                return {'valid': False, 'error': 'Invalid API key format'}
            
            if not api_key.startswith('pk_') and not api_key.startswith('sk_'):
                return {'valid': False, 'error': 'Invalid API key prefix'}
            
            # Simulate database lookup
            api_key_data = {
                'merchant_id': merchant_id or 'merchant_demo_001',
                'permissions': ['read', 'write'],
                'created_at': datetime.utcnow().isoformat(),
                'last_used': datetime.utcnow().isoformat()
            }
            
            return {'valid': True, 'data': api_key_data}
            
        except Exception as e:
            logger.error(f"Error validating API key: {str(e)}")
            return {'valid': False, 'error': 'API key validation failed'}
    
    def sanitize_input(self, input_data: Any) -> Any:
        """
        Sanitize input data to prevent injection attacks
        """
        try:
            if isinstance(input_data, str):
                # Remove potentially dangerous characters
                sanitized = re.sub(r'[<>"\';\\]', '', input_data)
                # Limit length
                sanitized = sanitized[:1000]
                return sanitized.strip()
            
            elif isinstance(input_data, dict):
                return {key: self.sanitize_input(value) for key, value in input_data.items()}
            
            elif isinstance(input_data, list):
                return [self.sanitize_input(item) for item in input_data]
            
            else:
                return input_data
                
        except Exception as e:
            logger.error(f"Error sanitizing input: {str(e)}")
            return input_data
    
    def validate_ip_address(self, ip_address: str, whitelist: List[str] = None) -> Dict[str, Any]:
        """
        Validate IP address against whitelist/blacklist
        """
        try:
            # Basic IP format validation
            ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
            
            if not re.match(ip_pattern, ip_address):
                return {'valid': False, 'error': 'Invalid IP address format'}
            
            # Check against whitelist if provided
            if whitelist and ip_address not in whitelist:
                return {'valid': False, 'error': 'IP address not in whitelist'}
            
            # Check against known malicious IPs (simplified)
            blacklist = ['192.168.1.100', '10.0.0.100']  # Example blacklist
            if ip_address in blacklist:
                return {'valid': False, 'error': 'IP address is blacklisted'}
            
            return {'valid': True, 'ip_address': ip_address}
            
        except Exception as e:
            logger.error(f"Error validating IP address: {str(e)}")
            return {'valid': False, 'error': 'IP validation failed'}
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], severity: str = 'INFO'):
        """
        Log security events for monitoring and analysis
        """
        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': event_type,
                'severity': severity,
                'details': details,
                'source_ip': request.remote_addr if request else 'unknown'
            }
            
            # In production, send to SIEM or security monitoring system
            if severity in ['HIGH', 'CRITICAL']:
                logger.warning(f"Security event: {log_entry}")
            else:
                logger.info(f"Security event: {log_entry}")
                
        except Exception as e:
            logger.error(f"Error logging security event: {str(e)}")
    
    def detect_suspicious_activity(self, user_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect suspicious activity patterns
        """
        try:
            suspicion_score = 0
            flags = []
            
            # Check for unusual transaction amounts
            if 'amount' in activity_data:
                amount = float(activity_data['amount'])
                if amount > 10000:  # Large transaction
                    suspicion_score += 2
                    flags.append('large_transaction')
            
            # Check for rapid successive transactions
            if 'transaction_count' in activity_data:
                if activity_data['transaction_count'] > 10:
                    suspicion_score += 3
                    flags.append('rapid_transactions')
            
            # Check for unusual location
            if 'location' in activity_data:
                # Simplified location check
                if activity_data['location'] not in ['DE', 'FR', 'ES', 'IT', 'NL']:
                    suspicion_score += 1
                    flags.append('unusual_location')
            
            # Check for failed authentication attempts
            if 'failed_attempts' in activity_data:
                if activity_data['failed_attempts'] > 3:
                    suspicion_score += 4
                    flags.append('multiple_failed_attempts')
            
            result = {
                'suspicious': suspicion_score >= 3,
                'suspicion_score': suspicion_score,
                'flags': flags,
                'recommended_action': 'monitor' if suspicion_score < 5 else 'block'
            }
            
            if result['suspicious']:
                self.log_security_event(
                    'suspicious_activity_detected',
                    {'user_id': user_id, 'result': result},
                    'HIGH'
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting suspicious activity: {str(e)}")
            return {
                'suspicious': False,
                'suspicion_score': 0,
                'flags': [],
                'error': str(e)
            }
    
    def generate_api_key(self, merchant_id: str, key_type: str = 'public') -> str:
        """
        Generate API key for merchant
        """
        try:
            prefix = 'pk_' if key_type == 'public' else 'sk_'
            random_part = secrets.token_urlsafe(32)
            api_key = f"{prefix}{random_part}"
            
            # In production, store in database with merchant_id
            self.log_security_event(
                'api_key_generated',
                {'merchant_id': merchant_id, 'key_type': key_type},
                'INFO'
            )
            
            return api_key
            
        except Exception as e:
            logger.error(f"Error generating API key: {str(e)}")
            raise
    
    def encrypt_sensitive_data(self, data: str, key: str = None) -> Dict[str, str]:
        """
        Encrypt sensitive data using AES encryption
        """
        try:
            from cryptography.fernet import Fernet
            
            if key is None:
                key = Fernet.generate_key()
            
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(data.encode())
            
            return {
                'encrypted_data': encrypted_data.decode(),
                'key': key.decode() if isinstance(key, bytes) else key
            }
            
        except Exception as e:
            logger.error(f"Error encrypting data: {str(e)}")
            raise
    
    def decrypt_sensitive_data(self, encrypted_data: str, key: str) -> str:
        """
        Decrypt sensitive data using AES encryption
        """
        try:
            from cryptography.fernet import Fernet
            
            fernet = Fernet(key.encode() if isinstance(key, str) else key)
            decrypted_data = fernet.decrypt(encrypted_data.encode())
            
            return decrypted_data.decode()
            
        except Exception as e:
            logger.error(f"Error decrypting data: {str(e)}")
            raise

# Decorator for requiring authentication
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        security_service = SecurityService()
        
        # Check for API key in headers
        api_key = request.headers.get('X-API-Key')
        if api_key:
            validation_result = security_service.validate_api_key(api_key)
            if not validation_result['valid']:
                return jsonify({'error': 'Invalid API key'}), 401
            
            # Add merchant info to request context
            request.merchant_data = validation_result['data']
            return f(*args, **kwargs)
        
        # Check for JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        token = auth_header.split(' ')[1]
        verification_result = security_service.verify_jwt_token(token)
        
        if not verification_result['valid']:
            return jsonify({'error': verification_result['error']}), 401
        
        # Add user info to request context
        request.user_data = verification_result['payload']
        return f(*args, **kwargs)
    
    return decorated_function

# Decorator for rate limiting
def rate_limit(max_requests: int = 100, window_minutes: int = 60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            security_service = SecurityService()
            
            # Use IP address as identifier
            identifier = request.remote_addr
            
            rate_limit_result = security_service.check_rate_limit(
                identifier, max_requests, window_minutes
            )
            
            if not rate_limit_result['allowed']:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'reset_time': rate_limit_result.get('reset_time')
                }), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

