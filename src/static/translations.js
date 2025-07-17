// Translation system for PayGateway frontend
class Translator {
    constructor() {
        this.currentLanguage = 'en';
        this.translations = {};
        this.fallbackLanguage = 'en';
        this.loadTranslations();
    }

    // Load translations for all supported languages
    loadTranslations() {
        this.translations = {
            en: {
                // Page titles and headers
                'payment_gateway_dashboard': 'Digipay EU Dashboard',
                
                // Dashboard
                'dashboard': 'Dashboard',
                'dashboard_subtitle': 'Monitor your Digipay EU performance',
                'total_revenue': 'Total Revenue',
                'total_transactions': 'Total Transactions',
                'success_rate': 'Success Rate',
                'active_merchants': 'Active Merchants',
                'transaction_volume': 'Transaction Volume',
                'payment_methods': 'Payment Methods',
                'recent_transactions': 'Recent Transactions',
                'revenue_trends': 'Revenue Trends',
                'geographic_distribution': 'Geographic Distribution',
                'fraud_detection': 'Fraud Detection',
                'fraud_rate': 'Fraud Rate',
                'prevented_losses': 'Prevented Losses',
                'advanced_analytics': 'Advanced Analytics',
                
                // Navigation
                'transactions': 'Transactions',
                'merchants': 'Merchants',
                'analytics': 'Analytics',
                'security': 'Security',
                'settings': 'Settings',
                
                // Security & Compliance
                'security_compliance': 'Security & Compliance',
                'pci_dss_compliance': 'PCI DSS Compliance',
                'compliance': 'Compliance',
                'compliant': 'Compliant',
                'last_audit': 'Last audit',
                'next_audit': 'Next audit',
                'data_retention': 'Data retention',
                'right_to_be_forgotten': 'Right to be forgotten',
                'enabled': 'Enabled',
                'strong_customer_auth': 'Strong Customer Authentication',
                'active': 'Active',
                'inactive': 'Inactive',
                'verified': 'Verified',
                'open_banking_apis': 'Open Banking APIs',
                'available': 'Available',
                
                // System Settings
                'system_settings': 'System Settings',
                'api_configuration': 'API Configuration',
                'rate_limiting': 'Rate Limiting',
                'timeout': 'Timeout',
                'security_settings': 'Security Settings',
                'enable_2fa': 'Enable 2FA',
                'require_https': 'Require HTTPS',
                
                // Table headers
                'transaction_id': 'Transaction ID',
                'merchant': 'Merchant',
                'customer': 'Customer',
                'amount': 'Amount',
                'payment_method': 'Payment Method',
                'status': 'Status',
                'date': 'Date',
                'actions': 'Actions',
                
                // Status values
                'completed': 'Completed',
                'pending': 'Pending',
                'failed': 'Failed',
                'processing': 'Processing',
                
                // Filters and buttons
                'all_statuses': 'All Statuses',
                'all_merchants': 'All Merchants',
                'apply_filters': 'Apply Filters',
                'new_transaction': 'New Transaction',
                'add_merchant': 'Add Merchant',
                'view_all': 'View All',
                'update': 'Update',
                'to': 'to',
                
                // Common
                'search_transactions': 'Search transactions...',
                'requests_per_minute': 'Requests per minute',
                'seconds': 'Seconds',
                'last_7_days': 'Last 7 days',
                'last_30_days': 'Last 30 days',
                'last_90_days': 'Last 90 days',
                'admin_user': 'Admin User',
                'years': 'years',
                
                 // Merchant Authentication
                'page_title': 'Digipay EU - Merchant Portal',
                'hero_title': 'Start Processing Payments Today',
                'hero_subtitle': 'Join thousands of European businesses using our secure, compliant payment gateway.',
                'feature_compliance': 'EU Compliant (PSD2, GDPR, PCI DSS)',
                'feature_no_fees': 'No Monthly Fees - Pay Per Transaction',
                'feature_dashboard': 'Real-time Dashboard & Analytics',
                'feature_multilingual': 'Multi-language Support',
                'feature_fraud': 'Advanced Fraud Protection',
                'auth_title': 'Create Your Account',
                'auth_subtitle': 'Get started with your merchant account',
                'tab_register': 'Register',
                'tab_login': 'Login',
                'label_business_name': 'Business Name *',
                'label_business_type': 'Business Type',
                'label_email': 'Email Address *',
                'label_phone': 'Phone Number *',
                'label_address': 'Business Address',
                'label_website': 'Website URL',
                'label_password': 'Password *',
                'select_type': 'Select type',
                'type_ecommerce': 'E-commerce',
                'type_retail': 'Retail',
                'type_services': 'Services',
                'type_saas': 'SaaS',
                'type_marketplace': 'Marketplace',
                'type_other': 'Other',
                'placeholder_address': 'Street address, city, country',
                'btn_create_account': 'Create Account',
                'btn_login': 'Login',
                'terms_text': 'By creating an account, you agree to our',
                'terms_service': 'Terms of Service',
                'and': 'and',
                'privacy_policy': 'Privacy Policy',
                'registration_success': 'Account created successfully! You can now login.',
                'registration_failed': 'Registration failed',
                'login_success': 'Login successful! Redirecting...',
                'login_failed': 'Login failed',
                
                // Billing
                'billing': 'Billing',
                'billing_management': 'Billing Management',
                'billing_settings': 'Billing Settings',
                'billing_configuration': 'Billing Configuration',
                'generate_invoices': 'Generate Invoices',
                'total_platform_revenue': 'Total Platform Revenue',
                'monthly_revenue': 'Monthly Revenue',
                'avg_fee_per_transaction': 'Avg Fee per Transaction',
                'pending_invoices': 'Pending Invoices',
                'revenue_breakdown': 'Revenue Breakdown',
                'fee_distribution': 'Fee Distribution',
                'recent_invoices': 'Recent Invoices',
                'view_all_invoices': 'View All Invoices',
                'invoice_management': 'Invoice Management',
                'invoice_number': 'Invoice Number',
                'billing_period': 'Billing Period',
                'subtotal': 'Subtotal',
                'tax': 'Tax',
                'total': 'Total',
                'overdue': 'Overdue',
                'cancelled': 'Cancelled',
                'revenue': 'Revenue',
                'revenue_analytics': 'Revenue Analytics',
                'transaction_fees': 'Transaction Fees',
                'other_fees': 'Other Fees',
                'chargeback_fees': 'Chargeback Fees',
                'refund_fees': 'Refund Fees',
                'merchant_metrics': 'Merchant Metrics',
                'new_merchants': 'New Merchants',
                'avg_revenue_per_merchant': 'Avg Revenue per Merchant',
                'revenue_over_time': 'Revenue Over Time',
                'revenue_by_merchant': 'Revenue by Merchant',
                'fee_type_breakdown': 'Fee Type Breakdown',
                'fee_calculator': 'Fee Calculator',
                'calculate_transaction_fee': 'Calculate Transaction Fee',
                'transaction_amount': 'Transaction Amount',
                'card_type': 'Card Type',
                'european_card': 'European Card',
                'non_european_card': 'Non-European Card',
                'merchant_optional': 'Merchant (Optional)',
                'default_rates': 'Default Rates',
                'calculate': 'Calculate',
                'calculation_result': 'Calculation Result',
                'processing_fee': 'Processing Fee',
                'merchant_receives': 'Merchant Receives',
                'current_rates': 'Current Rates',
                'european_cards': 'European Cards',
                'non_european_cards': 'Non-European Cards',
                'competitive_advantage': 'Competitive Advantage',
                'no_monthly_fees': 'No monthly fees',
                'no_setup_fees': 'No setup fees',
                'no_hidden_charges': 'No hidden charges',
                'transparent_pricing': 'Transparent pricing',
                'default_fee_structure': 'Default Fee Structure',
                'european_card_percentage': 'European Card Percentage (%)',
                'european_card_fixed_fee': 'European Card Fixed Fee (€)',
                'non_european_card_percentage': 'Non-European Card Percentage (%)',
                'non_european_card_fixed_fee': 'Non-European Card Fixed Fee (€)',
                'default_billing_cycle': 'Default Billing Cycle',
                'monthly': 'Monthly',
                'weekly': 'Weekly',
                'daily': 'Daily',
                'auto_billing': 'Auto Billing',
                'enable_automatic_billing': 'Enable automatic billing',
                'cancel': 'Cancel',
                'save_configuration': 'Save Configuration'
            },
            
            es: {
                // Page titles and headers
                'payment_gateway_dashboard': 'Panel de Control de Digipay EU',
                'dashboard': 'Panel de Control',
                'monitor_performance': 'Monitorea el rendimiento de tu Digipay EU',
                'total_revenue': 'Ingresos Totales',
                'total_transactions': 'Transacciones Totales',
                'success_rate': 'Tasa de Éxito',
                'active_merchants': 'Comerciantes Activos',
                'transaction_volume': 'Volumen de Transacciones',
                'payment_methods': 'Métodos de Pago',
                'recent_transactions': 'Transacciones Recientes',
                'revenue_trends': 'Tendencias de Ingresos',
                'geographic_distribution': 'Distribución Geográfica',
                'fraud_detection': 'Detección de Fraude',
                'fraud_rate': 'Tasa de Fraude',
                'prevented_losses': 'Pérdidas Prevenidas',
                'advanced_analytics': 'Analíticas Avanzadas',
                
                // Navigation
                'transactions': 'Transacciones',
                'merchants': 'Comerciantes',
                'analytics': 'Analíticas',
                'security': 'Seguridad',
                'settings': 'Configuración',
                
                // Security & Compliance
                'security_compliance': 'Seguridad y Cumplimiento',
                'pci_dss_compliance': 'Cumplimiento PCI DSS',
                'compliance': 'Cumplimiento',
                'compliant': 'Conforme',
                'last_audit': 'Última auditoría',
                'next_audit': 'Próxima auditoría',
                'data_retention': 'Retención de datos',
                'right_to_be_forgotten': 'Derecho al olvido',
                'enabled': 'Habilitado',
                'strong_customer_auth': 'Autenticación Fuerte del Cliente',
                'active': 'Activo',
                'inactive': 'Inactivo',
                'verified': 'Verificado',
                'open_banking_apis': 'APIs de Banca Abierta',
                'available': 'Disponible',
                
                // System Settings
                'system_settings': 'Configuración del Sistema',
                'api_configuration': 'Configuración de API',
                'rate_limiting': 'Limitación de Velocidad',
                'timeout': 'Tiempo de Espera',
                'security_settings': 'Configuración de Seguridad',
                'enable_2fa': 'Habilitar 2FA',
                'require_https': 'Requerir HTTPS',
                
                // Table headers
                'transaction_id': 'ID de Transacción',
                'merchant': 'Comerciante',
                'customer': 'Cliente',
                'amount': 'Cantidad',
                'payment_method': 'Método de Pago',
                'status': 'Estado',
                'date': 'Fecha',
                'actions': 'Acciones',
                
                // Status values
                'completed': 'Completado',
                'pending': 'Pendiente',
                'failed': 'Fallido',
                'processing': 'Procesando',
                
                // Filters and buttons
                'all_statuses': 'Todos los Estados',
                'all_merchants': 'Todos los Comerciantes',
                'apply_filters': 'Aplicar Filtros',
                'new_transaction': 'Nueva Transacción',
                'add_merchant': 'Agregar Comerciante',
                'view_all': 'Ver Todo',
                'update': 'Actualizar',
                'to': 'a',
                
                // Common
                'search_transactions': 'Buscar transacciones...',
                'requests_per_minute': 'Solicitudes por minuto',
                'seconds': 'Segundos',
                'last_7_days': 'Últimos 7 días',
                'last_30_days': 'Últimos 30 días',
                'last_90_days': 'Últimos 90 días',
                'admin_user': 'Usuario Administrador',
                'years': 'años'
            },
            
            fr: {
                // Page titles and headers
                'payment_gateway_dashboard': 'Tableau de Bord de Passerelle de Paiement',
                'dashboard': 'Tableau de Bord',
                'monitor_performance': 'Surveillez les performances de votre passerelle de paiement',
                'total_revenue': 'Revenus Totaux',
                'total_transactions': 'Transactions Totales',
                'success_rate': 'Taux de Réussite',
                'active_merchants': 'Marchands Actifs',
                'transaction_volume': 'Volume de Transactions',
                'payment_methods': 'Méthodes de Paiement',
                'recent_transactions': 'Transactions Récentes',
                'revenue_trends': 'Tendances des Revenus',
                'geographic_distribution': 'Distribution Géographique',
                'fraud_detection': 'Détection de Fraude',
                'fraud_rate': 'Taux de Fraude',
                'prevented_losses': 'Pertes Évitées',
                'advanced_analytics': 'Analyses Avancées',
                
                // Navigation
                'transactions': 'Transactions',
                'merchants': 'Marchands',
                'analytics': 'Analyses',
                'security': 'Sécurité',
                'settings': 'Paramètres',
                
                // Security & Compliance
                'security_compliance': 'Sécurité et Conformité',
                'pci_dss_compliance': 'Conformité PCI DSS',
                'compliance': 'Conformité',
                'compliant': 'Conforme',
                'last_audit': 'Dernier audit',
                'next_audit': 'Prochain audit',
                'data_retention': 'Rétention des données',
                'right_to_be_forgotten': 'Droit à l\'oubli',
                'enabled': 'Activé',
                'strong_customer_auth': 'Authentification Client Forte',
                'active': 'Actif',
                'inactive': 'Inactif',
                'verified': 'Vérifié',
                'open_banking_apis': 'APIs de Banque Ouverte',
                'available': 'Disponible',
                
                // System Settings
                'system_settings': 'Paramètres Système',
                'api_configuration': 'Configuration API',
                'rate_limiting': 'Limitation de Débit',
                'timeout': 'Délai d\'Attente',
                'security_settings': 'Paramètres de Sécurité',
                'enable_2fa': 'Activer 2FA',
                'require_https': 'Exiger HTTPS',
                
                // Table headers
                'transaction_id': 'ID Transaction',
                'merchant': 'Marchand',
                'customer': 'Client',
                'amount': 'Montant',
                'payment_method': 'Méthode de Paiement',
                'status': 'Statut',
                'date': 'Date',
                'actions': 'Actions',
                
                // Status values
                'completed': 'Terminé',
                'pending': 'En Attente',
                'failed': 'Échoué',
                'processing': 'En Cours',
                
                // Filters and buttons
                'all_statuses': 'Tous les Statuts',
                'all_merchants': 'Tous les Marchands',
                'apply_filters': 'Appliquer les Filtres',
                'new_transaction': 'Nouvelle Transaction',
                'add_merchant': 'Ajouter Marchand',
                'view_all': 'Voir Tout',
                'update': 'Mettre à Jour',
                'to': 'à',
                
                // Common
                'search_transactions': 'Rechercher des transactions...',
                'requests_per_minute': 'Requêtes par minute',
                'seconds': 'Secondes',
                'last_7_days': '7 derniers jours',
                'last_30_days': '30 derniers jours',
                'last_90_days': '90 derniers jours',
                'admin_user': 'Utilisateur Admin',
                'years': 'ans'
            },
            
            de: {
                // Page titles and headers
                'payment_gateway_dashboard': 'Payment-Gateway Dashboard',
                'dashboard': 'Dashboard',
                'monitor_performance': 'Überwachen Sie die Leistung Ihres Payment-Gateways',
                'total_revenue': 'Gesamtumsatz',
                'total_transactions': 'Gesamttransaktionen',
                'success_rate': 'Erfolgsrate',
                'active_merchants': 'Aktive Händler',
                'transaction_volume': 'Transaktionsvolumen',
                'payment_methods': 'Zahlungsmethoden',
                'recent_transactions': 'Aktuelle Transaktionen',
                'revenue_trends': 'Umsatztrends',
                'geographic_distribution': 'Geografische Verteilung',
                'fraud_detection': 'Betrugserkennung',
                'fraud_rate': 'Betrugsrate',
                'prevented_losses': 'Verhinderte Verluste',
                'advanced_analytics': 'Erweiterte Analysen',
                
                // Navigation
                'transactions': 'Transaktionen',
                'merchants': 'Händler',
                'analytics': 'Analysen',
                'security': 'Sicherheit',
                'settings': 'Einstellungen',
                
                // Security & Compliance
                'security_compliance': 'Sicherheit & Compliance',
                'pci_dss_compliance': 'PCI DSS Compliance',
                'compliance': 'Compliance',
                'compliant': 'Konform',
                'last_audit': 'Letztes Audit',
                'next_audit': 'Nächstes Audit',
                'data_retention': 'Datenspeicherung',
                'right_to_be_forgotten': 'Recht auf Vergessenwerden',
                'enabled': 'Aktiviert',
                'strong_customer_auth': 'Starke Kundenauthentifizierung',
                'active': 'Aktiv',
                'inactive': 'Inaktiv',
                'verified': 'Verifiziert',
                'open_banking_apis': 'Open Banking APIs',
                'available': 'Verfügbar',
                
                // System Settings
                'system_settings': 'Systemeinstellungen',
                'api_configuration': 'API-Konfiguration',
                'rate_limiting': 'Rate Limiting',
                'timeout': 'Timeout',
                'security_settings': 'Sicherheitseinstellungen',
                'enable_2fa': '2FA Aktivieren',
                'require_https': 'HTTPS Erforderlich',
                
                // Table headers
                'transaction_id': 'Transaktions-ID',
                'merchant': 'Händler',
                'customer': 'Kunde',
                'amount': 'Betrag',
                'payment_method': 'Zahlungsmethode',
                'status': 'Status',
                'date': 'Datum',
                'actions': 'Aktionen',
                
                // Status values
                'completed': 'Abgeschlossen',
                'pending': 'Ausstehend',
                'failed': 'Fehlgeschlagen',
                'processing': 'Verarbeitung',
                
                // Filters and buttons
                'all_statuses': 'Alle Status',
                'all_merchants': 'Alle Händler',
                'apply_filters': 'Filter Anwenden',
                'new_transaction': 'Neue Transaktion',
                'add_merchant': 'Händler Hinzufügen',
                'view_all': 'Alle Anzeigen',
                'update': 'Aktualisieren',
                'to': 'bis',
                
                // Common
                'search_transactions': 'Transaktionen suchen...',
                'requests_per_minute': 'Anfragen pro Minute',
                'seconds': 'Sekunden',
                'last_7_days': 'Letzte 7 Tage',
                'last_30_days': 'Letzte 30 Tage',
                'last_90_days': 'Letzte 90 Tage',
                'admin_user': 'Admin-Benutzer',
                'years': 'Jahre'
            },
            
            it: {
                // Page titles and headers
                'payment_gateway_dashboard': 'Dashboard Gateway di Pagamento',
                'dashboard': 'Dashboard',
                'monitor_performance': 'Monitora le prestazioni del tuo gateway di pagamento',
                'total_revenue': 'Ricavi Totali',
                'total_transactions': 'Transazioni Totali',
                'success_rate': 'Tasso di Successo',
                'active_merchants': 'Commercianti Attivi',
                'transaction_volume': 'Volume Transazioni',
                'payment_methods': 'Metodi di Pagamento',
                'recent_transactions': 'Transazioni Recenti',
                'revenue_trends': 'Tendenze Ricavi',
                'geographic_distribution': 'Distribuzione Geografica',
                'fraud_detection': 'Rilevamento Frodi',
                'fraud_rate': 'Tasso di Frode',
                'prevented_losses': 'Perdite Prevenute',
                'advanced_analytics': 'Analisi Avanzate',
                
                // Navigation
                'transactions': 'Transazioni',
                'merchants': 'Commercianti',
                'analytics': 'Analisi',
                'security': 'Sicurezza',
                'settings': 'Impostazioni',
                
                // Security & Compliance
                'security_compliance': 'Sicurezza e Conformità',
                'pci_dss_compliance': 'Conformità PCI DSS',
                'compliance': 'Conformità',
                'compliant': 'Conforme',
                'last_audit': 'Ultimo audit',
                'next_audit': 'Prossimo audit',
                'data_retention': 'Conservazione dati',
                'right_to_be_forgotten': 'Diritto all\'oblio',
                'enabled': 'Abilitato',
                'strong_customer_auth': 'Autenticazione Cliente Forte',
                'active': 'Attivo',
                'inactive': 'Inattivo',
                'verified': 'Verificato',
                'open_banking_apis': 'API Open Banking',
                'available': 'Disponibile',
                
                // System Settings
                'system_settings': 'Impostazioni Sistema',
                'api_configuration': 'Configurazione API',
                'rate_limiting': 'Limitazione Velocità',
                'timeout': 'Timeout',
                'security_settings': 'Impostazioni Sicurezza',
                'enable_2fa': 'Abilita 2FA',
                'require_https': 'Richiedi HTTPS',
                
                // Table headers
                'transaction_id': 'ID Transazione',
                'merchant': 'Commerciante',
                'customer': 'Cliente',
                'amount': 'Importo',
                'payment_method': 'Metodo di Pagamento',
                'status': 'Stato',
                'date': 'Data',
                'actions': 'Azioni',
                
                // Status values
                'completed': 'Completato',
                'pending': 'In Attesa',
                'failed': 'Fallito',
                'processing': 'Elaborazione',
                
                // Filters and buttons
                'all_statuses': 'Tutti gli Stati',
                'all_merchants': 'Tutti i Commercianti',
                'apply_filters': 'Applica Filtri',
                'new_transaction': 'Nuova Transazione',
                'add_merchant': 'Aggiungi Commerciante',
                'view_all': 'Visualizza Tutto',
                'update': 'Aggiorna',
                'to': 'a',
                
                // Common
                'search_transactions': 'Cerca transazioni...',
                'requests_per_minute': 'Richieste per minuto',
                'seconds': 'Secondi',
                'last_7_days': 'Ultimi 7 giorni',
                'last_30_days': 'Ultimi 30 giorni',
                'last_90_days': 'Ultimi 90 giorni',
                'admin_user': 'Utente Admin',
                'years': 'anni'
            },
            
            pt: {
                // Page titles and headers
                'payment_gateway_dashboard': 'Painel do Gateway de Pagamento',
                'dashboard': 'Painel',
                'monitor_performance': 'Monitore o desempenho do seu gateway de pagamento',
                'total_revenue': 'Receita Total',
                'total_transactions': 'Transações Totais',
                'success_rate': 'Taxa de Sucesso',
                'active_merchants': 'Comerciantes Ativos',
                'transaction_volume': 'Volume de Transações',
                'payment_methods': 'Métodos de Pagamento',
                'recent_transactions': 'Transações Recentes',
                'revenue_trends': 'Tendências de Receita',
                'geographic_distribution': 'Distribuição Geográfica',
                'fraud_detection': 'Detecção de Fraude',
                'fraud_rate': 'Taxa de Fraude',
                'prevented_losses': 'Perdas Prevenidas',
                'advanced_analytics': 'Análises Avançadas',
                
                // Navigation
                'transactions': 'Transações',
                'merchants': 'Comerciantes',
                'analytics': 'Análises',
                'security': 'Segurança',
                'settings': 'Configurações',
                
                // Security & Compliance
                'security_compliance': 'Segurança e Conformidade',
                'pci_dss_compliance': 'Conformidade PCI DSS',
                'compliance': 'Conformidade',
                'compliant': 'Conforme',
                'last_audit': 'Última auditoria',
                'next_audit': 'Próxima auditoria',
                'data_retention': 'Retenção de dados',
                'right_to_be_forgotten': 'Direito ao esquecimento',
                'enabled': 'Habilitado',
                'strong_customer_auth': 'Autenticação Forte do Cliente',
                'active': 'Ativo',
                'inactive': 'Inativo',
                'verified': 'Verificado',
                'open_banking_apis': 'APIs Open Banking',
                'available': 'Disponível',
                
                // System Settings
                'system_settings': 'Configurações do Sistema',
                'api_configuration': 'Configuração da API',
                'rate_limiting': 'Limitação de Taxa',
                'timeout': 'Timeout',
                'security_settings': 'Configurações de Segurança',
                'enable_2fa': 'Habilitar 2FA',
                'require_https': 'Exigir HTTPS',
                
                // Table headers
                'transaction_id': 'ID da Transação',
                'merchant': 'Comerciante',
                'customer': 'Cliente',
                'amount': 'Valor',
                'payment_method': 'Método de Pagamento',
                'status': 'Status',
                'date': 'Data',
                'actions': 'Ações',
                
                // Status values
                'completed': 'Concluído',
                'pending': 'Pendente',
                'failed': 'Falhado',
                'processing': 'Processando',
                
                // Filters and buttons
                'all_statuses': 'Todos os Status',
                'all_merchants': 'Todos os Comerciantes',
                'apply_filters': 'Aplicar Filtros',
                'new_transaction': 'Nova Transação',
                'add_merchant': 'Adicionar Comerciante',
                'view_all': 'Ver Tudo',
                'update': 'Atualizar',
                'to': 'para',
                
                // Common
                'search_transactions': 'Buscar transações...',
                'requests_per_minute': 'Solicitações por minuto',
                'seconds': 'Segundos',
                'last_7_days': 'Últimos 7 dias',
                'last_30_days': 'Últimos 30 dias',
                'last_90_days': 'Últimos 90 dias',
                'admin_user': 'Usuário Admin',
                'years': 'anos'
            }
        };
    }

    // Get translation for a key
    t(key, params = {}) {
        let translation = this.translations[this.currentLanguage]?.[key] || 
                         this.translations[this.fallbackLanguage]?.[key] || 
                         key;
        
        // Replace parameters in translation
        Object.keys(params).forEach(param => {
            translation = translation.replace(`{{${param}}}`, params[param]);
        });
        
        return translation;
    }

    // Set current language
    setLanguage(language) {
        if (this.translations[language]) {
            this.currentLanguage = language;
            this.updateUI();
            // Save to localStorage
            localStorage.setItem('paygateway_language', language);
            // Notify backend
            this.notifyBackend(language);
        }
    }

    // Get current language
    getCurrentLanguage() {
        return this.currentLanguage;
    }

    // Get available languages
    getAvailableLanguages() {
        return {
            'en': 'English',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch',
            'it': 'Italiano',
            'pt': 'Português'
        };
    }

     // Initialize language from localStorage or default to English
    initLanguage() {
        // Always default to English first
        const savedLanguage = localStorage.getItem('digipay_language') || 'en';
        
        // Ensure we have a valid language
        if (this.translations[savedLanguage]) {
            this.currentLanguage = savedLanguage;
        } else {
            this.currentLanguage = 'en'; // Force English as fallback
        }
        
        this.applyTranslations();
        
        // Update language selector if it exists
        const languageSelect = document.getElementById('languageSelect');
        if (languageSelect) {
            languageSelect.value = this.currentLanguage;
        }
    }

    // Update UI with current language
    updateUI() {
        // Update all elements with data-translate attribute
        document.querySelectorAll('[data-translate]').forEach(element => {
            const key = element.getAttribute('data-translate');
            element.textContent = this.t(key);
        });

        // Update placeholders
        document.querySelectorAll('[data-translate-placeholder]').forEach(element => {
            const key = element.getAttribute('data-translate-placeholder');
            element.placeholder = this.t(key);
        });

        // Update titles
        document.querySelectorAll('[data-translate-title]').forEach(element => {
            const key = element.getAttribute('data-translate-title');
            element.title = this.t(key);
        });

        // Update select options
        document.querySelectorAll('option[data-translate]').forEach(element => {
            const key = element.getAttribute('data-translate');
            element.textContent = this.t(key);
        });

        // Update page title
        const titleElement = document.querySelector('title[data-translate]');
        if (titleElement) {
            const key = titleElement.getAttribute('data-translate');
            titleElement.textContent = this.t(key);
        }
    }

    // Notify backend of language change
    async notifyBackend(language) {
        try {
            await fetch('/api/set-language', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ language: language })
            });
        } catch (error) {
            console.error('Failed to notify backend of language change:', error);
        }
    }
}

// Global translator instance
window.translator = new Translator();

