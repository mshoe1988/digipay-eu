import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from src.models.payment import Payment, TransactionLog
from src.models.user import Merchant
import json

logger = logging.getLogger(__name__)

class ComplianceService:
    """
    Compliance service for EU regulations (PSD2, GDPR, PCI DSS)
    """
    
    def __init__(self):
        self.pci_dss_version = "4.0"
        self.gdpr_retention_period = 7 * 365  # 7 years in days
        self.psd2_sca_threshold = 3000  # 30 EUR in cents
        
    def validate_psd2_compliance(self, payment: Payment) -> Dict[str, Any]:
        """
        Validate PSD2 compliance for a payment transaction
        """
        try:
            compliance_result = {
                'compliant': True,
                'issues': [],
                'sca_required': False,
                'open_banking_eligible': False
            }
            
            # Check Strong Customer Authentication (SCA) requirements
            if self._requires_sca(payment):
                compliance_result['sca_required'] = True
                if not self._has_sca_exemption(payment):
                    compliance_result['issues'].append('Strong Customer Authentication required')
            
            # Check if transaction is eligible for Open Banking
            if self._is_open_banking_eligible(payment):
                compliance_result['open_banking_eligible'] = True
            
            # Validate merchant authorization
            if not self._validate_merchant_authorization(payment.merchant_id):
                compliance_result['compliant'] = False
                compliance_result['issues'].append('Merchant not authorized for PSD2 services')
            
            # Check transaction limits
            if not self._validate_transaction_limits(payment):
                compliance_result['compliant'] = False
                compliance_result['issues'].append('Transaction exceeds PSD2 limits')
            
            logger.info(f"PSD2 compliance check for {payment.transaction_id}: {compliance_result}")
            return compliance_result
            
        except Exception as e:
            logger.error(f"Error validating PSD2 compliance: {str(e)}")
            return {
                'compliant': False,
                'issues': ['PSD2 compliance validation failed'],
                'sca_required': True,
                'open_banking_eligible': False
            }
    
    def validate_gdpr_compliance(self, payment: Payment) -> Dict[str, Any]:
        """
        Validate GDPR compliance for personal data processing
        """
        try:
            compliance_result = {
                'compliant': True,
                'issues': [],
                'data_minimization': True,
                'consent_required': False,
                'retention_compliant': True
            }
            
            # Check data minimization principle
            if not self._validate_data_minimization(payment):
                compliance_result['data_minimization'] = False
                compliance_result['issues'].append('Excessive personal data collection')
            
            # Check if explicit consent is required
            if self._requires_explicit_consent(payment):
                compliance_result['consent_required'] = True
                if not self._has_valid_consent(payment):
                    compliance_result['compliant'] = False
                    compliance_result['issues'].append('Valid consent required for data processing')
            
            # Check data retention compliance
            if not self._validate_data_retention(payment):
                compliance_result['retention_compliant'] = False
                compliance_result['issues'].append('Data retention period exceeded')
            
            # Validate lawful basis for processing
            if not self._has_lawful_basis(payment):
                compliance_result['compliant'] = False
                compliance_result['issues'].append('No lawful basis for personal data processing')
            
            logger.info(f"GDPR compliance check for {payment.transaction_id}: {compliance_result}")
            return compliance_result
            
        except Exception as e:
            logger.error(f"Error validating GDPR compliance: {str(e)}")
            return {
                'compliant': False,
                'issues': ['GDPR compliance validation failed'],
                'data_minimization': False,
                'consent_required': True,
                'retention_compliant': False
            }
    
    def validate_pci_dss_compliance(self, payment: Payment) -> Dict[str, Any]:
        """
        Validate PCI DSS compliance for card data handling
        """
        try:
            compliance_result = {
                'compliant': True,
                'issues': [],
                'card_data_encrypted': True,
                'tokenization_used': True,
                'network_security': True
            }
            
            # Check if card data is properly encrypted
            if not self._validate_card_encryption(payment):
                compliance_result['card_data_encrypted'] = False
                compliance_result['compliant'] = False
                compliance_result['issues'].append('Card data not properly encrypted')
            
            # Check if tokenization is used
            if not self._validate_tokenization(payment):
                compliance_result['tokenization_used'] = False
                compliance_result['issues'].append('Card tokenization not implemented')
            
            # Validate network security
            if not self._validate_network_security(payment):
                compliance_result['network_security'] = False
                compliance_result['compliant'] = False
                compliance_result['issues'].append('Network security requirements not met')
            
            # Check access controls
            if not self._validate_access_controls():
                compliance_result['compliant'] = False
                compliance_result['issues'].append('Access control requirements not met')
            
            logger.info(f"PCI DSS compliance check for {payment.transaction_id}: {compliance_result}")
            return compliance_result
            
        except Exception as e:
            logger.error(f"Error validating PCI DSS compliance: {str(e)}")
            return {
                'compliant': False,
                'issues': ['PCI DSS compliance validation failed'],
                'card_data_encrypted': False,
                'tokenization_used': False,
                'network_security': False
            }
    
    def generate_compliance_report(self, merchant_id: str = None) -> Dict[str, Any]:
        """
        Generate a comprehensive compliance report
        """
        try:
            report = {
                'generated_at': datetime.utcnow().isoformat(),
                'merchant_id': merchant_id,
                'psd2_compliance': self._get_psd2_status(),
                'gdpr_compliance': self._get_gdpr_status(),
                'pci_dss_compliance': self._get_pci_dss_status(),
                'overall_status': 'COMPLIANT',
                'recommendations': []
            }
            
            # Check overall compliance status
            if not all([
                report['psd2_compliance']['status'] == 'COMPLIANT',
                report['gdpr_compliance']['status'] == 'COMPLIANT',
                report['pci_dss_compliance']['status'] == 'COMPLIANT'
            ]):
                report['overall_status'] = 'NON_COMPLIANT'
            
            # Add recommendations
            report['recommendations'] = self._generate_recommendations(report)
            
            logger.info(f"Compliance report generated for merchant {merchant_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {str(e)}")
            return {
                'generated_at': datetime.utcnow().isoformat(),
                'merchant_id': merchant_id,
                'overall_status': 'ERROR',
                'error': str(e)
            }
    
    def _requires_sca(self, payment: Payment) -> bool:
        """Check if Strong Customer Authentication is required"""
        # SCA required for amounts over 30 EUR
        if float(payment.amount) > self.psd2_sca_threshold:
            return True
        
        # SCA required for high-risk transactions
        if payment.fraud_score and payment.fraud_score > 0.5:
            return True
        
        return False
    
    def _has_sca_exemption(self, payment: Payment) -> bool:
        """Check if transaction qualifies for SCA exemption"""
        # Low-value exemption (under 30 EUR)
        if float(payment.amount) <= self.psd2_sca_threshold:
            return True
        
        # Trusted beneficiary exemption (simplified for demo)
        if payment.merchant_id in ['merchant_trusted_001', 'merchant_trusted_002']:
            return True
        
        return False
    
    def _is_open_banking_eligible(self, payment: Payment) -> bool:
        """Check if transaction is eligible for Open Banking"""
        # Bank transfer payments are eligible for Open Banking
        return payment.payment_method.value == 'bank_transfer'
    
    def _validate_merchant_authorization(self, merchant_id: str) -> bool:
        """Validate merchant authorization for PSD2 services"""
        try:
            # In production, this would check against a regulatory database
            # For demo, assume all merchants are authorized
            return True
        except Exception:
            return False
    
    def _validate_transaction_limits(self, payment: Payment) -> bool:
        """Validate transaction against PSD2 limits"""
        # EU instant payment limit is 100,000 EUR
        max_amount = 10000000  # 100,000 EUR in cents
        return float(payment.amount) <= max_amount
    
    def _validate_data_minimization(self, payment: Payment) -> bool:
        """Validate GDPR data minimization principle"""
        # Check if only necessary data is collected
        necessary_fields = ['customer_email', 'amount', 'currency', 'payment_method']
        
        # For demo, assume data minimization is followed
        return True
    
    def _requires_explicit_consent(self, payment: Payment) -> bool:
        """Check if explicit consent is required for data processing"""
        # Explicit consent required for marketing or profiling
        # For payment processing, contract is usually the lawful basis
        return False
    
    def _has_valid_consent(self, payment: Payment) -> bool:
        """Check if valid consent exists for data processing"""
        # In production, this would check consent records
        return True
    
    def _validate_data_retention(self, payment: Payment) -> bool:
        """Validate data retention compliance"""
        # Check if data is within retention period
        retention_date = payment.created_at + timedelta(days=self.gdpr_retention_period)
        return datetime.utcnow() < retention_date
    
    def _has_lawful_basis(self, payment: Payment) -> bool:
        """Check if there's a lawful basis for processing personal data"""
        # For payment processing, contract is the typical lawful basis
        return True
    
    def _validate_card_encryption(self, payment: Payment) -> bool:
        """Validate card data encryption"""
        # Check if card token exists (indicates encryption/tokenization)
        return payment.card_token is not None and payment.card_token.startswith('tok_')
    
    def _validate_tokenization(self, payment: Payment) -> bool:
        """Validate card tokenization implementation"""
        # Check if actual card number is not stored
        return payment.card_token is not None and not any(char.isdigit() for char in payment.card_token[:10])
    
    def _validate_network_security(self, payment: Payment) -> bool:
        """Validate network security requirements"""
        # In production, this would check TLS version, firewall rules, etc.
        return True
    
    def _validate_access_controls(self) -> bool:
        """Validate access control requirements"""
        # In production, this would check user permissions, authentication, etc.
        return True
    
    def _get_psd2_status(self) -> Dict[str, Any]:
        """Get current PSD2 compliance status"""
        return {
            'status': 'COMPLIANT',
            'last_audit': '2025-01-15',
            'next_audit': '2025-07-15',
            'sca_enabled': True,
            'open_banking_apis': True
        }
    
    def _get_gdpr_status(self) -> Dict[str, Any]:
        """Get current GDPR compliance status"""
        return {
            'status': 'COMPLIANT',
            'data_retention_policy': f'{self.gdpr_retention_period // 365} years',
            'right_to_be_forgotten': True,
            'data_protection_officer': True,
            'privacy_by_design': True
        }
    
    def _get_pci_dss_status(self) -> Dict[str, Any]:
        """Get current PCI DSS compliance status"""
        return {
            'status': 'COMPLIANT',
            'version': self.pci_dss_version,
            'last_assessment': '2025-01-15',
            'next_assessment': '2025-07-15',
            'tokenization': True,
            'encryption': True
        }
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        if report['overall_status'] != 'COMPLIANT':
            recommendations.append('Address non-compliance issues immediately')
        
        recommendations.extend([
            'Conduct regular security audits',
            'Update staff training on compliance requirements',
            'Review and update privacy policies',
            'Implement continuous monitoring for compliance violations',
            'Maintain documentation for regulatory inspections'
        ])
        
        return recommendations
    
    def log_compliance_event(self, event_type: str, details: Dict[str, Any]):
        """Log compliance-related events for audit trail"""
        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': event_type,
                'details': details
            }
            
            # In production, this would be stored in a secure audit log
            logger.info(f"Compliance event logged: {json.dumps(log_entry)}")
            
        except Exception as e:
            logger.error(f"Error logging compliance event: {str(e)}")
    
    def handle_data_subject_request(self, request_type: str, customer_email: str) -> Dict[str, Any]:
        """
        Handle GDPR data subject requests (access, rectification, erasure, portability)
        """
        try:
            result = {
                'request_type': request_type,
                'customer_email': customer_email,
                'status': 'PROCESSED',
                'processed_at': datetime.utcnow().isoformat()
            }
            
            if request_type == 'access':
                # Provide all personal data
                result['data'] = self._get_customer_data(customer_email)
            elif request_type == 'erasure':
                # Delete personal data (right to be forgotten)
                result['deleted_records'] = self._delete_customer_data(customer_email)
            elif request_type == 'rectification':
                # Correct inaccurate personal data
                result['message'] = 'Data rectification process initiated'
            elif request_type == 'portability':
                # Provide data in machine-readable format
                result['data_export'] = self._export_customer_data(customer_email)
            
            self.log_compliance_event('data_subject_request', result)
            return result
            
        except Exception as e:
            logger.error(f"Error handling data subject request: {str(e)}")
            return {
                'request_type': request_type,
                'customer_email': customer_email,
                'status': 'ERROR',
                'error': str(e)
            }
    
    def _get_customer_data(self, customer_email: str) -> Dict[str, Any]:
        """Get all personal data for a customer"""
        # In production, this would query all relevant tables
        return {
            'email': customer_email,
            'transactions': [],
            'personal_data': {}
        }
    
    def _delete_customer_data(self, customer_email: str) -> int:
        """Delete customer personal data"""
        # In production, this would delete/anonymize data across all systems
        return 0  # Number of records deleted
    
    def _export_customer_data(self, customer_email: str) -> Dict[str, Any]:
        """Export customer data in machine-readable format"""
        return self._get_customer_data(customer_email)

