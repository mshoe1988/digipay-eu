import logging
import re
from typing import Dict, Any
from src.models.payment import Payment
import random
import math

logger = logging.getLogger(__name__)

class FraudDetectionService:
    """
    Fraud detection service that analyzes transactions for potential fraud
    """
    
    def __init__(self):
        self.high_risk_countries = ['XX', 'YY']  # Example high-risk country codes
        self.suspicious_email_patterns = [
            r'.*temp.*@.*',
            r'.*test.*@.*',
            r'.*fake.*@.*'
        ]
        
    def analyze_transaction(self, payment: Payment, transaction_data: Dict[str, Any]) -> float:
        """
        Analyze a transaction and return a fraud score (0.0 to 1.0)
        Higher scores indicate higher fraud risk
        """
        try:
            fraud_score = 0.0
            
            # Amount-based risk
            fraud_score += self._analyze_amount_risk(payment.amount)
            
            # Email-based risk
            if payment.customer_email:
                fraud_score += self._analyze_email_risk(payment.customer_email)
            
            # IP-based risk
            if payment.ip_address:
                fraud_score += self._analyze_ip_risk(payment.ip_address)
            
            # Velocity checks
            fraud_score += self._analyze_velocity_risk(payment)
            
            # Card-based risk
            if payment.card_token:
                fraud_score += self._analyze_card_risk(payment.card_token)
            
            # Time-based risk
            fraud_score += self._analyze_time_risk()
            
            # Ensure score is between 0 and 1
            fraud_score = min(max(fraud_score, 0.0), 1.0)
            
            logger.info(f"Fraud score for transaction {payment.transaction_id}: {fraud_score}")
            
            return fraud_score
            
        except Exception as e:
            logger.error(f"Error analyzing fraud for transaction {payment.transaction_id}: {str(e)}")
            return 0.5  # Default medium risk on error
    
    def _analyze_amount_risk(self, amount: float) -> float:
        """
        Analyze risk based on transaction amount
        """
        try:
            amount_float = float(amount)
            
            # Very high amounts are riskier
            if amount_float > 100000:  # Over 1000 EUR
                return 0.4
            elif amount_float > 50000:  # Over 500 EUR
                return 0.2
            elif amount_float > 20000:  # Over 200 EUR
                return 0.1
            else:
                return 0.0
                
        except Exception:
            return 0.1
    
    def _analyze_email_risk(self, email: str) -> float:
        """
        Analyze risk based on customer email
        """
        try:
            risk_score = 0.0
            
            # Check for suspicious email patterns
            for pattern in self.suspicious_email_patterns:
                if re.match(pattern, email.lower()):
                    risk_score += 0.3
                    break
            
            # Check for disposable email domains
            disposable_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
            email_domain = email.split('@')[-1].lower()
            if email_domain in disposable_domains:
                risk_score += 0.4
            
            # Check for recently created domains (simplified check)
            if email_domain.endswith('.tk') or email_domain.endswith('.ml'):
                risk_score += 0.2
            
            return min(risk_score, 0.5)
            
        except Exception:
            return 0.1
    
    def _analyze_ip_risk(self, ip_address: str) -> float:
        """
        Analyze risk based on IP address
        """
        try:
            # Simplified IP risk analysis
            # In production, this would use IP geolocation and reputation services
            
            risk_score = 0.0
            
            # Check for private/local IPs (might indicate proxy/VPN)
            if ip_address.startswith('10.') or ip_address.startswith('192.168.') or ip_address.startswith('127.'):
                risk_score += 0.1
            
            # Check for known proxy/VPN ranges (simplified)
            high_risk_prefixes = ['185.', '46.', '91.']
            for prefix in high_risk_prefixes:
                if ip_address.startswith(prefix):
                    risk_score += 0.2
                    break
            
            # Simulate geolocation risk
            # Random risk for demo purposes
            if random.random() > 0.8:  # 20% chance of high-risk location
                risk_score += 0.3
            
            return min(risk_score, 0.4)
            
        except Exception:
            return 0.1
    
    def _analyze_velocity_risk(self, payment: Payment) -> float:
        """
        Analyze risk based on transaction velocity
        (frequency of transactions from same merchant/customer)
        """
        try:
            # Simplified velocity check
            # In production, this would query the database for recent transactions
            
            # Simulate velocity risk
            velocity_risk = random.uniform(0.0, 0.3)
            
            return velocity_risk
            
        except Exception:
            return 0.1
    
    def _analyze_card_risk(self, card_token: str) -> float:
        """
        Analyze risk based on card information
        """
        try:
            risk_score = 0.0
            
            # Check token format (simplified)
            if len(card_token) < 10:
                risk_score += 0.2
            
            # Simulate card reputation check
            if random.random() > 0.9:  # 10% chance of risky card
                risk_score += 0.4
            
            return min(risk_score, 0.3)
            
        except Exception:
            return 0.1
    
    def _analyze_time_risk(self) -> float:
        """
        Analyze risk based on transaction time
        """
        try:
            import datetime
            
            current_hour = datetime.datetime.now().hour
            
            # Higher risk during unusual hours (late night/early morning)
            if current_hour < 6 or current_hour > 23:
                return 0.1
            else:
                return 0.0
                
        except Exception:
            return 0.0
    
    def is_high_risk(self, fraud_score: float) -> bool:
        """
        Determine if a transaction is high risk based on fraud score
        """
        return fraud_score > 0.7
    
    def is_medium_risk(self, fraud_score: float) -> bool:
        """
        Determine if a transaction is medium risk based on fraud score
        """
        return 0.3 < fraud_score <= 0.7
    
    def get_risk_level(self, fraud_score: float) -> str:
        """
        Get risk level description based on fraud score
        """
        if fraud_score > 0.7:
            return "HIGH"
        elif fraud_score > 0.3:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_recommended_action(self, fraud_score: float) -> str:
        """
        Get recommended action based on fraud score
        """
        if fraud_score > 0.8:
            return "BLOCK"
        elif fraud_score > 0.6:
            return "REVIEW"
        elif fraud_score > 0.3:
            return "MONITOR"
        else:
            return "APPROVE"

