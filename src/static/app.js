// Global variables
let currentPage = 'dashboard';
let currentTransactions = [];
let transactionChart = null;
let paymentMethodChart = null;
let revenueChart = null;
let geoChart = null;

// API base URL
const API_BASE = '/api';

// Language change function
function changeLanguage(language) {
    if (window.translator) {
        window.translator.setLanguage(language);
        // Update charts and dynamic content
        updateDashboardContent();
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Force English as default language
    localStorage.setItem('digipay_language', 'en');
    
    // Initialize translator
    if (window.translator) {
        window.translator.currentLanguage = 'en'; // Force English
        window.translator.initLanguage();
        
        // Set language selector to English
        const languageSelect = document.getElementById('languageSelect');
        if (languageSelect) {
            languageSelect.value = 'en';
        }
    }
    
    initializeApp();
    loadDashboardData();
    setupEventListeners();
});

function initializeApp() {
    // Initialize charts
    initializeCharts();
    
    // Load initial data
    loadStats();
    loadRecentTransactions();
}

function setupEventListeners() {
    // Sidebar navigation
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.dataset.page;
            if (page) {
                showPage(page);
            }
        });
    });
    
    // Modal close
    const modalOverlay = document.getElementById('modal-overlay');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
    }
    
    // Chart period change
    const chartPeriod = document.getElementById('chart-period');
    if (chartPeriod) {
        chartPeriod.addEventListener('change', function() {
            updateTransactionChart(this.value);
        });
    }
}

function showPage(pageName) {
    // Update sidebar active state
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    const activeMenuItem = document.querySelector(`[data-page="${pageName}"]`);
    if (activeMenuItem) {
        activeMenuItem.classList.add('active');
    }
    
    // Update page content
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    const targetPage = document.getElementById(`${pageName}-page`);
    if (targetPage) {
        targetPage.classList.add('active');
    }
    
    // Update header
    updatePageHeader(pageName);
    
    // Load page-specific data
    loadPageData(pageName);
    
    currentPage = pageName;
}

function updatePageHeader(pageName) {
    const titles = {
        dashboard: 'Dashboard',
        transactions: 'Transactions',
        merchants: 'Merchants',
        analytics: 'Analytics',
        security: 'Security & Compliance',
        settings: 'Settings'
    };
    
    const subtitles = {
        dashboard: 'Monitor your payment gateway performance',
        transactions: 'View and manage all payment transactions',
        merchants: 'Manage merchant accounts and settings',
        analytics: 'Advanced analytics and reporting',
        security: 'Security status and compliance monitoring',
        settings: 'System configuration and preferences'
    };
    
    const titleElement = document.getElementById('page-title');
    const subtitleElement = document.getElementById('page-subtitle');
    
    if (titleElement) titleElement.textContent = titles[pageName] || 'Dashboard';
    if (subtitleElement) subtitleElement.textContent = subtitles[pageName] || '';
}

function loadPageData(pageName) {
    switch(pageName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'transactions':
            loadTransactions();
            break;
        case 'merchants':
            loadMerchants();
            break;
        case 'analytics':
            loadAnalytics();
            break;
        case 'security':
            loadSecurityData();
            break;
        case 'settings':
            loadSettings();
            break;
    }
}

function updateDashboardContent() {
    // Update dashboard content when language changes
    loadDashboardData();
}

// Dashboard functions
function loadDashboardData() {
    loadStats();
    loadRecentTransactions();
    updateTransactionChart('7d');
    updatePaymentMethodChart();
}

async function loadStats() {
    try {
        // Simulate API calls for demo
        const stats = {
            totalRevenue: 125430.50,
            totalTransactions: 1247,
            successRate: 98.2,
            activeMerchants: 23
        };
        
        document.getElementById('total-revenue').textContent = `€${stats.totalRevenue.toLocaleString()}`;
        document.getElementById('total-transactions').textContent = stats.totalTransactions.toLocaleString();
        document.getElementById('success-rate').textContent = `${stats.successRate}%`;
        document.getElementById('active-merchants').textContent = stats.activeMerchants;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadRecentTransactions() {
    try {
        const response = await fetch(`${API_BASE}/payments?limit=5`);
        const transactions = await response.json();
        
        const tbody = document.getElementById('recent-transactions-body');
        tbody.innerHTML = '';
        
        if (transactions.length === 0) {
            // Show demo data if no real transactions
            const demoTransactions = [
                {
                    transaction_id: 'txn_demo_001',
                    merchant_id: 'merchant_demo_001',
                    amount: 99.99,
                    status: 'completed',
                    created_at: new Date().toISOString()
                },
                {
                    transaction_id: 'txn_demo_002',
                    merchant_id: 'merchant_demo_002',
                    amount: 249.50,
                    status: 'pending',
                    created_at: new Date(Date.now() - 3600000).toISOString()
                }
            ];
            
            demoTransactions.forEach(transaction => {
                const row = createTransactionRow(transaction);
                tbody.appendChild(row);
            });
        } else {
            transactions.forEach(transaction => {
                const row = createTransactionRow(transaction);
                tbody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading recent transactions:', error);
        showDemoTransactions();
    }
}

function showDemoTransactions() {
    const demoTransactions = [
        {
            transaction_id: 'txn_demo_001',
            merchant_id: 'merchant_demo_001',
            amount: 99.99,
            status: 'completed',
            created_at: new Date().toISOString()
        },
        {
            transaction_id: 'txn_demo_002',
            merchant_id: 'merchant_demo_002',
            amount: 249.50,
            status: 'pending',
            created_at: new Date(Date.now() - 3600000).toISOString()
        },
        {
            transaction_id: 'txn_demo_003',
            merchant_id: 'merchant_demo_001',
            amount: 75.25,
            status: 'completed',
            created_at: new Date(Date.now() - 7200000).toISOString()
        }
    ];
    
    const tbody = document.getElementById('recent-transactions-body');
    tbody.innerHTML = '';
    
    demoTransactions.forEach(transaction => {
        const row = createTransactionRow(transaction);
        tbody.appendChild(row);
    });
}

function createTransactionRow(transaction) {
    const row = document.createElement('tr');
    
    const statusClass = getStatusClass(transaction.status);
    const formattedDate = new Date(transaction.created_at).toLocaleDateString();
    
    row.innerHTML = `
        <td><code>${transaction.transaction_id}</code></td>
        <td>${transaction.merchant_id}</td>
        <td>€${transaction.amount}</td>
        <td><span class="status-badge ${statusClass}">${transaction.status}</span></td>
        <td>${formattedDate}</td>
        <td>
            <button class="btn btn-secondary" onclick="viewTransaction('${transaction.transaction_id}')">
                <i class="fas fa-eye"></i>
            </button>
        </td>
    `;
    
    return row;
}

function getStatusClass(status) {
    switch(status) {
        case 'completed': return 'success';
        case 'pending': return 'pending';
        case 'failed': return 'failed';
        default: return 'pending';
    }
}

// Chart functions
function initializeCharts() {
    // Transaction Chart
    const transactionCtx = document.getElementById('transactionChart').getContext('2d');
    transactionChart = new Chart(transactionCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Transaction Volume',
                data: [],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#f1f5f9'
                    }
                },
                x: {
                    grid: {
                        color: '#f1f5f9'
                    }
                }
            }
        }
    });
    
    // Payment Method Chart
    const paymentMethodCtx = document.getElementById('paymentMethodChart').getContext('2d');
    paymentMethodChart = new Chart(paymentMethodCtx, {
        type: 'doughnut',
        data: {
            labels: ['Credit Card', 'Debit Card', 'Bank Transfer', 'Digital Wallet'],
            datasets: [{
                data: [45, 30, 15, 10],
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#fbbf24',
                    '#10b981'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function updateTransactionChart(period) {
    // Generate demo data based on period
    const data = generateChartData(period);
    
    transactionChart.data.labels = data.labels;
    transactionChart.data.datasets[0].data = data.values;
    transactionChart.update();
}

function updatePaymentMethodChart() {
    // Demo data for payment methods
    const data = [45, 30, 15, 10];
    paymentMethodChart.data.datasets[0].data = data;
    paymentMethodChart.update();
}

function generateChartData(period) {
    const now = new Date();
    const labels = [];
    const values = [];
    
    let days;
    switch(period) {
        case '7d': days = 7; break;
        case '30d': days = 30; break;
        case '90d': days = 90; break;
        default: days = 7;
    }
    
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        
        if (days <= 7) {
            labels.push(date.toLocaleDateString('en-US', { weekday: 'short' }));
        } else if (days <= 30) {
            labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        } else {
            labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        }
        
        // Generate random transaction volume
        values.push(Math.floor(Math.random() * 100) + 20);
    }
    
    return { labels, values };
}

// Transaction functions
async function loadTransactions() {
    try {
        const response = await fetch(`${API_BASE}/payments`);
        const transactions = await response.json();
        
        const tbody = document.getElementById('transactions-body');
        tbody.innerHTML = '';
        
        if (transactions.length === 0) {
            showDemoTransactionsTable();
        } else {
            transactions.forEach(transaction => {
                const row = createFullTransactionRow(transaction);
                tbody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading transactions:', error);
        showDemoTransactionsTable();
    }
}

function showDemoTransactionsTable() {
    const demoTransactions = [
        {
            transaction_id: 'txn_demo_001',
            merchant_id: 'merchant_demo_001',
            customer_email: 'customer@example.com',
            amount: 99.99,
            payment_method: 'credit_card',
            status: 'completed',
            created_at: new Date().toISOString()
        },
        {
            transaction_id: 'txn_demo_002',
            merchant_id: 'merchant_demo_002',
            customer_email: 'user@test.com',
            amount: 249.50,
            payment_method: 'debit_card',
            status: 'pending',
            created_at: new Date(Date.now() - 3600000).toISOString()
        },
        {
            transaction_id: 'txn_demo_003',
            merchant_id: 'merchant_demo_001',
            customer_email: 'buyer@shop.com',
            amount: 75.25,
            payment_method: 'digital_wallet',
            status: 'completed',
            created_at: new Date(Date.now() - 7200000).toISOString()
        }
    ];
    
    const tbody = document.getElementById('transactions-body');
    tbody.innerHTML = '';
    
    demoTransactions.forEach(transaction => {
        const row = createFullTransactionRow(transaction);
        tbody.appendChild(row);
    });
}

function createFullTransactionRow(transaction) {
    const row = document.createElement('tr');
    
    const statusClass = getStatusClass(transaction.status);
    const formattedDate = new Date(transaction.created_at).toLocaleDateString();
    const paymentMethod = formatPaymentMethod(transaction.payment_method);
    
    row.innerHTML = `
        <td><code>${transaction.transaction_id}</code></td>
        <td>${transaction.merchant_id}</td>
        <td>${transaction.customer_email || 'N/A'}</td>
        <td>€${transaction.amount}</td>
        <td>${paymentMethod}</td>
        <td><span class="status-badge ${statusClass}">${transaction.status}</span></td>
        <td>${formattedDate}</td>
        <td>
            <button class="btn btn-secondary" onclick="viewTransaction('${transaction.transaction_id}')">
                <i class="fas fa-eye"></i>
            </button>
            ${transaction.status === 'completed' ? 
                `<button class="btn btn-danger" onclick="refundTransaction('${transaction.transaction_id}')">
                    <i class="fas fa-undo"></i>
                </button>` : ''
            }
        </td>
    `;
    
    return row;
}

function formatPaymentMethod(method) {
    const methods = {
        'credit_card': 'Credit Card',
        'debit_card': 'Debit Card',
        'bank_transfer': 'Bank Transfer',
        'digital_wallet': 'Digital Wallet'
    };
    return methods[method] || method;
}

// Merchant functions
async function loadMerchants() {
    try {
        const response = await fetch(`${API_BASE}/merchants`);
        const merchants = await response.json();
        
        const grid = document.getElementById('merchants-grid');
        grid.innerHTML = '';
        
        if (merchants.length === 0) {
            showDemoMerchants();
        } else {
            merchants.forEach(merchant => {
                const card = createMerchantCard(merchant);
                grid.appendChild(card);
            });
        }
    } catch (error) {
        console.error('Error loading merchants:', error);
        showDemoMerchants();
    }
}

function showDemoMerchants() {
    const demoMerchants = [
        {
            merchant_id: 'merchant_demo_001',
            business_name: 'Demo Store',
            contact_email: 'contact@demostore.com',
            business_type: 'E-commerce',
            country: 'DE',
            is_active: true,
            is_verified: true
        },
        {
            merchant_id: 'merchant_demo_002',
            business_name: 'Test Shop',
            contact_email: 'info@testshop.com',
            business_type: 'Retail',
            country: 'FR',
            is_active: true,
            is_verified: false
        }
    ];
    
    const grid = document.getElementById('merchants-grid');
    grid.innerHTML = '';
    
    demoMerchants.forEach(merchant => {
        const card = createMerchantCard(merchant);
        grid.appendChild(card);
    });
}

function createMerchantCard(merchant) {
    const card = document.createElement('div');
    card.className = 'merchant-card';
    
    const statusClass = merchant.is_active ? 'success' : 'failed';
    const verifiedClass = merchant.is_verified ? 'success' : 'warning';
    
    card.innerHTML = `
        <div class="merchant-header">
            <div class="merchant-info">
                <h4>${merchant.business_name}</h4>
                <p>${merchant.contact_email}</p>
                <p>${merchant.business_type} • ${merchant.country}</p>
            </div>
            <div class="merchant-status">
                <span class="status-badge ${statusClass}">${merchant.is_active ? 'Active' : 'Inactive'}</span>
                <span class="status-badge ${verifiedClass}">${merchant.is_verified ? 'Verified' : 'Pending'}</span>
            </div>
        </div>
        <div class="merchant-stats">
            <div class="merchant-stat">
                <div class="number">€${(Math.random() * 10000).toFixed(0)}</div>
                <div class="label">Monthly Volume</div>
            </div>
            <div class="merchant-stat">
                <div class="number">${Math.floor(Math.random() * 100)}</div>
                <div class="label">Transactions</div>
            </div>
        </div>
        <div class="merchant-actions" style="margin-top: 1rem;">
            <button class="btn btn-secondary" onclick="editMerchant('${merchant.merchant_id}')">
                <i class="fas fa-edit"></i> Edit
            </button>
            <button class="btn btn-primary" onclick="viewMerchantDetails('${merchant.merchant_id}')">
                <i class="fas fa-eye"></i> View
            </button>
        </div>
    `;
    
    return card;
}

// Analytics functions
function loadAnalytics() {
    initializeAnalyticsCharts();
}

function initializeAnalyticsCharts() {
    // Revenue Chart
    const revenueCtx = document.getElementById('revenueChart');
    if (revenueCtx) {
        revenueChart = new Chart(revenueCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Revenue',
                    data: [12000, 15000, 18000, 14000, 22000, 25000],
                    backgroundColor: '#667eea'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
    
    // Geographic Chart
    const geoCtx = document.getElementById('geoChart');
    if (geoCtx) {
        geoChart = new Chart(geoCtx.getContext('2d'), {
            type: 'pie',
            data: {
                labels: ['Germany', 'France', 'Spain', 'Italy', 'Others'],
                datasets: [{
                    data: [35, 25, 15, 15, 10],
                    backgroundColor: ['#667eea', '#764ba2', '#fbbf24', '#10b981', '#f59e0b']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}

// Security functions
function loadSecurityData() {
    // Security data is mostly static for demo
    console.log('Security data loaded');
}

// Settings functions
function loadSettings() {
    // Settings are mostly static for demo
    console.log('Settings loaded');
}

// Modal functions
function showModal(title, content) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = content;
    document.getElementById('modal-overlay').classList.add('active');
}

function closeModal() {
    document.getElementById('modal-overlay').classList.remove('active');
}

function showCreateTransactionModal() {
    const content = `
        <form onsubmit="createTransaction(event)">
            <div class="form-group">
                <label>Merchant ID</label>
                <input type="text" name="merchant_id" required placeholder="merchant_123">
            </div>
            <div class="form-group">
                <label>Amount (EUR)</label>
                <input type="number" name="amount" step="0.01" required placeholder="99.99">
            </div>
            <div class="form-group">
                <label>Currency</label>
                <select name="currency" required>
                    <option value="EUR">EUR</option>
                    <option value="USD">USD</option>
                    <option value="GBP">GBP</option>
                </select>
            </div>
            <div class="form-group">
                <label>Payment Method</label>
                <select name="payment_method" required>
                    <option value="credit_card">Credit Card</option>
                    <option value="debit_card">Debit Card</option>
                    <option value="bank_transfer">Bank Transfer</option>
                    <option value="digital_wallet">Digital Wallet</option>
                </select>
            </div>
            <div class="form-group">
                <label>Customer Email</label>
                <input type="email" name="customer_email" placeholder="customer@example.com">
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea name="description" placeholder="Payment description"></textarea>
            </div>
            <div class="form-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Create Transaction</button>
            </div>
        </form>
    `;
    
    showModal('Create New Transaction', content);
}

function showCreateMerchantModal() {
    const content = `
        <form onsubmit="createMerchant(event)">
            <div class="form-group">
                <label>Business Name</label>
                <input type="text" name="business_name" required placeholder="My Business">
            </div>
            <div class="form-group">
                <label>Contact Email</label>
                <input type="email" name="contact_email" required placeholder="contact@business.com">
            </div>
            <div class="form-group">
                <label>Business Type</label>
                <select name="business_type" required>
                    <option value="E-commerce">E-commerce</option>
                    <option value="Retail">Retail</option>
                    <option value="Services">Services</option>
                    <option value="SaaS">SaaS</option>
                </select>
            </div>
            <div class="form-group">
                <label>Country</label>
                <select name="country" required>
                    <option value="DE">Germany</option>
                    <option value="FR">France</option>
                    <option value="ES">Spain</option>
                    <option value="IT">Italy</option>
                    <option value="NL">Netherlands</option>
                </select>
            </div>
            <div class="form-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Create Merchant</button>
            </div>
        </form>
    `;
    
    showModal('Add New Merchant', content);
}

// API functions
async function createTransaction(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch(`${API_BASE}/payments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const transaction = await response.json();
            alert('Transaction created successfully!');
            closeModal();
            if (currentPage === 'transactions') {
                loadTransactions();
            }
            loadRecentTransactions();
        } else {
            const error = await response.json();
            alert(`Error: ${error.error}`);
        }
    } catch (error) {
        console.error('Error creating transaction:', error);
        alert('Error creating transaction. Please try again.');
    }
}

async function createMerchant(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch(`${API_BASE}/merchants`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const merchant = await response.json();
            alert('Merchant created successfully!');
            closeModal();
            if (currentPage === 'merchants') {
                loadMerchants();
            }
        } else {
            const error = await response.json();
            alert(`Error: ${error.error}`);
        }
    } catch (error) {
        console.error('Error creating merchant:', error);
        alert('Error creating merchant. Please try again.');
    }
}

function viewTransaction(transactionId) {
    alert(`Viewing transaction: ${transactionId}`);
}

function refundTransaction(transactionId) {
    if (confirm(`Are you sure you want to refund transaction ${transactionId}?`)) {
        alert(`Refund initiated for transaction: ${transactionId}`);
    }
}

function editMerchant(merchantId) {
    alert(`Editing merchant: ${merchantId}`);
}

function viewMerchantDetails(merchantId) {
    alert(`Viewing merchant details: ${merchantId}`);
}

function applyFilters() {
    alert('Filters applied');
    loadTransactions();
}

function updateAnalytics() {
    alert('Analytics updated');
    loadAnalytics();
}



// Billing Management Functions
function loadBillingData() {
    loadTotalRevenue();
    loadRecentInvoices();
    loadRevenueCharts();
}

async function loadTotalRevenue() {
    try {
        const response = await fetch(`${API_BASE}/billing/revenue/total?period=month`);
        const data = await response.json();
        
        if (data.success) {
            const revenue = data.data;
            document.getElementById('total-platform-revenue').textContent = `€${revenue.total_revenue.toFixed(2)}`;
            document.getElementById('monthly-revenue').textContent = `€${revenue.total_revenue.toFixed(2)}`;
            
            if (revenue.total_transactions > 0) {
                const avgFee = revenue.total_revenue / revenue.total_transactions;
                document.getElementById('average-fee-per-transaction').textContent = `€${avgFee.toFixed(2)}`;
            }
        }
    } catch (error) {
        console.error('Error loading revenue data:', error);
    }
}

async function loadRecentInvoices() {
    try {
        // For now, we'll show sample data since we need merchant data
        const sampleInvoices = [
            {
                invoice_number: 'INV-20250116-ABC123',
                merchant_id: 'MERCHANT001',
                total_amount: 125.50,
                status: 'pending',
                due_date: '2025-02-15'
            },
            {
                invoice_number: 'INV-20250115-DEF456',
                merchant_id: 'MERCHANT002',
                total_amount: 89.25,
                status: 'paid',
                due_date: '2025-02-14'
            }
        ];
        
        const tbody = document.getElementById('recent-invoices-body');
        tbody.innerHTML = '';
        
        sampleInvoices.forEach(invoice => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${invoice.invoice_number}</td>
                <td>${invoice.merchant_id}</td>
                <td>€${invoice.total_amount.toFixed(2)}</td>
                <td><span class="status ${invoice.status}">${invoice.status}</span></td>
                <td>${invoice.due_date}</td>
                <td>
                    <button class="btn btn-sm" onclick="viewInvoice('${invoice.invoice_number}')">View</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading recent invoices:', error);
    }
}

function loadRevenueCharts() {
    // Revenue Breakdown Chart
    const revenueCtx = document.getElementById('revenueBreakdownChart');
    if (revenueCtx) {
        new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Transaction Fees',
                    data: [1200, 1350, 1100, 1400, 1600, 1750],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Other Fees',
                    data: [200, 180, 220, 190, 210, 240],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '€' + value;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Fee Distribution Chart
    const feeCtx = document.getElementById('feeDistributionChart');
    if (feeCtx) {
        new Chart(feeCtx, {
            type: 'doughnut',
            data: {
                labels: ['European Cards', 'Non-European Cards', 'Chargeback Fees', 'Refund Fees'],
                datasets: [{
                    data: [65, 25, 8, 2],
                    backgroundColor: [
                        '#3b82f6',
                        '#10b981',
                        '#f59e0b',
                        '#ef4444'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    }
}

// Fee Calculator Functions
async function calculateFee() {
    const amount = parseFloat(document.getElementById('calc-amount').value);
    const isEuropeanCard = document.getElementById('calc-card-type').value === 'true';
    const merchantId = document.getElementById('calc-merchant').value;
    
    if (!amount || amount <= 0) {
        alert('Please enter a valid transaction amount');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/billing/fee-calculator`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                amount: amount,
                is_european_card: isEuropeanCard,
                merchant_id: merchantId || null
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const result = data.data;
            document.getElementById('result-amount').textContent = `€${result.amount.toFixed(2)}`;
            document.getElementById('result-fee').textContent = `€${result.fee.toFixed(2)}`;
            document.getElementById('result-net').textContent = `€${result.net_amount.toFixed(2)}`;
            document.getElementById('calculation-result').style.display = 'block';
        } else {
            alert('Error calculating fee: ' + data.error);
        }
    } catch (error) {
        console.error('Error calculating fee:', error);
        alert('Error calculating fee. Please try again.');
    }
}

// Billing Configuration Functions
function showBillingConfigModal() {
    document.getElementById('billing-config-modal').style.display = 'flex';
    loadBillingConfig();
}

function closeBillingConfigModal() {
    document.getElementById('billing-config-modal').style.display = 'none';
}

async function loadBillingConfig() {
    // Load default configuration
    document.getElementById('config-eu-percentage').value = '0.5';
    document.getElementById('config-eu-fixed').value = '0.10';
    document.getElementById('config-non-eu-percentage').value = '2.4';
    document.getElementById('config-non-eu-fixed').value = '0.20';
    document.getElementById('config-chargeback-fee').value = '9.00';
    document.getElementById('config-refund-fee').value = '0.05';
    document.getElementById('config-billing-cycle').value = 'monthly';
    document.getElementById('config-auto-billing').checked = true;
}

// Invoice Management Functions
function viewInvoice(invoiceNumber) {
    openModal('Invoice Details', `Viewing invoice: ${invoiceNumber}`);
}

async function generateAllInvoices() {
    if (confirm('Generate invoices for all merchants with pending fees?')) {
        try {
            // This would call the backend to generate invoices
            alert('Invoice generation started. This may take a few minutes.');
            loadRecentInvoices(); // Refresh the invoice list
        } catch (error) {
            console.error('Error generating invoices:', error);
            alert('Error generating invoices. Please try again.');
        }
    }
}

// Revenue Analytics Functions
function updateRevenueAnalytics() {
    const startDate = document.getElementById('revenue-start-date').value;
    const endDate = document.getElementById('revenue-end-date').value;
    
    if (!startDate || !endDate) {
        alert('Please select both start and end dates');
        return;
    }
    
    loadRevenueAnalytics(startDate, endDate);
}

async function loadRevenueAnalytics(startDate, endDate) {
    try {
        const response = await fetch(`${API_BASE}/billing/revenue/total?period=custom&start_date=${startDate}&end_date=${endDate}`);
        const data = await response.json();
        
        if (data.success) {
            const revenue = data.data;
            document.getElementById('transaction-fees-total').textContent = `€${revenue.transaction_fees.toFixed(2)}`;
            document.getElementById('european-fees').textContent = `€${(revenue.transaction_fees * 0.7).toFixed(2)}`;
            document.getElementById('non-european-fees').textContent = `€${(revenue.transaction_fees * 0.3).toFixed(2)}`;
            document.getElementById('other-fees-total').textContent = `€${(revenue.chargeback_fees + revenue.refund_fees).toFixed(2)}`;
            document.getElementById('chargeback-fees').textContent = `€${revenue.chargeback_fees.toFixed(2)}`;
            document.getElementById('refund-fees').textContent = `€${revenue.refund_fees.toFixed(2)}`;
            document.getElementById('active-merchants-count').textContent = revenue.active_merchants;
            
            if (revenue.active_merchants > 0) {
                const avgRevenue = revenue.total_revenue / revenue.active_merchants;
                document.getElementById('avg-revenue-per-merchant').textContent = `€${avgRevenue.toFixed(2)}`;
            }
        }
    } catch (error) {
        console.error('Error loading revenue analytics:', error);
    }
}

// Update the showPage function to handle billing pages
const originalShowPage = showPage;
function showPage(pageId) {
    originalShowPage(pageId);
    
    // Load specific data for billing pages
    if (pageId === 'billing') {
        loadBillingData();
    } else if (pageId === 'fee-calculator') {
        loadMerchantOptions();
    } else if (pageId === 'revenue') {
        // Set default date range to current month
        const now = new Date();
        const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
        document.getElementById('revenue-start-date').value = firstDay.toISOString().split('T')[0];
        document.getElementById('revenue-end-date').value = now.toISOString().split('T')[0];
        loadRevenueAnalytics(firstDay.toISOString().split('T')[0], now.toISOString().split('T')[0]);
    }
}

async function loadMerchantOptions() {
    try {
        // Load merchants for the fee calculator
        const response = await fetch(`${API_BASE}/merchants`);
        const data = await response.json();
        
        if (data.success) {
            const select = document.getElementById('calc-merchant');
            // Clear existing options except the first one
            while (select.children.length > 1) {
                select.removeChild(select.lastChild);
            }
            
            data.data.forEach(merchant => {
                const option = document.createElement('option');
                option.value = merchant.merchant_id;
                option.textContent = `${merchant.business_name} (${merchant.merchant_id})`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading merchants:', error);
    }
}

// Billing form submission
document.addEventListener('DOMContentLoaded', function() {
    const billingForm = document.getElementById('billing-config-form');
    if (billingForm) {
        billingForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const config = {
                european_card_percentage: parseFloat(document.getElementById('config-eu-percentage').value),
                european_card_fixed_fee: parseFloat(document.getElementById('config-eu-fixed').value),
                non_european_card_percentage: parseFloat(document.getElementById('config-non-eu-percentage').value),
                non_european_card_fixed_fee: parseFloat(document.getElementById('config-non-eu-fixed').value),
                chargeback_fee: parseFloat(document.getElementById('config-chargeback-fee').value),
                refund_fee: parseFloat(document.getElementById('config-refund-fee').value),
                auto_billing_enabled: document.getElementById('config-auto-billing').checked
            };
            
            try {
                // This would save the configuration to the backend
                alert('Billing configuration saved successfully!');
                closeBillingConfigModal();
            } catch (error) {
                console.error('Error saving billing configuration:', error);
                alert('Error saving configuration. Please try again.');
            }
        });
    }
});

