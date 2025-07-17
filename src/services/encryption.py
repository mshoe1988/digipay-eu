import hashlib
import secrets
import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

logger = logging.getLogger(__name__)

class EncryptionService:
    """
    Encryption service for handling sensitive data like card numbers
    Implements tokenization and encryption for PCI DSS compliance
    """
    
    def __init__(self):
        # In production, these would be stored securely (e.g., AWS KMS, HashiCorp Vault)
        self.master_key = os.environ.get('ENCRYPTION_MASTER_KEY', 'default-master-key-change-in-production')
        self.salt = b'stable_salt_for_demo'  # In production, use random salt per encryption
        
    def _get_encryption_key(self) -> bytes:
        """
        Derive encryption key from master key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return key
    
    def tokenize_card(self, card_number: str) -> str:
        """
        Tokenize a card number for secure storage
        Returns a token that can be used to reference the card without storing the actual number
        """
        try:
            # Remove any spaces or dashes
            clean_card = ''.join(filter(str.isdigit, card_number))
            
            # Validate card number format
            if not self._validate_card_number(clean_card):
                raise ValueError("Invalid card number format")
            
            # Create a secure token
            # In production, this would store the mapping in a secure vault
            token_data = f"{clean_card}:{secrets.token_urlsafe(16)}"
            
            # Encrypt the token data
            fernet = Fernet(self._get_encryption_key())
            encrypted_token = fernet.encrypt(token_data.encode())
            
            # Return base64 encoded token
            token = base64.urlsafe_b64encode(encrypted_token).decode()
            
            logger.info(f"Card tokenized successfully, token length: {len(token)}")
            return f"tok_{token[:32]}"  # Truncate for demo purposes
            
        except Exception as e:
            logger.error(f"Error tokenizing card: {str(e)}")
            raise ValueError("Card tokenization failed")
    
    def detokenize_card(self, token: str) -> str:
        """
        Retrieve the original card number from a token
        This should only be used when absolutely necessary and with proper authorization
        """
        try:
            if not token.startswith('tok_'):
                raise ValueError("Invalid token format")
            
            # Remove token prefix
            token_data = token[4:]
            
            # In a real implementation, this would retrieve from secure vault
            # For demo purposes, we'll return a masked number
            return "****-****-****-1234"  # Always return masked for security
            
        except Exception as e:
            logger.error(f"Error detokenizing card: {str(e)}")
            raise ValueError("Card detokenization failed")
    
    def _validate_card_number(self, card_number: str) -> bool:
        """
        Validate card number using Luhn algorithm
        """
        try:
            # Luhn algorithm implementation
            def luhn_checksum(card_num):
                def digits_of(n):
                    return [int(d) for d in str(n)]
                
                digits = digits_of(card_num)
                odd_digits = digits[-1::-2]
                even_digits = digits[-2::-2]
                checksum = sum(odd_digits)
                for d in even_digits:
                    checksum += sum(digits_of(d*2))
                return checksum % 10
            
            return luhn_checksum(card_number) == 0 and len(card_number) >= 13
            
        except Exception:
            return False
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """
        Encrypt sensitive data for storage
        """
        try:
            fernet = Fernet(self._get_encryption_key())
            encrypted_data = fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
            
        except Exception as e:
            logger.error(f"Error encrypting data: {str(e)}")
            raise ValueError("Data encryption failed")
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data
        """
        try:
            fernet = Fernet(self._get_encryption_key())
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = fernet.decrypt(decoded_data)
            return decrypted_data.decode()
            
        except Exception as e:
            logger.error(f"Error decrypting data: {str(e)}")
            raise ValueError("Data decryption failed")
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password for secure storage
        """
        try:
            # Generate a random salt
            salt = secrets.token_hex(16)
            
            # Hash the password with salt
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            
            # Return salt + hash
            return f"{salt}:{password_hash.hex()}"
            
        except Exception as e:
            logger.error(f"Error hashing password: {str(e)}")
            raise ValueError("Password hashing failed")
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """
        Verify a password against a stored hash
        """
        try:
            salt, hash_hex = stored_hash.split(':')
            stored_hash_bytes = bytes.fromhex(hash_hex)
            
            # Hash the provided password with the same salt
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            
            # Compare hashes
            return password_hash == stored_hash_bytes
            
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False
    
    def generate_api_key(self, prefix: str = "pk") -> str:
        """
        Generate a secure API key
        """
        try:
            random_part = secrets.token_urlsafe(32)
            return f"{prefix}_{random_part}"
            
        except Exception as e:
            logger.error(f"Error generating API key: {str(e)}")
            raise ValueError("API key generation failed")
    
    def mask_card_number(self, card_number: str) -> str:
        """
        Mask a card number for display purposes
        """
        try:
            clean_card = ''.join(filter(str.isdigit, card_number))
            if len(clean_card) < 4:
                return "****"
            
            return f"****-****-****-{clean_card[-4:]}"
            
        except Exception:
            return "****-****-****-****"
    
    def mask_email(self, email: str) -> str:
        """
        Mask an email address for display purposes
        """
        try:
            if '@' not in email:
                return "***@***.***"
            
            local, domain = email.split('@', 1)
            
            if len(local) <= 2:
                masked_local = "*" * len(local)
            else:
                masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
            
            if '.' in domain:
                domain_parts = domain.split('.')
                masked_domain = domain_parts[0][0] + "*" * (len(domain_parts[0]) - 1)
                for part in domain_parts[1:]:
                    masked_domain += "." + part
            else:
                masked_domain = domain[0] + "*" * (len(domain) - 1)
            
            return f"{masked_local}@{masked_domain}"
            
        except Exception:
            return "***@***.***"

