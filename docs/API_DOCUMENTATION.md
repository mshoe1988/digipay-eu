# Digipay EU API Documentation

**Version:** 2.0.0  
**Base URL:** `https://api.digipay.eu/v1`  
**Authentication:** API Key or JWT Token  
**Content-Type:** `application/json`

## Table of Contents

1. [Authentication](#authentication)
2. [Rate Limiting](#rate-limiting)
3. [Error Handling](#error-handling)
4. [Payment Endpoints](#payment-endpoints)
5. [Merchant Endpoints](#merchant-endpoints)
6. [Compliance Endpoints](#compliance-endpoints)
7. [Security Endpoints](#security-endpoints)
8. [Webhook Endpoints](#webhook-endpoints)
9. [SDKs and Libraries](#sdks-and-libraries)

## Authentication

PayGateway API supports two authentication methods: API Keys for server-to-server communication and JWT tokens for client applications.

### API Key Authentication

API keys are the recommended authentication method for server-to-server integration. They provide secure, long-term access without requiring token refresh mechanisms.

**Header Format:**
```http
X-API-Key: pk_live_your_api_key_here
```

**API Key Types:**
- **Public Keys** (`pk_`): Used for client-side operations with limited permissions
- **Secret Keys** (`sk_`): Used for server-side operations with full permissions

**Example Request:**
```bash
curl -X GET "https://api.paygateway.com/v1/payments" \
  -H "X-API-Key: pk_live_1234567890abcdef" \
  -H "Content-Type: application/json"
```

### JWT Token Authentication

JWT tokens provide temporary access and are ideal for client applications where API keys cannot be securely stored.

**Header Format:**
```http
Authorization: Bearer your_jwt_token_here
```

**Token Acquisition:**
```bash
curl -X POST "https://api.paygateway.com/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

## Rate Limiting

To ensure fair usage and system stability, the PayGateway API implements rate limiting based on your subscription tier and endpoint usage patterns.

### Rate Limit Tiers

| Tier | Requests per Hour | Burst Limit | Overage Policy |
|------|------------------|-------------|----------------|
| Starter | 1,000 | 100 | Block |
| Professional | 10,000 | 500 | Throttle |
| Enterprise | 100,000 | 2,000 | Custom |
| Unlimited | No limit | No limit | N/A |

### Rate Limit Headers

All API responses include rate limiting information in the headers:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1625097600
X-RateLimit-Retry-After: 3600
```

### Rate Limit Exceeded Response

When rate limits are exceeded, the API returns a 429 status code:

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Please try again later.",
    "retry_after": 3600
  }
}
```

## Error Handling

PayGateway API uses conventional HTTP response codes to indicate the success or failure of API requests. Error responses include detailed information to help developers diagnose and resolve issues.

### HTTP Status Codes

| Code | Description | Usage |
|------|-------------|-------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Temporary service unavailability |

### Error Response Format

All error responses follow a consistent format:

```json
{
  "error": {
    "code": "validation_error",
    "message": "The request contains invalid parameters.",
    "details": {
      "field": "amount",
      "issue": "Amount must be greater than 0"
    },
    "request_id": "req_1234567890abcdef",
    "timestamp": "2025-07-14T10:30:00Z"
  }
}
```

### Common Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `invalid_api_key` | API key is invalid or expired | Check API key format and validity |
| `insufficient_permissions` | API key lacks required permissions | Use appropriate API key type |
| `validation_error` | Request parameters are invalid | Review parameter requirements |
| `merchant_not_found` | Merchant ID does not exist | Verify merchant ID |
| `payment_not_found` | Payment transaction not found | Check transaction ID |
| `compliance_violation` | Request violates compliance rules | Review compliance requirements |
| `fraud_detected` | Transaction flagged by fraud detection | Review transaction details |

## Payment Endpoints

The payment endpoints handle all aspects of payment processing, from transaction creation to refund management.

### Create Payment

Creates a new payment transaction with comprehensive validation and fraud detection.

**Endpoint:** `POST /payments`

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `merchant_id` | string | Yes | Unique merchant identifier |
| `amount` | number | Yes | Payment amount in cents |
| `currency` | string | Yes | ISO 4217 currency code |
| `payment_method` | string | Yes | Payment method type |
| `customer_email` | string | No | Customer email address |
| `customer_name` | string | No | Customer full name |
| `description` | string | No | Payment description |
| `reference_number` | string | No | Merchant reference number |
| `card_number` | string | Conditional | Card number (if card payment) |
| `card_expiry` | string | Conditional | Card expiry (MM/YY) |
| `card_cvv` | string | Conditional | Card CVV code |
| `billing_address` | object | No | Billing address details |

**Example Request:**
```bash
curl -X POST "https://api.paygateway.com/v1/payments" \
  -H "X-API-Key: sk_live_your_secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": "merchant_123",
    "amount": 2500,
    "currency": "EUR",
    "payment_method": "credit_card",
    "customer_email": "customer@example.com",
    "customer_name": "John Doe",
    "description": "Online purchase",
    "card_number": "4111111111111111",
    "card_expiry": "12/25",
    "card_cvv": "123",
    "billing_address": {
      "street": "123 Main St",
      "city": "Berlin",
      "postal_code": "10115",
      "country": "DE"
    }
  }'
```

**Success Response (201 Created):**
```json
{
  "transaction_id": "txn_1234567890abcdef",
  "status": "completed",
  "amount": 2500,
  "currency": "EUR",
  "payment_method": "credit_card",
  "merchant_id": "merchant_123",
  "customer_email": "customer@example.com",
  "card_token": "tok_1234567890abcdef",
  "card_last_four": "1111",
  "card_brand": "visa",
  "fraud_score": 0.15,
  "compliance_checks": {
    "psd2_compliant": true,
    "gdpr_compliant": true,
    "pci_compliant": true,
    "sca_required": false
  },
  "created_at": "2025-07-14T10:30:00Z",
  "processed_at": "2025-07-14T10:30:01Z"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": {
    "code": "validation_error",
    "message": "Invalid card number format",
    "details": {
      "field": "card_number",
      "issue": "Card number must be 13-19 digits"
    }
  }
}
```

### Retrieve Payment

Retrieves details of a specific payment transaction.

**Endpoint:** `GET /payments/{transaction_id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `transaction_id` | string | Yes | Unique transaction identifier |

**Example Request:**
```bash
curl -X GET "https://api.paygateway.com/v1/payments/txn_1234567890abcdef" \
  -H "X-API-Key: pk_live_your_public_key"
```

**Success Response (200 OK):**
```json
{
  "transaction_id": "txn_1234567890abcdef",
  "status": "completed",
  "amount": 2500,
  "currency": "EUR",
  "payment_method": "credit_card",
  "merchant_id": "merchant_123",
  "customer_email": "customer@example.com",
  "description": "Online purchase",
  "card_last_four": "1111",
  "card_brand": "visa",
  "fraud_score": 0.15,
  "created_at": "2025-07-14T10:30:00Z",
  "processed_at": "2025-07-14T10:30:01Z",
  "settlement_date": "2025-07-15T00:00:00Z"
}
```

### List Payments

Retrieves a list of payment transactions with optional filtering and pagination.

**Endpoint:** `GET /payments`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `merchant_id` | string | No | Filter by merchant ID |
| `status` | string | No | Filter by payment status |
| `currency` | string | No | Filter by currency |
| `payment_method` | string | No | Filter by payment method |
| `start_date` | string | No | Filter by start date (ISO 8601) |
| `end_date` | string | No | Filter by end date (ISO 8601) |
| `limit` | integer | No | Number of results (max 100) |
| `offset` | integer | No | Pagination offset |

**Example Request:**
```bash
curl -X GET "https://api.paygateway.com/v1/payments?merchant_id=merchant_123&status=completed&limit=10" \
  -H "X-API-Key: pk_live_your_public_key"
```

**Success Response (200 OK):**
```json
{
  "data": [
    {
      "transaction_id": "txn_1234567890abcdef",
      "status": "completed",
      "amount": 2500,
      "currency": "EUR",
      "payment_method": "credit_card",
      "merchant_id": "merchant_123",
      "created_at": "2025-07-14T10:30:00Z"
    }
  ],
  "pagination": {
    "total": 150,
    "limit": 10,
    "offset": 0,
    "has_more": true
  }
}
```

### Refund Payment

Processes a full or partial refund for a completed payment transaction.

**Endpoint:** `POST /payments/{transaction_id}/refund`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `transaction_id` | string | Yes | Unique transaction identifier |

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `amount` | number | No | Refund amount (defaults to full amount) |
| `reason` | string | No | Reason for refund |
| `reference_number` | string | No | Merchant reference for refund |

**Example Request:**
```bash
curl -X POST "https://api.paygateway.com/v1/payments/txn_1234567890abcdef/refund" \
  -H "X-API-Key: sk_live_your_secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000,
    "reason": "Customer request",
    "reference_number": "REF123"
  }'
```

**Success Response (200 OK):**
```json
{
  "refund_id": "rfnd_1234567890abcdef",
  "transaction_id": "txn_1234567890abcdef",
  "status": "completed",
  "amount": 1000,
  "currency": "EUR",
  "reason": "Customer request",
  "reference_number": "REF123",
  "processed_at": "2025-07-14T11:00:00Z",
  "settlement_date": "2025-07-15T00:00:00Z"
}
```

## Merchant Endpoints

Merchant endpoints provide comprehensive merchant account management capabilities.

### Create Merchant

Creates a new merchant account with KYC validation and compliance checks.

**Endpoint:** `POST /merchants`

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `business_name` | string | Yes | Legal business name |
| `business_type` | string | Yes | Type of business |
| `contact_email` | string | Yes | Primary contact email |
| `contact_phone` | string | Yes | Primary contact phone |
| `business_address` | object | Yes | Business address details |
| `tax_id` | string | Yes | Business tax identification |
| `website_url` | string | No | Business website URL |
| `description` | string | No | Business description |
| `processing_volume` | number | No | Expected monthly volume |

**Example Request:**
```bash
curl -X POST "https://api.paygateway.com/v1/merchants" \
  -H "X-API-Key: sk_live_your_secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "Example Store GmbH",
    "business_type": "e_commerce",
    "contact_email": "contact@example-store.com",
    "contact_phone": "+49301234567",
    "business_address": {
      "street": "Unter den Linden 1",
      "city": "Berlin",
      "postal_code": "10117",
      "country": "DE"
    },
    "tax_id": "DE123456789",
    "website_url": "https://example-store.com",
    "description": "Online electronics retailer",
    "processing_volume": 50000
  }'
```

**Success Response (201 Created):**
```json
{
  "merchant_id": "merchant_1234567890abcdef",
  "business_name": "Example Store GmbH",
  "business_type": "e_commerce",
  "contact_email": "contact@example-store.com",
  "status": "pending_verification",
  "is_active": false,
  "is_verified": false,
  "api_keys": {
    "public_key": "pk_test_1234567890abcdef",
    "secret_key": "sk_test_1234567890abcdef"
  },
  "compliance_status": {
    "kyc_status": "pending",
    "aml_status": "pending",
    "pci_status": "not_required"
  },
  "created_at": "2025-07-14T10:30:00Z"
}
```

### Retrieve Merchant

Retrieves details of a specific merchant account.

**Endpoint:** `GET /merchants/{merchant_id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `merchant_id` | string | Yes | Unique merchant identifier |

**Example Request:**
```bash
curl -X GET "https://api.paygateway.com/v1/merchants/merchant_1234567890abcdef" \
  -H "X-API-Key: sk_live_your_secret_key"
```

**Success Response (200 OK):**
```json
{
  "merchant_id": "merchant_1234567890abcdef",
  "business_name": "Example Store GmbH",
  "business_type": "e_commerce",
  "contact_email": "contact@example-store.com",
  "status": "active",
  "is_active": true,
  "is_verified": true,
  "processing_limits": {
    "daily_limit": 100000,
    "monthly_limit": 2000000,
    "transaction_limit": 10000
  },
  "settlement_schedule": "daily",
  "fee_structure": {
    "transaction_fee": 0.029,
    "fixed_fee": 30
  },
  "created_at": "2025-07-14T10:30:00Z",
  "verified_at": "2025-07-15T09:15:00Z"
}
```

### Update Merchant

Updates merchant account information and settings.

**Endpoint:** `PUT /merchants/{merchant_id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `merchant_id` | string | Yes | Unique merchant identifier |

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `contact_email` | string | No | Updated contact email |
| `contact_phone` | string | No | Updated contact phone |
| `website_url` | string | No | Updated website URL |
| `description` | string | No | Updated business description |
| `processing_volume` | number | No | Updated expected volume |

**Example Request:**
```bash
curl -X PUT "https://api.paygateway.com/v1/merchants/merchant_1234567890abcdef" \
  -H "X-API-Key: sk_live_your_secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_email": "new-contact@example-store.com",
    "website_url": "https://new-example-store.com",
    "processing_volume": 75000
  }'
```

**Success Response (200 OK):**
```json
{
  "merchant_id": "merchant_1234567890abcdef",
  "business_name": "Example Store GmbH",
  "contact_email": "new-contact@example-store.com",
  "website_url": "https://new-example-store.com",
  "processing_volume": 75000,
  "updated_at": "2025-07-14T11:00:00Z"
}
```

## Compliance Endpoints

Compliance endpoints provide access to regulatory compliance information and reporting.

### Generate Compliance Report

Generates a comprehensive compliance report for regulatory requirements.

**Endpoint:** `GET /compliance/report`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `merchant_id` | string | No | Specific merchant ID |
| `start_date` | string | No | Report start date |
| `end_date` | string | No | Report end date |
| `report_type` | string | No | Type of compliance report |

**Example Request:**
```bash
curl -X GET "https://api.paygateway.com/v1/compliance/report?merchant_id=merchant_123&report_type=psd2" \
  -H "X-API-Key: sk_live_your_secret_key"
```

**Success Response (200 OK):**
```json
{
  "report_id": "rpt_1234567890abcdef",
  "generated_at": "2025-07-14T10:30:00Z",
  "merchant_id": "merchant_123",
  "report_type": "comprehensive",
  "period": {
    "start_date": "2025-06-01T00:00:00Z",
    "end_date": "2025-06-30T23:59:59Z"
  },
  "psd2_compliance": {
    "status": "COMPLIANT",
    "sca_transactions": 1250,
    "sca_exemptions": 3750,
    "open_banking_requests": 45
  },
  "gdpr_compliance": {
    "status": "COMPLIANT",
    "data_subject_requests": 12,
    "consent_records": 5000,
    "data_retention_compliant": true
  },
  "pci_dss_compliance": {
    "status": "COMPLIANT",
    "last_assessment": "2025-01-15T00:00:00Z",
    "next_assessment": "2025-07-15T00:00:00Z",
    "tokenization_rate": 100
  },
  "recommendations": [
    "Continue regular security assessments",
    "Update privacy policy for new regulations",
    "Implement additional fraud detection measures"
  ]
}
```

### Handle Data Subject Request

Processes GDPR data subject requests for access, rectification, erasure, or portability.

**Endpoint:** `POST /compliance/data-subject-request`

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `request_type` | string | Yes | Type of request (access, erasure, etc.) |
| `customer_email` | string | Yes | Customer email address |
| `verification_token` | string | Yes | Customer verification token |
| `additional_info` | object | No | Additional request information |

**Example Request:**
```bash
curl -X POST "https://api.paygateway.com/v1/compliance/data-subject-request" \
  -H "X-API-Key: sk_live_your_secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "request_type": "access",
    "customer_email": "customer@example.com",
    "verification_token": "vrf_1234567890abcdef"
  }'
```

**Success Response (200 OK):**
```json
{
  "request_id": "dsr_1234567890abcdef",
  "request_type": "access",
  "customer_email": "customer@example.com",
  "status": "processed",
  "processed_at": "2025-07-14T10:30:00Z",
  "data_export_url": "https://secure.paygateway.com/exports/dsr_1234567890abcdef.json",
  "expiry_date": "2025-07-21T10:30:00Z"
}
```

## Security Endpoints

Security endpoints manage API keys, authentication, and security monitoring.

### Generate API Key

Generates new API keys for merchant authentication.

**Endpoint:** `POST /security/api-key`

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `merchant_id` | string | Yes | Merchant identifier |
| `key_type` | string | Yes | Type of key (public/secret) |
| `permissions` | array | No | Specific permissions for the key |
| `expiry_date` | string | No | Key expiration date |

**Example Request:**
```bash
curl -X POST "https://api.paygateway.com/v1/security/api-key" \
  -H "X-API-Key: sk_live_your_secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": "merchant_123",
    "key_type": "secret",
    "permissions": ["payments:read", "payments:write"],
    "expiry_date": "2026-07-14T00:00:00Z"
  }'
```

**Success Response (201 Created):**
```json
{
  "api_key": "sk_live_new_1234567890abcdef",
  "key_type": "secret",
  "merchant_id": "merchant_123",
  "permissions": ["payments:read", "payments:write"],
  "created_at": "2025-07-14T10:30:00Z",
  "expiry_date": "2026-07-14T00:00:00Z",
  "last_used": null
}
```

### Revoke API Key

Revokes an existing API key to prevent further use.

**Endpoint:** `DELETE /security/api-key/{key_id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `key_id` | string | Yes | API key identifier |

**Example Request:**
```bash
curl -X DELETE "https://api.paygateway.com/v1/security/api-key/key_1234567890abcdef" \
  -H "X-API-Key: sk_live_your_secret_key"
```

**Success Response (200 OK):**
```json
{
  "key_id": "key_1234567890abcdef",
  "status": "revoked",
  "revoked_at": "2025-07-14T10:30:00Z"
}
```

## Webhook Endpoints

Webhooks provide real-time notifications for payment events and system updates.

### Configure Webhook

Configures webhook endpoints for receiving event notifications.

**Endpoint:** `POST /webhooks`

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | Webhook endpoint URL |
| `events` | array | Yes | List of events to subscribe to |
| `secret` | string | No | Webhook signing secret |
| `active` | boolean | No | Whether webhook is active |

**Example Request:**
```bash
curl -X POST "https://api.paygateway.com/v1/webhooks" \
  -H "X-API-Key: sk_live_your_secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-site.com/webhooks/paygateway",
    "events": ["payment.completed", "payment.failed", "refund.processed"],
    "secret": "your_webhook_secret",
    "active": true
  }'
```

**Success Response (201 Created):**
```json
{
  "webhook_id": "wh_1234567890abcdef",
  "url": "https://your-site.com/webhooks/paygateway",
  "events": ["payment.completed", "payment.failed", "refund.processed"],
  "active": true,
  "created_at": "2025-07-14T10:30:00Z"
}
```

### Webhook Event Format

All webhook events follow a consistent format:

```json
{
  "id": "evt_1234567890abcdef",
  "type": "payment.completed",
  "created": 1625097600,
  "data": {
    "object": {
      "transaction_id": "txn_1234567890abcdef",
      "status": "completed",
      "amount": 2500,
      "currency": "EUR",
      "merchant_id": "merchant_123"
    }
  },
  "request": {
    "id": "req_1234567890abcdef",
    "idempotency_key": null
  }
}
```

### Webhook Signature Verification

Verify webhook signatures to ensure authenticity:

```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
```

## SDKs and Libraries

PayGateway provides official SDKs for popular programming languages to simplify integration.

### Python SDK

```python
import paygateway

# Initialize client
client = paygateway.Client(api_key='sk_live_your_secret_key')

# Create payment
payment = client.payments.create(
    merchant_id='merchant_123',
    amount=2500,
    currency='EUR',
    payment_method='credit_card',
    customer_email='customer@example.com'
)

print(f"Payment created: {payment.transaction_id}")
```

### Node.js SDK

```javascript
const PayGateway = require('paygateway-node');

// Initialize client
const client = new PayGateway('sk_live_your_secret_key');

// Create payment
const payment = await client.payments.create({
  merchant_id: 'merchant_123',
  amount: 2500,
  currency: 'EUR',
  payment_method: 'credit_card',
  customer_email: 'customer@example.com'
});

console.log(`Payment created: ${payment.transaction_id}`);
```

### PHP SDK

```php
<?php
require_once 'vendor/autoload.php';

use PayGateway\Client;

// Initialize client
$client = new Client('sk_live_your_secret_key');

// Create payment
$payment = $client->payments->create([
    'merchant_id' => 'merchant_123',
    'amount' => 2500,
    'currency' => 'EUR',
    'payment_method' => 'credit_card',
    'customer_email' => 'customer@example.com'
]);

echo "Payment created: " . $payment->transaction_id;
?>
```

### Java SDK

```java
import com.paygateway.PayGatewayClient;
import com.paygateway.model.Payment;

// Initialize client
PayGatewayClient client = new PayGatewayClient("sk_live_your_secret_key");

// Create payment
Payment payment = client.payments().create(
    Payment.builder()
        .merchantId("merchant_123")
        .amount(2500)
        .currency("EUR")
        .paymentMethod("credit_card")
        .customerEmail("customer@example.com")
        .build()
);

System.out.println("Payment created: " + payment.getTransactionId());
```

## Testing

PayGateway provides a comprehensive testing environment with test API keys and mock data.

### Test Environment

- **Base URL:** `https://api-test.paygateway.com/v1`
- **Test API Keys:** Use keys prefixed with `pk_test_` and `sk_test_`
- **Test Cards:** Use specific test card numbers for different scenarios

### Test Card Numbers

| Card Number | Brand | Scenario |
|-------------|-------|----------|
| 4111111111111111 | Visa | Successful payment |
| 4000000000000002 | Visa | Card declined |
| 4000000000009995 | Visa | Insufficient funds |
| 5555555555554444 | Mastercard | Successful payment |
| 5200828282828210 | Mastercard | Card declined |

### Webhook Testing

Use tools like ngrok to expose local endpoints for webhook testing:

```bash
# Install ngrok
npm install -g ngrok

# Expose local port
ngrok http 3000

# Use the generated URL for webhook configuration
```

---

*This API documentation is regularly updated to reflect the latest features and changes. For the most current information and interactive API explorer, visit our developer portal at [developer.paygateway.com](https://developer.paygateway.com).*

