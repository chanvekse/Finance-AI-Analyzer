# 💰 Bank Statement Analyzer

A comprehensive financial analysis tool that provides insights into your spending patterns, generates visualizations, and creates detailed PDF reports.

## 🚀 Features

### Core Analysis
- ✅ **CSV Data Processing**: Load and validate bank statement CSV files
- ✅ **Manual Expense Entry**: Quick expense tracking with category dropdowns and auto-date
- ✅ **Grocery Receipt Scanning**: OCR-powered receipt text extraction (optional)
- ✅ **Subscription Management**: Track recurring payments with due date alerts
- ✅ **Smart Categorization**: Automatically categorize transactions using keyword rules
- ✅ **Financial Metrics**: Calculate income, expenses, savings, and savings rate
- ✅ **Password Protection**: Secure user authentication and role management

### Visualizations
- 📊 **Category Spending**: Bar charts showing spending by category
- 📈 **Monthly Trends**: Line charts tracking income, expenses, and savings over time
- 🥧 **Pie Charts**: Spending distribution visualization
- 📉 **Daily Spending Trends**: Track daily spending patterns

### Reports & Insights
- 💡 **Smart Insights**: AI-powered financial recommendations
- 📄 **PDF Reports**: Professional PDF summaries with embedded charts
- 🎯 **Top Categories**: Identify biggest spending areas
- 📈 **Trend Analysis**: Understand financial trajectory

## 🖥️ Two Ways to Use

### 1. Command Line Interface (CLI)
```bash
python main.py
```
**Features:**
- Interactive terminal interface
- Complete analysis pipeline
- Matplotlib visualizations
- PDF report generation
- Sample data creation

### 2. Web Application (Streamlit)
```bash
streamlit run app.py
```
**Features:**
- Modern web interface
- Drag-and-drop file upload
- Interactive Plotly charts
- Real-time analysis
- PDF download functionality

## 📦 Installation

1. **Clone or download** this project
2. **Install core dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Optional: Install OCR dependencies for receipt scanning:**
   ```bash
   pip install -r requirements-ocr.txt
   ```

### Core Dependencies
```
pandas>=1.5.0          # Data processing
matplotlib>=3.5.0      # Static charts
seaborn>=0.11.0         # Statistical visualizations  
numpy>=1.21.0           # Numerical computations
fpdf2>=2.7.0           # PDF generation
streamlit>=1.28.0      # Web application
plotly>=5.15.0         # Interactive charts
openpyxl>=3.0.0        # Excel export
twilio>=8.5.0          # SMS notifications
bcrypt>=4.0.0          # Password hashing
```

### Optional OCR Dependencies
```
pytesseract>=0.3.10    # OCR text extraction
opencv-python>=4.8.0   # Image processing
pillow>=9.0.0          # Image handling
```

**Note:** For receipt OCR scanning to work, you also need to install Tesseract OCR:
- **Windows:** Download from [Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS:** `brew install tesseract`
- **Ubuntu/Debian:** `sudo apt install tesseract-ocr`

## 📊 CSV File Format

Your bank statement CSV must have these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `Date` | Transaction date | 2024-01-01 |
| `Description` | Transaction description | WALMART SUPERCENTER |
| `Amount` | Transaction amount | -85.50 |

### Sample CSV:
```csv
Date,Description,Amount
2024-01-01,PAYROLL DEPOSIT,3500.00
2024-01-02,WALMART SUPERCENTER,-85.50
2024-01-03,NETFLIX SUBSCRIPTION,-15.99
2024-01-05,SHELL GAS STATION,-45.20
```

## 🎯 Category Rules

Transactions are automatically categorized using these keyword rules:

- **Groceries**: walmart, kroger, trader joe, target
- **Entertainment**: netflix, youtube, apple music  
- **Dining**: starbucks, chick-fil-a
- **Transportation**: uber, lyft, shell, gas
- **Credit Card/Transfers**: chase, zelle
- **Bills**: rent, insurance, electricity, internet
- **Income**: salary, deposit
- **Uncategorized**: Everything else

## 🚀 Quick Start

### Web Application (Recommended)
```bash
streamlit run app.py
```
1. Open your browser to `http://localhost:8501`
2. **Login** with default credentials:
   - Username: `admin`
   - Password: `admin123`
   - ⚠️ **Change the password after first login**
3. Upload CSV files or enter expenses manually
4. Track groceries with receipt scanning
5. Set up subscription alerts
6. Generate comprehensive reports

### Option 2: Command Line
```bash
python main.py
```
1. Enter your CSV file path (or press Enter for sample data)
2. View terminal output analysis
3. Check generated visualizations
4. Open `finance_summary.pdf`

## 📈 Analysis Output

### Metrics Calculated
- **Total Income**: Sum of positive amounts
- **Total Expenses**: Sum of negative amounts (absolute)
- **Net Savings**: Income - Expenses
- **Savings Rate**: (Savings / Income) × 100
- **Financial Health Score**: 0-100 comprehensive rating

### Visualizations Generated
1. **Category Bar Chart**: Horizontal bar chart of spending by category
2. **Monthly Trends**: Line chart showing income/expenses/savings over time
3. **Pie Chart**: Spending distribution by category
4. **Daily Trends**: Daily spending pattern analysis

### Reports Generated
- **Terminal Output**: Comprehensive text analysis
- **PNG Charts**: High-resolution chart images
- **PDF Report**: Professional summary document
- **Interactive Charts**: Web-based visualizations (Streamlit only)

## 🔧 Advanced Features

### Monthly Comparison Analysis
- Compares current month vs previous month
- Shows percentage changes in income, expenses, savings
- Identifies categories with biggest changes
- Provides trend-based recommendations

### Financial Health Scoring
- **Savings Rate** (40 points): Based on percentage saved
- **Spending Distribution** (30 points): Balance across categories  
- **Emergency Fund** (30 points): Estimated fund adequacy

### Smart Insights
- Personalized recommendations based on spending patterns
- Category-specific advice
- Trend analysis and alerts
- Financial goal suggestions

## 📁 Generated Files

After running analysis, you'll find:
- `category_pie.png`: Pie chart visualization
- `finance_summary.pdf`: Comprehensive PDF report
- Sample CSV files for testing

## 🛠️ Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
pip install -r requirements.txt
```

**CSV format errors:**
- Ensure columns are named exactly: Date, Description, Amount
- Check date format (YYYY-MM-DD recommended)
- Verify amounts are numeric (negative for expenses)

**Streamlit won't start:**
```bash
streamlit --version
streamlit run app.py --server.port 8502
```

### File Encoding Issues
If you see encoding errors:
```python
# The app automatically handles common encodings
# Try saving your CSV as UTF-8 in Excel/Google Sheets
```

## 🎨 Customization

### Adding New Categories
Edit the `category_keywords` dictionary in either file:
```python
self.category_keywords = {
    'Your Category': ['keyword1', 'keyword2'],
    # ... existing categories
}
```

### Changing Analysis Period
The tool automatically detects date ranges, but you can filter data:
```python
df = df[df['Date'] >= '2024-01-01']  # Filter to specific date
```

## 📊 Sample Data

Both applications include sample data generators for testing. The sample includes:
- Multi-month transactions (January & February 2024)
- Various categories and transaction types
- Realistic spending patterns for demonstration

## 🔒 Privacy & Security

- ✅ **Local Processing**: All analysis runs on your computer
- ✅ **No Data Upload**: Your financial data never leaves your device
- ✅ **No Internet Required**: Works completely offline
- ✅ **Open Source**: Full transparency in code

## 🤝 Contributing

Want to improve the analyzer? Here are some ideas:
- Add new visualization types
- Improve categorization rules  
- Add more financial metrics
- Enhance PDF reports
- Create mobile-friendly interface

## 📜 License

This project is open source. Feel free to use, modify, and distribute.

## 🚀 Future Enhancements

Planned features:
- [ ] Budget tracking and alerts
- [ ] Goal setting and progress tracking
- [ ] Multi-account analysis
- [ ] Integration with bank APIs
- [ ] Machine learning categorization
- [ ] Expense forecasting
- [ ] Mobile app version

---

**Built with ❤️ for better financial awareness**

For support or questions, check the code comments or create an issue! 