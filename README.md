# 💰 Bank Statement Analyzer - Enterprise Edition

A comprehensive, multi-user financial analysis platform with advanced features including user management, persistent data storage, subscription tracking, receipt scanning, SMS alerts, and professional reporting.

## 🌟 Enterprise Features

### 🔐 User Management & Security
- **Multi-user support** with role-based access control
- **Secure authentication** with bcrypt password hashing
- **Admin dashboard** for user and system management
- **User-specific data isolation** - each user has private data storage
- **Test user mode** for safe feature testing without data pollution

### 💾 Persistent Data Storage
- **Automatic data persistence** for all users (except test user)
- **User-specific file storage** - each user's data saved separately
- **Session persistence** across app restarts
- **Admin data management** with system-wide controls
- **Data backup and restore** capabilities

### ⚡ Quick Expense Management
- **Instant expense entry** with 19+ predefined categories
- **Auto-date functionality** for quick daily expense tracking
- **Real-time integration** into all charts and reports
- **Bulk expense management** with edit/delete capabilities

### 🛒 Advanced Grocery Tracking
- **Receipt OCR scanning** with automatic text extraction
- **Item categorization** (Snacks, Dairy & Milk, Vegetables, etc.)
- **Year-to-Date spending** tracking by grocery category
- **Mobile-friendly** receipt upload for on-the-go tracking

### 📋 Subscription & Bill Management
- **Manual subscription entry** with due date tracking
- **SMS alert system** via Twilio API (1-day advance notice)
- **Recurring payment calendar** visualization
- **Payment history tracking** and analytics

### 📊 Professional Analytics & Reporting
- **Interactive charts** with zoom, pan, and hover details
- **PDF reports** with embedded visualizations
- **Excel exports** with multi-sheet analysis
- **YTD breakdowns** by category and type
- **Financial health insights** and recommendations

## 🚀 Getting Started

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/chanvekse/Finance-AI-Analyzer.git
cd Finance-AI-Analyzer

# Install core dependencies
pip install -r requirements.txt

# Optional: Install OCR dependencies for receipt scanning
pip install -r requirements-ocr.txt
```

### 2. Launch the Application

```bash
streamlit run app.py
```

### 3. Login & First Time Setup

Navigate to `http://localhost:8501` and login with:

#### 👑 Admin Account (Full Access)
- **Username:** `admin`
- **Password:** `admin123`
- **Features:** User management, system administration, persistent data

#### 🧪 Test Account (Safe Testing)
- **Username:** `test`
- **Password:** `test123`
- **Features:** All functionality, data clears on logout

## 📦 Dependencies

### Core Requirements (required)
```txt
pandas>=1.5.0          # Data processing and analysis
matplotlib>=3.5.0      # Static chart generation
seaborn>=0.11.0         # Statistical visualizations
numpy>=1.21.0           # Numerical computations
fpdf2>=2.7.0           # PDF report generation
streamlit>=1.28.0      # Web application framework
plotly>=5.15.0         # Interactive charts
openpyxl>=3.0.0        # Excel export functionality
twilio>=8.5.0          # SMS notifications
bcrypt>=4.0.0          # Secure password hashing
```

### Optional OCR Requirements (for receipt scanning)
```txt
pytesseract>=0.3.10    # OCR text extraction
opencv-python>=4.8.0   # Image preprocessing
pillow>=9.0.0          # Image handling
```

**Tesseract OCR Installation:**
- **Windows:** Download from [Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS:** `brew install tesseract`
- **Ubuntu/Debian:** `sudo apt install tesseract-ocr`

## 🎯 User Guide

### 💾 Admin Users
1. **Create new users** through User Management in sidebar
2. **Manage system data** with admin-only controls
3. **Monitor user activity** and data usage
4. **Reset system** or clear individual user data
5. **All data persists permanently** across sessions

### 🧪 Test Users
1. **Safely test all features** without affecting real data
2. **Add sample expenses** and subscriptions
3. **Try receipt scanning** and SMS alerts
4. **Export test reports** in PDF/Excel
5. **Data automatically clears** on logout

### 👥 Regular Users
1. **Auto-persistence enabled** - data saves permanently
2. **Private data storage** - isolated from other users
3. **Full feature access** except admin functions
4. **Seamless login experience** with data auto-loading

## 🔧 Core Features

### ⚡ Quick Expense Entry
- **Top-priority placement** for immediate access
- **19 expense categories:** Groceries, Dining, Transportation, etc.
- **Auto-date to today** for rapid entry
- **Amount and notes** fields with validation
- **Instant integration** into all reports and charts

### 📊 Financial Analytics
- **Category spending charts** with interactive hover data
- **Monthly trends** showing income, expenses, savings rate
- **YTD breakdowns** by category and spending type
- **Financial health scoring** with personalized insights

### 🛒 Grocery Management
- **Receipt upload** with OCR text extraction
- **Manual item entry** with auto-categorization
- **Category tracking:** Snacks, Dairy, Vegetables, etc.
- **YTD spending analysis** by grocery category
- **Mobile-friendly interface** for phone uploads

### 📋 Subscription Tracking
- **Manual subscription entry** with service name, amount, due date
- **SMS alerts** 1 day before due date (Twilio integration)
- **Next due date calculation** with automatic scheduling
- **Payment history** and recurring expense analysis

### 📄 Professional Reporting
- **PDF reports** with financial summary and embedded charts
- **Excel exports** with multiple analysis sheets
- **Custom date filtering** for specific time periods
- **Professional formatting** suitable for business use

## 📱 Mobile & Upload Features

### Mobile Receipt Scanning
1. **Take photo** of grocery receipt on mobile device
2. **Upload via web interface** (works on mobile browsers)
3. **Automatic OCR extraction** of items and prices
4. **Manual review and editing** of extracted data
5. **Instant categorization** and YTD tracking

### Mobile Expense Entry
1. **Responsive design** works on all devices
2. **Quick expense entry** optimized for mobile
3. **Touch-friendly interface** with large buttons
4. **Auto-date functionality** for on-the-go tracking

### Offline Capabilities
- **See [MOBILE_APP_GUIDE.md](MOBILE_APP_GUIDE.md)** for complete mobile deployment guide
- **PWA conversion** instructions for offline use
- **Native app development** with Kivy/KivyMD
- **SQLite offline storage** implementation

## 🗃️ Data Management

### File Structure
```
user_data/
├── users.json                          # User credentials (secure)
├── admin_settings.json                 # Admin preferences
├── admin_manual_expenses.json         # Admin's expenses
├── admin_manual_subscriptions.json    # Admin's subscriptions
├── admin_grocery_items.json           # Admin's grocery data
├── [user]_manual_expenses.json        # User-specific expenses
├── [user]_manual_subscriptions.json   # User-specific subscriptions
└── [user]_grocery_items.json          # User-specific grocery data
```

### Admin Data Controls
- **🧹 Clear All User Data:** Remove all expenses/subscriptions (keep accounts)
- **🗑️ Complete System Reset:** Fresh start with only admin/test users
- **👤 Individual User Management:** Clear specific user's data
- **📊 System Status:** Monitor users and data file counts

### Data Privacy & Security
- **Local storage only** - no cloud uploads
- **User isolation** - each user sees only their data
- **Encrypted passwords** with bcrypt hashing
- **Git-ignored sensitive files** - no accidental commits
- **Admin-only system controls** - protected operations

## 🔧 CSV Data Import

### Required Format
| Column | Description | Example |
|--------|-------------|---------|
| `Date` | Transaction date | 2024-01-01 |
| `Description` | Transaction description | WALMART SUPERCENTER |
| `Amount` | Transaction amount | -85.50 |

### Sample CSV
```csv
Date,Description,Amount
2024-01-01,PAYROLL DEPOSIT,3500.00
2024-01-02,WALMART SUPERCENTER,-85.50
2024-01-03,NETFLIX SUBSCRIPTION,-15.99
2024-01-05,SHELL GAS STATION,-45.20
```

## 🎨 Customization

### Adding Categories
Edit the `category_keywords` dictionary in `app.py`:
```python
self.category_keywords = {
    'Custom Category': ['keyword1', 'keyword2'],
    # ... existing categories
}
```

### SMS Configuration
1. **Sign up for Twilio** account
2. **Get Account SID, Auth Token, and Phone Number**
3. **Configure in SMS settings** within the app
4. **Test alerts** with subscription due dates

## 🛠️ Troubleshooting

### Common Issues

**Authentication Problems:**
- Clear browser cookies and retry login
- Ensure correct username/password format
- Check for caps lock and spelling

**OCR Not Working:**
- Install `requirements-ocr.txt` dependencies
- Install Tesseract OCR on your system
- Ensure images are clear and well-lit

**Data Not Persisting:**
- Login as admin (not test user)
- Check "Data Persistence" status in sidebar
- Verify file permissions in user_data directory

**SMS Alerts Failing:**
- Verify Twilio credentials in settings
- Check phone number format (+1234567890)
- Ensure Twilio account has sufficient credits

### File Permissions
```bash
# Ensure user_data directory is writable
chmod 755 user_data/
chmod 644 user_data/*.json
```

## 📈 Advanced Analytics

### Financial Metrics
- **Total Income/Expenses/Savings**
- **Savings Rate Percentage**
- **Category-wise spending breakdown**
- **Monthly trend analysis**
- **YTD comparisons and projections**

### Smart Insights
- **Spending pattern analysis**
- **Category overspending alerts**
- **Savings rate improvements**
- **Budget recommendations**
- **Recurring expense optimization**

## 🔒 Security Best Practices

### For Production Use
1. **Change default passwords** immediately
2. **Use strong passwords** for all accounts  
3. **Regular data backups** using admin controls
4. **Monitor user activity** through admin dashboard
5. **Keep dependencies updated** with `pip install -U`

### Data Protection
- **Local processing only** - no internet required for core features
- **Encrypted password storage** with bcrypt
- **User data isolation** - private file storage
- **Git exclusion** of sensitive data files

## 🚀 Future Roadmap

### Planned Features
- [ ] **Budget tracking** with spending limits and alerts
- [ ] **Goal setting** and progress tracking
- [ ] **Bank API integration** for automatic data sync
- [ ] **Machine learning** category prediction
- [ ] **Advanced reporting** with custom date ranges
- [ ] **Multi-currency support** for international users
- [ ] **Team collaboration** features for shared accounts

### Mobile Development
- [ ] **Progressive Web App (PWA)** for offline mobile use
- [ ] **Native iOS/Android** apps with sync capabilities
- [ ] **Camera integration** for instant receipt capture
- [ ] **Push notifications** for subscription alerts

## 📞 Support & Contributing

### Getting Help
1. **Check documentation** in `MOBILE_APP_GUIDE.md`
2. **Review troubleshooting** section above
3. **Create GitHub issue** for bugs or feature requests
4. **Contribute improvements** via pull requests

### Contributing
We welcome contributions! Areas for improvement:
- **New visualization types** and chart options
- **Enhanced categorization** rules and algorithms
- **Mobile UI improvements** and optimizations
- **Additional export formats** and report templates
- **Integration capabilities** with financial services

## 📜 License

This project is open source under the MIT License. Feel free to use, modify, and distribute.

---

**🏆 Built for comprehensive financial management with enterprise-grade features**

**💡 Perfect for individuals, families, and small businesses tracking expenses and financial goals**

For questions, support, or feature requests, visit our [GitHub repository](https://github.com/chanvekse/Finance-AI-Analyzer). 