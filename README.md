# Digipay EU - Payment Gateway Platform

**Version:** 2.0.0  
**Company:** Digipay EU  
**Status:** Production Ready

## 🚀 Quick Start

### Deploy to Render

1. **Upload these files to GitHub**
2. **Connect GitHub to Render**
3. **Set Root Directory to**: (leave empty)
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `gunicorn --bind 0.0.0.0:$PORT src.main:app`

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

Access at: `http://localhost:5000`

## 📁 Project Structure

```
digipay-eu/
├── src/
│   ├── main.py              # Main Flask application
│   ├── database.py          # Database configuration
│   ├── i18n.py             # Internationalization
│   ├── models/             # Database models
│   │   ├── user.py         # User and Merchant models
│   │   ├── payment.py      # Payment models
│   │   └── billing.py      # Billing models
│   ├── routes/             # API endpoints
│   │   ├── user.py         # User management
│   │   ├── payment.py      # Payment processing
│   │   ├── merchant.py     # Merchant management
│   │   └── billing.py      # Billing and revenue
│   ├── services/           # Business logic
│   │   ├── payment_processor.py
│   │   ├── fraud_detection.py
│   │   ├── billing_service.py
│   │   ├── compliance.py
│   │   ├── encryption.py
│   │   └── security.py
│   └── static/             # Frontend files
│       ├── index.html      # Dashboard interface
│       ├── styles.css      # Styling
│       ├── app.js          # JavaScript functionality
│       └── translations.js # Multi-language support
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
├── Procfile               # Render deployment config
└── README.md              # This file
```

## ✨ Features

### 💳 Payment Processing
- **Multi-payment methods**: Cards, bank transfers, digital wallets
- **Real-time processing**: Sub-second transaction handling
- **EU compliance**: PSD2, GDPR, PCI DSS compliant
- **Fraud detection**: ML-powered risk assessment

### 💰 Revenue Generation
- **European Cards**: 0.5% + €0.10 per transaction
- **Non-European Cards**: 2.4% + €0.20 per transaction
- **No monthly fees**: Competitive pricing model
- **Automated billing**: Invoice generation and collection

### 🌍 Multilingual Support
- **6 Languages**: English, Spanish, French, German, Italian, Portuguese
- **Real-time switching**: Instant language changes
- **Professional terminology**: Financial industry standards

### 🔒 Security & Compliance
- **PCI DSS Level 1**: Highest security standards
- **AES-256 Encryption**: Advanced data protection
- **JWT Authentication**: Secure API access
- **Audit logging**: Complete compliance trails

### 📊 Management Dashboard
- **Real-time analytics**: Transaction monitoring
- **Revenue tracking**: Comprehensive billing dashboard
- **Merchant management**: Complete lifecycle management
- **Fee calculator**: Transparent pricing tool

## 🔧 Configuration

### Environment Variables
```bash
# Database (optional - uses SQLite by default)
DATABASE_URL=postgresql://user:pass@host:port/db

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here

# Compliance
PCI_DSS_MODE=strict
GDPR_RETENTION_DAYS=2555
PSD2_SCA_ENABLED=true
```

### Render Settings
- **Root Directory**: (leave empty)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT src.main:app`
- **Python Version**: 3.11

## 📚 Documentation

- **API Documentation**: See `docs/API_DOCUMENTATION.md`
- **Deployment Guide**: See `docs/README.md`
- **Business Features**: Complete billing and revenue system

## 🆘 Support

### Common Issues

**Render Deployment Error**: Ensure Root Directory is empty and Start Command is correct.

**Database Issues**: Platform uses SQLite by default, PostgreSQL for production.

**Missing Dependencies**: All required packages are in `requirements.txt`.

### Features Included

✅ **Working Navigation** - All buttons functional  
✅ **Complete Translations** - 6 languages supported  
✅ **Revenue System** - Automated billing and fees  
✅ **EU Compliance** - PSD2, GDPR, PCI DSS ready  
✅ **Professional Dashboard** - Real-time monitoring  
✅ **Scalable Architecture** - Production-ready platform  

## 📄 License

MIT License - See LICENSE file for details.

---

**Digipay EU** - European Payment Processing Made Simple

*Ready for immediate deployment and revenue generation.*
