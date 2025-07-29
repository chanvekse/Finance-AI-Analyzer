import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
from collections import defaultdict
import re
from fpdf import FPDF

class BankStatementAnalyzer:
    def __init__(self, csv_file_path):
        """Initialize the analyzer with a CSV file path."""
        self.csv_file_path = csv_file_path
        self.df = None
        self.categorized_df = None
        
        # Define category keywords mapping as specified by user
        self.category_keywords = {
            'Groceries': ['walmart', 'kroger', 'trader joe', 'target'],
            'Entertainment': ['netflix', 'youtube', 'apple music'],
            'Dining': ['starbucks', 'chick-fil-a'],
            'Transportation': ['uber', 'lyft', 'shell', 'gas'],
            'Credit Card / Transfers': ['chase', 'zelle'],
            'Bills': ['rent', 'insurance', 'electricity', 'internet'],
            'Income': ['salary', 'deposit'],
            'Uncategorized': []
        }
    
    def load_csv(self):
        """Load and validate the CSV file."""
        try:
            self.df = pd.read_csv(self.csv_file_path)
            
            # Validate required columns
            required_columns = ['Date', 'Description', 'Amount']
            if not all(col in self.df.columns for col in required_columns):
                raise ValueError(f"CSV must contain columns: {required_columns}")
            
            # Convert Date column to datetime
            self.df['Date'] = pd.to_datetime(self.df['Date'])
            
            # Convert Amount to numeric
            self.df['Amount'] = pd.to_numeric(self.df['Amount'], errors='coerce')
            
            # Remove rows with invalid data
            self.df = self.df.dropna()
            
            print(f"✅ Successfully loaded {len(self.df)} transactions")
            return True
            
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            return False
    
    def categorize_transaction(self, description):
        """Categorize a transaction based on description keywords."""
        description_lower = description.lower()
        
        for category, keywords in self.category_keywords.items():
            if category == 'Uncategorized':
                continue
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'Uncategorized'
    
    def categorize_transactions(self):
        """Apply categorization to all transactions."""
        if self.df is None:
            print("❌ Please load CSV data first")
            return False
        
        self.df['Category'] = self.df['Description'].apply(self.categorize_transaction)
        
        # Separate income and expenses
        self.df['Type'] = self.df['Amount'].apply(lambda x: 'Income' if x > 0 else 'Expense')
        self.df['Month'] = self.df['Date'].dt.to_period('M')
        
        self.categorized_df = self.df.copy()
        print("✅ Transactions categorized successfully")
        return True
    
    def calculate_category_totals(self):
        """Calculate total spending per category."""
        if self.categorized_df is None:
            print("❌ Please categorize transactions first")
            return None
        
        # Filter only expenses (negative amounts)
        expenses = self.categorized_df[self.categorized_df['Amount'] < 0].copy()
        expenses['Amount'] = expenses['Amount'].abs()  # Convert to positive for easier reading
        
        category_totals = expenses.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        
        print("\n📊 SPENDING BY CATEGORY:")
        print("-" * 30)
        for category, total in category_totals.items():
            print(f"{category:20}: ${total:,.2f}")
        
        return category_totals
    
    def monthly_income_vs_expenses(self):
        """Calculate monthly income vs expenses."""
        if self.categorized_df is None:
            print("❌ Please categorize transactions first")
            return None
        
        monthly_summary = self.categorized_df.groupby(['Month', 'Type'])['Amount'].sum().unstack(fill_value=0)
        
        # Ensure we have both Income and Expense columns
        if 'Income' not in monthly_summary.columns:
            monthly_summary['Income'] = 0
        if 'Expense' not in monthly_summary.columns:
            monthly_summary['Expense'] = 0
        
        monthly_summary['Expense'] = monthly_summary['Expense'].abs()  # Convert to positive
        monthly_summary['Net_Savings'] = monthly_summary['Income'] - monthly_summary['Expense']
        
        print("\n📈 MONTHLY INCOME VS EXPENSES:")
        print("-" * 50)
        for month in monthly_summary.index:
            income = monthly_summary.loc[month, 'Income']
            expense = monthly_summary.loc[month, 'Expense']
            savings = monthly_summary.loc[month, 'Net_Savings']
            print(f"{month} | Income: ${income:,.2f} | Expenses: ${expense:,.2f} | Savings: ${savings:,.2f}")
        
        return monthly_summary
    
    def visualize_category_spending(self, category_totals):
        """Create bar chart for category-wise spending."""
        plt.figure(figsize=(12, 8))
        colors = plt.cm.Set3(np.linspace(0, 1, len(category_totals)))
        
        bars = plt.bar(range(len(category_totals)), category_totals.values, color=colors)
        plt.title('Category-wise Spending Analysis', fontsize=16, fontweight='bold')
        plt.xlabel('Categories', fontsize=12)
        plt.ylabel('Amount Spent ($)', fontsize=12)
        plt.xticks(range(len(category_totals)), category_totals.index, rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, value in zip(bars, category_totals.values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + value*0.01,
                    f'${value:,.0f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.grid(axis='y', alpha=0.3)
        plt.show()
    
    def visualize_daily_spending_trend(self):
        """Create line chart for daily spending trend."""
        if self.categorized_df is None:
            return
        
        # Filter expenses and group by date
        expenses = self.categorized_df[self.categorized_df['Amount'] < 0].copy()
        expenses['Amount'] = expenses['Amount'].abs()
        daily_spending = expenses.groupby('Date')['Amount'].sum()
        
        plt.figure(figsize=(14, 6))
        plt.plot(daily_spending.index, daily_spending.values, marker='o', linewidth=2, markersize=4)
        plt.title('Daily Spending Trend', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Daily Spending ($)', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(range(len(daily_spending)), daily_spending.values, 1)
        p = np.poly1d(z)
        plt.plot(daily_spending.index, p(range(len(daily_spending))), "--", alpha=0.8, color='red', 
                label=f'Trend Line (${p.coefficients[0]:.2f}/day)')
        plt.legend()
        
        plt.tight_layout()
        plt.show()
    
    def visualize_monthly_financial_trends(self):
        """Create line plot of monthly financial trends showing income, expenses, and savings."""
        if self.categorized_df is None:
            print("❌ Please categorize transactions first")
            return
        
        # Group by month and calculate totals
        monthly_data = self.categorized_df.groupby('Month').agg({
            'Amount': lambda x: [x[x > 0].sum(), abs(x[x < 0].sum())]
        }).reset_index()
        
        # Extract income and expenses from the aggregated data
        monthly_data['Income'] = monthly_data['Amount'].apply(lambda x: x[0])
        monthly_data['Expenses'] = monthly_data['Amount'].apply(lambda x: x[1])
        monthly_data['Savings'] = monthly_data['Income'] - monthly_data['Expenses']
        
        # Convert Month period to string for better x-axis labels
        monthly_data['Month_Str'] = monthly_data['Month'].astype(str)
        
        # Create the line plot
        plt.figure(figsize=(12, 8))
        
        # Plot the three lines
        plt.plot(monthly_data['Month_Str'], monthly_data['Income'], 
                marker='o', linewidth=3, markersize=8, label='Income', color='green')
        plt.plot(monthly_data['Month_Str'], monthly_data['Expenses'], 
                marker='s', linewidth=3, markersize=8, label='Expenses', color='red')
        plt.plot(monthly_data['Month_Str'], monthly_data['Savings'], 
                marker='^', linewidth=3, markersize=8, label='Savings', color='blue')
        
        # Customize the plot
        plt.title('Monthly Financial Trends', fontsize=18, fontweight='bold', pad=20)
        plt.xlabel('Month', fontsize=14, fontweight='bold')
        plt.ylabel('Amount ($)', fontsize=14, fontweight='bold')
        
        # Format y-axis to show currency
        ax = plt.gca()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Add horizontal line at zero for savings reference
        plt.axhline(y=0, color='gray', linestyle='--', alpha=0.7, linewidth=1)
        
        # Customize legend
        plt.legend(fontsize=12, frameon=True, fancybox=True, shadow=True)
        
        # Add grid for better readability
        plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        # Add value annotations on data points
        for i, row in monthly_data.iterrows():
            # Income annotation
            plt.annotate(f'${row["Income"]:,.0f}', 
                        (i, row['Income']), 
                        textcoords="offset points", 
                        xytext=(0,10), 
                        ha='center', fontsize=9, color='green', fontweight='bold')
            
            # Expenses annotation
            plt.annotate(f'${row["Expenses"]:,.0f}', 
                        (i, row['Expenses']), 
                        textcoords="offset points", 
                        xytext=(0,10), 
                        ha='center', fontsize=9, color='red', fontweight='bold')
            
            # Savings annotation (with different positioning based on positive/negative)
            y_offset = 10 if row['Savings'] >= 0 else -20
            color = 'blue' if row['Savings'] >= 0 else 'darkred'
            plt.annotate(f'${row["Savings"]:,.0f}', 
                        (i, row['Savings']), 
                        textcoords="offset points", 
                        xytext=(0, y_offset), 
                        ha='center', fontsize=9, color=color, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
        
        # Print summary statistics
        print("\n📈 MONTHLY TRENDS SUMMARY:")
        print("-" * 40)
        avg_income = monthly_data['Income'].mean()
        avg_expenses = monthly_data['Expenses'].mean()
        avg_savings = monthly_data['Savings'].mean()
        
        print(f"Average Monthly Income:  ${avg_income:,.2f}")
        print(f"Average Monthly Expenses: ${avg_expenses:,.2f}")
        print(f"Average Monthly Savings:  ${avg_savings:,.2f}")
        
        if avg_savings > 0:
            print("✅ Positive average monthly savings trend!")
        else:
            print("⚠️  Negative average monthly savings - consider expense reduction.")
        
        return monthly_data
    
    def create_category_pie_chart(self):
        """Create and save a pie chart showing spending by category."""
        if self.categorized_df is None:
            print("❌ Please categorize transactions first")
            return False
        
        try:
            # Filter only expenses (negative amounts)
            expenses_df = self.categorized_df[self.categorized_df['Amount'] < 0].copy()
            expenses_df['Amount'] = expenses_df['Amount'].abs()
            
            # Group by category and calculate totals
            category_spending = expenses_df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
            
            # Create the pie chart
            plt.figure(figsize=(10, 8))
            
            # Define colors for the pie chart
            colors = plt.cm.Set3(range(len(category_spending)))
            
            # Create pie chart with better formatting
            wedges, texts, autotexts = plt.pie(
                category_spending.values, 
                labels=category_spending.index,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                explode=[0.05 if i == 0 else 0 for i in range(len(category_spending))],  # Explode the largest slice
                shadow=True
            )
            
            # Customize the text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
            
            for text in texts:
                text.set_fontsize(11)
                text.set_fontweight('bold')
            
            # Add title
            plt.title('Spending Distribution by Category', 
                     fontsize=16, fontweight='bold', pad=20)
            
            # Add total spending as subtitle
            total_spending = category_spending.sum()
            plt.suptitle(f'Total Spending: ${total_spending:,.2f}', 
                        fontsize=12, y=0.02)
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            plt.axis('equal')
            
            # Save the chart
            plt.tight_layout()
            plt.savefig('category_pie.png', dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()  # Close the figure to free memory
            
            print("✅ Pie chart saved as 'category_pie.png'")
            return True
            
        except Exception as e:
            print(f"❌ Error creating pie chart: {e}")
            return False
    
    def generate_financial_insights(self):
        """Generate detailed financial insights and recommendations."""
        if self.categorized_df is None:
            print("❌ Please categorize transactions first")
            return
        
        print("\n" + "="*70)
        print("🔍 FINANCIAL INSIGHTS & ANALYSIS")
        print("="*70)
        
        # Calculate basic metrics
        total_income = self.categorized_df[self.categorized_df['Amount'] > 0]['Amount'].sum()
        total_expenses = abs(self.categorized_df[self.categorized_df['Amount'] < 0]['Amount'].sum())
        total_savings = total_income - total_expenses
        savings_rate = (total_savings / total_income * 100) if total_income > 0 else 0
        
        # 1. Top 3 spending categories
        expenses_df = self.categorized_df[self.categorized_df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        category_spending = expenses_df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        
        print("\n💸 TOP 3 SPENDING CATEGORIES:")
        print("-" * 50)
        for i, (category, amount) in enumerate(category_spending.head(3).items(), 1):
            percentage = (amount / total_income * 100) if total_income > 0 else 0
            print(f"{i}. {category:25} ${amount:>8,.2f} ({percentage:5.1f}% of income)")
        
        # 2. Savings rate analysis
        print(f"\n💰 SAVINGS ANALYSIS:")
        print("-" * 30)
        print(f"💵 Total Income:     ${total_income:>10,.2f}")
        print(f"💸 Total Expenses:   ${total_expenses:>10,.2f}")
        print(f"🏦 Net Savings:      ${total_savings:>10,.2f}")
        print(f"📊 Savings Rate:     {savings_rate:>13.1f}%")
        
        # Savings rate evaluation
        if savings_rate >= 20:
            print("✅ EXCELLENT! You're saving 20%+ of your income!")
        elif savings_rate >= 10:
            print("✅ GOOD! You're saving 10%+ of your income.")
        elif savings_rate >= 0:
            print("⚠️  FAIR: You're saving money, but could improve.")
        else:
            print("🚨 ALERT: You're spending more than you earn!")
        
        # 3. Monthly comparison (if multiple months exist)
        monthly_summary = self.categorized_df.groupby('Month').agg({
            'Amount': lambda x: [x[x > 0].sum(), abs(x[x < 0].sum())]
        })
        
        if len(monthly_summary) > 1:
            print(f"\n📈 MONTH-OVER-MONTH ANALYSIS:")
            print("-" * 40)
            
            months = sorted(monthly_summary.index)
            current_month = months[-1]
            previous_month = months[-2]
            
            current_expenses = monthly_summary.loc[current_month, 'Amount'][1]
            previous_expenses = monthly_summary.loc[previous_month, 'Amount'][1]
            
            expense_change = current_expenses - previous_expenses
            expense_change_pct = (expense_change / previous_expenses * 100) if previous_expenses > 0 else 0
            
            print(f"Previous Month ({previous_month}): ${previous_expenses:,.2f}")
            print(f"Current Month ({current_month}):  ${current_expenses:,.2f}")
            print(f"Change:                     ${expense_change:+,.2f} ({expense_change_pct:+.1f}%)")
            
            if expense_change > 0:
                print(f"📈 Expenses INCREASED by ${expense_change:,.2f} this month")
            elif expense_change < 0:
                print(f"📉 Expenses DECREASED by ${abs(expense_change):,.2f} this month")
            else:
                print("➡️  Expenses remained the same this month")
        else:
            print(f"\n📅 SINGLE MONTH DATA:")
            print("-" * 30)
            print("Need multiple months of data for trend analysis.")
        
        # 4. Category insights and recommendations
        print(f"\n🎯 CATEGORY INSIGHTS:")
        print("-" * 30)
        
        for category, amount in category_spending.head(5).items():
            percentage = (amount / total_income * 100) if total_income > 0 else 0
            
            # Provide recommendations based on category and percentage
            if category == 'Bills' and percentage > 50:
                print(f"⚠️  {category}: {percentage:.1f}% - Consider reviewing bills for potential savings")
            elif category == 'Dining' and percentage > 15:
                print(f"🍽️  {category}: {percentage:.1f}% - High dining costs, consider cooking more at home")
            elif category == 'Entertainment' and percentage > 10:
                print(f"🎬 {category}: {percentage:.1f}% - Entertainment spending is above average")
            elif category == 'Transportation' and percentage > 20:
                print(f"🚗 {category}: {percentage:.1f}% - High transportation costs, consider alternatives")
            elif category == 'Groceries' and percentage > 15:
                print(f"🛒 {category}: {percentage:.1f}% - Grocery spending is reasonable")
            elif category == 'Uncategorized' and percentage > 20:
                print(f"❓ {category}: {percentage:.1f}% - Large uncategorized expenses need review")
            else:
                print(f"✓  {category}: {percentage:.1f}% - Spending level looks reasonable")
        
        # 5. Financial health score
        print(f"\n🏥 FINANCIAL HEALTH SCORE:")
        print("-" * 35)
        
        health_score = 0
        factors = []
        
        # Savings rate factor (40 points max)
        if savings_rate >= 20:
            health_score += 40
            factors.append("✅ Excellent savings rate (+40)")
        elif savings_rate >= 10:
            health_score += 30
            factors.append("✅ Good savings rate (+30)")
        elif savings_rate >= 0:
            health_score += 15
            factors.append("⚠️  Fair savings rate (+15)")
        else:
            health_score += 0
            factors.append("🚨 Negative savings rate (+0)")
        
        # Category distribution factor (30 points max)
        top_category_pct = (category_spending.iloc[0] / total_income * 100) if len(category_spending) > 0 and total_income > 0 else 0
        if top_category_pct < 40:
            health_score += 30
            factors.append("✅ Balanced spending distribution (+30)")
        elif top_category_pct < 60:
            health_score += 20
            factors.append("⚠️  Moderate spending concentration (+20)")
        else:
            health_score += 10
            factors.append("🚨 High spending concentration (+10)")
        
        # Emergency fund estimate (30 points max)
        monthly_expenses = total_expenses / len(self.categorized_df['Month'].unique())
        emergency_fund_months = total_savings / monthly_expenses if monthly_expenses > 0 and total_savings > 0 else 0
        
        if emergency_fund_months >= 6:
            health_score += 30
            factors.append("✅ Strong emergency fund position (+30)")
        elif emergency_fund_months >= 3:
            health_score += 20
            factors.append("✅ Adequate emergency fund (+20)")
        elif emergency_fund_months >= 1:
            health_score += 10
            factors.append("⚠️  Limited emergency fund (+10)")
        else:
            health_score += 0
            factors.append("🚨 No emergency fund buffer (+0)")
        
        print(f"📊 Overall Score: {health_score}/100")
        
        if health_score >= 80:
            print("🏆 EXCELLENT - Your finances are in great shape!")
        elif health_score >= 60:
            print("✅ GOOD - You're doing well with room for improvement")
        elif health_score >= 40:
            print("⚠️  FAIR - Several areas need attention")
        else:
            print("🚨 NEEDS IMPROVEMENT - Consider financial planning help")
        
        print("\nScore Breakdown:")
        for factor in factors:
            print(f"  {factor}")
        
        # 6. Action recommendations
        print(f"\n💡 RECOMMENDED ACTIONS:")
        print("-" * 35)
        
        if savings_rate < 10:
            print("1. 🎯 Increase savings to at least 10% of income")
        if category_spending.iloc[0] / total_income > 0.5:
            print("2. 🔍 Review largest expense category for optimization")
        if 'Uncategorized' in category_spending.head(3).index:
            print("3. 📝 Track and categorize unknown expenses")
        if len(monthly_summary) > 1 and expense_change > 0:
            print("4. 📉 Investigate recent expense increases")
        
        if health_score >= 80:
            print("🌟 Keep up the excellent financial management!")
        
        print("="*70)
    
    def analyze_monthly_comparison(self):
        """Analyze month-over-month changes in income, expenses, savings, and category spending."""
        if self.categorized_df is None:
            print("❌ Please categorize transactions first")
            return
        
        # Get unique months and check if we have at least 2 months
        months = sorted(self.categorized_df['Month'].unique())
        
        if len(months) < 2:
            print("\n📅 MONTHLY COMPARISON:")
            print("-" * 40)
            print("⚠️  Need at least 2 months of data for comparison analysis.")
            print(f"Currently have data for: {months[0] if months else 'No months'}")
            return
        
        # Get the 2 most recent months
        current_month = months[-1]
        previous_month = months[-2]
        
        print("\n" + "="*70)
        print("📈 MONTH-OVER-MONTH COMPARISON ANALYSIS")
        print("="*70)
        
        # Calculate metrics for both months
        def calculate_month_metrics(month):
            month_data = self.categorized_df[self.categorized_df['Month'] == month]
            income = month_data[month_data['Amount'] > 0]['Amount'].sum()
            expenses = abs(month_data[month_data['Amount'] < 0]['Amount'].sum())
            savings = income - expenses
            return income, expenses, savings, month_data
        
        prev_income, prev_expenses, prev_savings, prev_data = calculate_month_metrics(previous_month)
        curr_income, curr_expenses, curr_savings, curr_data = calculate_month_metrics(current_month)
        
        # Calculate percentage changes
        def calculate_change_pct(current, previous):
            if previous == 0:
                return float('inf') if current > 0 else 0
            return ((current - previous) / previous) * 100
        
        income_change = calculate_change_pct(curr_income, prev_income)
        expenses_change = calculate_change_pct(curr_expenses, prev_expenses)
        savings_change = calculate_change_pct(curr_savings, prev_savings)
        
        # Print comparison summary
        print(f"\n💰 FINANCIAL METRICS COMPARISON:")
        print("-" * 50)
        print(f"📅 Previous Month: {previous_month}")
        print(f"📅 Current Month:  {current_month}")
        print()
        
        # Income comparison
        income_arrow = "📈" if income_change > 0 else "📉" if income_change < 0 else "➡️"
        print(f"💵 INCOME:")
        print(f"   Previous: ${prev_income:>10,.2f}")
        print(f"   Current:  ${curr_income:>10,.2f}")
        if income_change == float('inf'):
            print(f"   Change:   {income_arrow} New income (from $0)")
        else:
            print(f"   Change:   {income_arrow} {income_change:+6.1f}% (${curr_income - prev_income:+,.2f})")
        print()
        
        # Expenses comparison
        expense_arrow = "📈" if expenses_change > 0 else "📉" if expenses_change < 0 else "➡️"
        print(f"💸 EXPENSES:")
        print(f"   Previous: ${prev_expenses:>10,.2f}")
        print(f"   Current:  ${curr_expenses:>10,.2f}")
        if expenses_change == float('inf'):
            print(f"   Change:   {expense_arrow} New expenses (from $0)")
        else:
            print(f"   Change:   {expense_arrow} {expenses_change:+6.1f}% (${curr_expenses - prev_expenses:+,.2f})")
        print()
        
        # Savings comparison
        savings_arrow = "📈" if savings_change > 0 else "📉" if savings_change < 0 else "➡️"
        print(f"🏦 SAVINGS:")
        print(f"   Previous: ${prev_savings:>10,.2f}")
        print(f"   Current:  ${curr_savings:>10,.2f}")
        if prev_savings == 0 and curr_savings != 0:
            print(f"   Change:   {savings_arrow} New savings trend")
        elif savings_change == float('inf'):
            print(f"   Change:   {savings_arrow} Significant improvement")
        else:
            print(f"   Change:   {savings_arrow} {savings_change:+6.1f}% (${curr_savings - prev_savings:+,.2f})")
        
        # Category-wise spending comparison
        print(f"\n🎯 CATEGORY SPENDING CHANGES:")
        print("-" * 50)
        
        # Get category spending for both months (expenses only)
        def get_category_spending(month_data):
            expenses_data = month_data[month_data['Amount'] < 0].copy()
            expenses_data['Amount'] = expenses_data['Amount'].abs()
            return expenses_data.groupby('Category')['Amount'].sum()
        
        prev_categories = get_category_spending(prev_data)
        curr_categories = get_category_spending(curr_data)
        
        # Get all categories from both months
        all_categories = set(prev_categories.index) | set(curr_categories.index)
        
        category_changes = []
        
        for category in all_categories:
            prev_amount = prev_categories.get(category, 0)
            curr_amount = curr_categories.get(category, 0)
            
            if prev_amount == 0 and curr_amount > 0:
                change_pct = float('inf')
                change_amount = curr_amount
                change_desc = "NEW"
            elif prev_amount > 0 and curr_amount == 0:
                change_pct = -100
                change_amount = -prev_amount
                change_desc = "ELIMINATED"
            elif prev_amount == 0 and curr_amount == 0:
                continue
            else:
                change_pct = ((curr_amount - prev_amount) / prev_amount) * 100
                change_amount = curr_amount - prev_amount
                change_desc = f"{change_pct:+.1f}%"
            
            category_changes.append({
                'category': category,
                'prev_amount': prev_amount,
                'curr_amount': curr_amount,
                'change_pct': change_pct,
                'change_amount': change_amount,
                'change_desc': change_desc
            })
        
        # Sort by absolute change amount (biggest changes first)
        category_changes.sort(key=lambda x: abs(x['change_amount']), reverse=True)
        
        # Print top category changes
        print("Top 5 Category Changes:")
        print()
        for i, change in enumerate(category_changes[:5], 1):
            arrow = "📈" if change['change_amount'] > 0 else "📉" if change['change_amount'] < 0 else "➡️"
            
            print(f"{i}. {change['category']:20} {arrow}")
            print(f"   Previous: ${change['prev_amount']:>8,.2f}")
            print(f"   Current:  ${change['curr_amount']:>8,.2f}")
            print(f"   Change:   {change['change_desc']:>8} (${change['change_amount']:+,.2f})")
            print()
        
        # Identify biggest change
        if category_changes:
            biggest_change = category_changes[0]
            print(f"🔥 BIGGEST CHANGE: {biggest_change['category']}")
            print(f"   Amount: ${biggest_change['change_amount']:+,.2f} ({biggest_change['change_desc']})")
            
            if biggest_change['change_amount'] > 0:
                print(f"   ⚠️  Consider reviewing this category for potential savings")
            else:
                print(f"   ✅ Great job reducing spending in this category!")
        
        # Overall trend analysis
        print(f"\n📊 OVERALL TREND ANALYSIS:")
        print("-" * 40)
        
        if curr_savings > prev_savings:
            if curr_savings > 0:
                print("✅ IMPROVING: Savings increased and are positive")
            else:
                print("📈 IMPROVING: Moving towards positive savings")
        elif curr_savings < prev_savings:
            if curr_savings > 0:
                print("⚠️  DECLINING: Savings decreased but still positive")
            else:
                print("🚨 DECLINING: Savings decreased and are negative")
        else:
            if curr_savings > 0:
                print("➡️  STABLE: Consistent positive savings")
            else:
                print("⚠️  STABLE: Consistent negative savings - action needed")
        
        # Recommendations based on trends
        print(f"\n💡 MONTH-TO-MONTH RECOMMENDATIONS:")
        print("-" * 45)
        
        recommendations_given = 0
        if expenses_change > 10:
            print("1. 🎯 Expenses increased significantly - review recent spending")
            recommendations_given += 1
        if income_change < -5:
            print(f"{recommendations_given + 1}. 💰 Income decreased - consider additional income sources")
            recommendations_given += 1
        if category_changes and biggest_change['change_amount'] > 0 and biggest_change['change_amount'] > curr_income * 0.1:
            print(f"{recommendations_given + 1}. 🔍 Large increase in {biggest_change['category']} - investigate this category")
            recommendations_given += 1
        if curr_savings < 0 and prev_savings >= 0:
            print(f"{recommendations_given + 1}. 🚨 Moved from positive to negative savings - urgent budget review needed")
            recommendations_given += 1
        
        if recommendations_given == 0:
            print("✨ Your month-to-month financial trends look stable!")
        
        print("="*70)
        return category_changes
    
    def generate_summary(self):
        """Generate comprehensive financial summary."""
        if self.categorized_df is None:
            print("❌ Please categorize transactions first")
            return
        
        # Calculate key metrics
        total_income = self.categorized_df[self.categorized_df['Amount'] > 0]['Amount'].sum()
        total_expenses = abs(self.categorized_df[self.categorized_df['Amount'] < 0]['Amount'].sum())
        total_savings = total_income - total_expenses
        
        # Find most expensive category
        expenses = self.categorized_df[self.categorized_df['Amount'] < 0].copy()
        expenses['Amount'] = expenses['Amount'].abs()
        category_totals = expenses.groupby('Category')['Amount'].sum()
        most_expensive_category = category_totals.idxmax()
        most_expensive_amount = category_totals.max()
        
        # Calculate savings rate
        savings_rate = (total_savings / total_income * 100) if total_income > 0 else 0
        
        print("\n" + "="*60)
        print("💰 FINANCIAL SUMMARY REPORT")
        print("="*60)
        print(f"📅 Analysis Period: {self.categorized_df['Date'].min().strftime('%Y-%m-%d')} to {self.categorized_df['Date'].max().strftime('%Y-%m-%d')}")
        print(f"📊 Total Transactions: {len(self.categorized_df)}")
        print(f"💵 Total Income: ${total_income:,.2f}")
        print(f"💸 Total Expenses: ${total_expenses:,.2f}")
        print(f"🏦 Net Savings: ${total_savings:,.2f}")
        print(f"📈 Savings Rate: {savings_rate:.1f}%")
        print(f"🔥 Most Expensive Category: {most_expensive_category} (${most_expensive_amount:,.2f})")
        
        # Additional insights
        avg_daily_spending = total_expenses / len(self.categorized_df['Date'].unique())
        print(f"📊 Average Daily Spending: ${avg_daily_spending:.2f}")
        
        if total_savings > 0:
            print("✅ You're saving money! Keep up the good work!")
        else:
            print("⚠️  You're spending more than you earn. Consider reviewing your expenses.")
        
        print("="*60)
    
    def generate_pdf_report(self, total_income, total_expenses, total_savings, savings_rate, top_categories):
        """Generate a PDF report with financial summary."""
        try:
            # Create PDF instance
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Title
            pdf.set_font('Arial', 'B', 20)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 15, 'Monthly Financial Summary', 0, 1, 'C')
            pdf.ln(10)
            
            # Date range
            date_min = self.categorized_df['Date'].min().strftime('%Y-%m-%d')
            date_max = self.categorized_df['Date'].max().strftime('%Y-%m-%d')
            pdf.set_font('Arial', '', 12)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 8, f'Analysis Period: {date_min} to {date_max}', 0, 1, 'C')
            pdf.ln(15)
            
            # Financial Overview Section
            pdf.set_font('Arial', 'B', 16)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 10, 'Financial Overview', 0, 1, 'L')
            pdf.ln(5)
            
            # Create a summary box
            pdf.set_fill_color(240, 240, 240)
            pdf.rect(10, pdf.get_y(), 190, 60, 'F')
            
            # Financial metrics
            pdf.set_font('Arial', 'B', 12)
            pdf.set_text_color(0, 100, 0)  # Green for income
            pdf.cell(95, 12, f'Total Income:', 0, 0, 'L')
            pdf.set_text_color(0, 0, 0)
            pdf.cell(95, 12, f'${total_income:,.2f}', 0, 1, 'R')
            
            pdf.set_text_color(200, 0, 0)  # Red for expenses
            pdf.cell(95, 12, f'Total Expenses:', 0, 0, 'L')
            pdf.set_text_color(0, 0, 0)
            pdf.cell(95, 12, f'${total_expenses:,.2f}', 0, 1, 'R')
            
            pdf.set_text_color(0, 0, 200)  # Blue for savings
            pdf.cell(95, 12, f'Net Savings:', 0, 0, 'L')
            pdf.set_text_color(0, 0, 0)
            savings_color = (200, 0, 0) if total_savings < 0 else (0, 100, 0)
            pdf.set_text_color(*savings_color)
            pdf.cell(95, 12, f'${total_savings:,.2f}', 0, 1, 'R')
            
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(95, 12, f'Savings Rate:', 0, 0, 'L')
            rate_color = (200, 0, 0) if savings_rate < 0 else (0, 100, 0)
            pdf.set_text_color(*rate_color)
            pdf.cell(95, 12, f'{savings_rate:.1f}%', 0, 1, 'R')
            
            pdf.ln(20)
            
            # Top Spending Categories Section
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Top Spending Categories', 0, 1, 'L')
            pdf.ln(5)
            
            # Category table header
            pdf.set_fill_color(200, 200, 200)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(10, 12, '#', 1, 0, 'C', True)
            pdf.cell(120, 12, 'Category', 1, 0, 'L', True)
            pdf.cell(30, 12, 'Amount', 1, 0, 'R', True)
            pdf.cell(30, 12, '% of Income', 1, 1, 'R', True)
            
            # Category rows
            pdf.set_font('Arial', '', 11)
            pdf.set_fill_color(250, 250, 250)
            
            for i, (category, amount) in enumerate(top_categories.head(3).items(), 1):
                percentage = (amount / total_income * 100) if total_income > 0 else 0
                fill = True if i % 2 == 0 else False
                
                pdf.cell(10, 10, str(i), 1, 0, 'C', fill)
                pdf.cell(120, 10, category, 1, 0, 'L', fill)
                pdf.cell(30, 10, f'${amount:,.2f}', 1, 0, 'R', fill)
                pdf.cell(30, 10, f'{percentage:.1f}%', 1, 1, 'R', fill)
            
            pdf.ln(15)
            
            # Financial Health Assessment
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Financial Health Assessment', 0, 1, 'L')
            pdf.ln(5)
            
            # Health indicators
            pdf.set_font('Arial', '', 11)
            
            # Savings assessment
            if savings_rate >= 20:
                status = "EXCELLENT - You're saving 20%+ of your income!"
                status_color = (0, 150, 0)
            elif savings_rate >= 10:
                status = "GOOD - You're saving 10%+ of your income."
                status_color = (0, 100, 0)
            elif savings_rate >= 0:
                status = "FAIR - You're saving money, but could improve."
                status_color = (200, 150, 0)
            else:
                status = "ALERT - You're spending more than you earn!"
                status_color = (200, 0, 0)
            
            pdf.set_text_color(*status_color)
            pdf.cell(0, 8, f'Savings Status: {status}', 0, 1, 'L')
            
            # Spending concentration
            pdf.set_text_color(0, 0, 0)
            top_category_pct = (top_categories.iloc[0] / total_income * 100) if len(top_categories) > 0 else 0
            if top_category_pct > 50:
                concentration_msg = f"High spending concentration in {top_categories.index[0]} ({top_category_pct:.1f}%)"
            else:
                concentration_msg = f"Balanced spending distribution across categories"
            
            pdf.cell(0, 8, f'Spending Pattern: {concentration_msg}', 0, 1, 'L')
            pdf.ln(10)
            
            # Recommendations Section
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Recommendations', 0, 1, 'L')
            pdf.ln(5)
            
            pdf.set_font('Arial', '', 11)
            recommendations = []
            
            if savings_rate < 10:
                recommendations.append("- Increase savings to at least 10% of income")
            if top_category_pct > 50:
                recommendations.append(f"- Review {top_categories.index[0]} expenses for optimization opportunities")
            if savings_rate < 0:
                recommendations.append("- Create a budget to reduce expenses below income level")
            if len(recommendations) == 0:
                recommendations.append("- Continue maintaining your excellent financial habits!")
            
            for rec in recommendations:
                pdf.cell(0, 8, rec, 0, 1, 'L')
            
            pdf.ln(10)
            
            # Add pie chart image if it exists
            try:
                import os
                if os.path.exists('category_pie.png'):
                    # Add section title for the chart
                    pdf.set_font('Arial', 'B', 16)
                    pdf.set_text_color(0, 0, 0)
                    pdf.cell(0, 10, 'Spending Distribution', 0, 1, 'L')
                    pdf.ln(5)
                    
                    # Calculate image position and size
                    img_width = 120  # Width of the image in the PDF
                    img_x = (210 - img_width) / 2  # Center the image (A4 width is 210mm)
                    
                    # Add the pie chart image
                    pdf.image('category_pie.png', x=img_x, y=pdf.get_y(), w=img_width)
                    
                    # Move cursor down by the image height (approximately)
                    pdf.ln(img_width * 0.75)  # Approximate aspect ratio adjustment
                else:
                    pdf.set_font('Arial', 'I', 10)
                    pdf.set_text_color(150, 150, 150)
                    pdf.cell(0, 8, 'Pie chart image not available', 0, 1, 'C')
                    pdf.ln(10)
            except Exception as e:
                print(f"Warning: Could not add pie chart to PDF: {e}")
                pdf.ln(10)
            
            # Footer
            pdf.ln(15)
            pdf.set_font('Arial', 'I', 10)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 8, f'Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
            
            # Save the PDF
            pdf.output('finance_summary.pdf')
            print("✅ PDF report saved as 'finance_summary.pdf'")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating PDF report: {e}")
            return False
    
    def run_complete_analysis(self):
        """Run the complete analysis pipeline."""
        print("🚀 Starting Bank Statement Analysis...")
        print("-" * 50)
        
        # Step 1: Load CSV
        if not self.load_csv():
            return
        
        # Step 2: Categorize transactions
        if not self.categorize_transactions():
            return
        
        # Step 3: Calculate category totals
        category_totals = self.calculate_category_totals()
        
        # Step 4: Monthly analysis
        monthly_summary = self.monthly_income_vs_expenses()
        
        # Step 5: Visualizations
        print("\n📊 Generating visualizations...")
        if category_totals is not None:
            self.visualize_category_spending(category_totals)
        self.visualize_daily_spending_trend()
        self.visualize_monthly_financial_trends()
        
        # Step 6: Financial Insights
        self.generate_financial_insights()
        
        # Step 7: Monthly Comparison Analysis
        self.analyze_monthly_comparison()
        
        # Step 8: Create Pie Chart
        print("\n📊 Creating pie chart visualization...")
        self.create_category_pie_chart()
        
        # Step 9: Generate PDF Report
        print("\n📄 Generating PDF report...")
        total_income = self.categorized_df[self.categorized_df['Amount'] > 0]['Amount'].sum()
        total_expenses = abs(self.categorized_df[self.categorized_df['Amount'] < 0]['Amount'].sum())
        total_savings = total_income - total_expenses
        savings_rate = (total_savings / total_income * 100) if total_income > 0 else 0
        
        # Get top spending categories for PDF
        expenses_df = self.categorized_df[self.categorized_df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        top_categories = expenses_df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        
        self.generate_pdf_report(total_income, total_expenses, total_savings, savings_rate, top_categories)
        
        # Step 10: Summary
        self.generate_summary()

def create_sample_data():
    """Create a sample CSV file for testing with multiple months."""
    sample_data = {
        'Date': [
            # January 2024
            '2024-01-01', '2024-01-02', '2024-01-03', '2024-01-05', '2024-01-07',
            '2024-01-10', '2024-01-12', '2024-01-15', '2024-01-18', '2024-01-20',
            '2024-01-22', '2024-01-25', '2024-01-28', '2024-01-30',
            # February 2024
            '2024-02-01', '2024-02-03', '2024-02-05', '2024-02-08', '2024-02-10',
            '2024-02-12', '2024-02-15', '2024-02-18', '2024-02-20', '2024-02-22',
            '2024-02-25', '2024-02-28'
        ],
        'Description': [
            # January transactions
            'PAYROLL DEPOSIT', 'WALMART SUPERCENTER', 'NETFLIX SUBSCRIPTION', 'SHELL GAS STATION', 'STARBUCKS COFFEE',
            'AMAZON PURCHASE', 'ELECTRIC COMPANY', 'MCDONALDS', 'UBER RIDE', 'KROGER GROCERY',
            'ATM WITHDRAWAL FEE', 'PHARMACY CVS', 'RENT PAYMENT', 'SPOTIFY PREMIUM',
            # February transactions (with some increases)
            'PAYROLL DEPOSIT', 'TARGET STORE', 'NETFLIX SUBSCRIPTION', 'SHELL GAS STATION', 'STARBUCKS COFFEE',
            'UBER RIDE', 'ELECTRIC COMPANY', 'CHICK-FIL-A DINING', 'LYFT RIDE', 'WALMART SUPERCENTER',
            'INTERNET BILL', 'RENT PAYMENT'
        ],
        'Amount': [
            # January amounts
            3500.00, -85.50, -15.99, -45.20, -12.75,
            -125.30, -120.00, -8.99, -18.50, -75.40,
            -3.50, -25.80, -1200.00, -9.99,
            # February amounts (some categories increased)
            3500.00, -95.75, -15.99, -52.30, -15.25,
            -22.00, -135.00, -18.99, -25.50, -82.60,
            -75.00, -1200.00
        ]
    }
    
    df = pd.DataFrame(sample_data)
    df.to_csv('sample_bank_statement.csv', index=False)
    print("✅ Created sample_bank_statement.csv with multi-month data for testing")

def main():
    """Main function to run the analysis."""
    print("🏦 Bank Statement Analyzer")
    print("=" * 40)
    
    # Ask user for CSV file path
    csv_file = input("Enter CSV file path (or press Enter to create sample data): ").strip()
    
    if not csv_file:
        create_sample_data()
        csv_file = 'sample_bank_statement.csv'
    
    # Create analyzer and run analysis
    analyzer = BankStatementAnalyzer(csv_file)
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()
