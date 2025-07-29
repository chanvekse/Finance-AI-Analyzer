import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fpdf import FPDF
import tempfile
import os
import io
import base64

# Set page configuration
st.set_page_config(
    page_title="💰 Bank Statement Analyzer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #4CAF50, #2196F3, #FF9800);
        background-size: 200% 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradient 3s ease infinite;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 0.5rem 0;
    }
    
    .chart-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f2937;
        margin: 1.5rem 0 1rem 0;
        padding: 0.8rem;
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 8px;
        text-align: center;
        color: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .insight-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: white;
        margin: 1.5rem 0 1rem 0;
        padding: 0.8rem;
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        padding: 10px 0;
        font-size: 0.9rem;
        z-index: 999;
        box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stApp > div:first-child {
        margin-bottom: 60px;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitBankAnalyzer:
    def __init__(self):
        """Initialize the Streamlit Bank Analyzer."""
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
    
    def categorize_transaction(self, description):
        """Categorize a transaction based on description keywords."""
        description_lower = str(description).lower()
        
        for category, keywords in self.category_keywords.items():
            if category == 'Uncategorized':
                continue
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'Uncategorized'
    
    def process_dataframe(self, df):
        """Process the uploaded DataFrame."""
        try:
            # Validate columns
            required_columns = ['Date', 'Description', 'Amount']
            if not all(col in df.columns for col in required_columns):
                st.error(f"❌ CSV must contain columns: {required_columns}")
                return None
            
            # Convert Date column to datetime
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Convert Amount to numeric
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
            
            # Remove rows with invalid data
            df = df.dropna()
            
            # Add categorization
            df['Category'] = df['Description'].apply(self.categorize_transaction)
            
            # Separate income and expenses
            df['Type'] = df['Amount'].apply(lambda x: 'Income' if x > 0 else 'Expense')
            df['Month'] = df['Date'].dt.to_period('M')
            
            return df
            
        except Exception as e:
            st.error(f"❌ Error processing data: {e}")
            return None
    
    def calculate_metrics(self, df):
        """Calculate financial metrics."""
        total_income = df[df['Amount'] > 0]['Amount'].sum()
        total_expenses = abs(df[df['Amount'] < 0]['Amount'].sum())
        total_savings = total_income - total_expenses
        savings_rate = (total_savings / total_income * 100) if total_income > 0 else 0
        
        return total_income, total_expenses, total_savings, savings_rate
    
    def create_category_spending_chart(self, df):
        """Create category spending bar chart using Plotly."""
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        category_spending = expenses_df.groupby('Category')['Amount'].sum().sort_values(ascending=True)
        
        if len(category_spending) == 0:
            return None
        
        fig = px.bar(
            x=category_spending.values,
            y=category_spending.index,
            orientation='h',
            title='📊 Category-wise Spending',
            labels={'x': 'Amount ($)', 'y': 'Category'},
            color=category_spending.values,
            color_continuous_scale='RdYlBu_r'
        )
        
        fig.update_layout(
            height=400,
            showlegend=False,
            xaxis_tickformat='$,.0f'
        )
        
        return fig
    
    def create_monthly_trends_chart(self, df):
        """Create monthly trends line chart."""
        monthly_data = df.groupby('Month').agg({
            'Amount': lambda x: [x[x > 0].sum(), abs(x[x < 0].sum())]
        }).reset_index()
        
        monthly_data['Income'] = monthly_data['Amount'].apply(lambda x: x[0])
        monthly_data['Expenses'] = monthly_data['Amount'].apply(lambda x: x[1])
        monthly_data['Savings'] = monthly_data['Income'] - monthly_data['Expenses']
        monthly_data['Month_Str'] = monthly_data['Month'].astype(str)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=monthly_data['Month_Str'],
            y=monthly_data['Income'],
            mode='lines+markers',
            name='Income',
            line=dict(color='green', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=monthly_data['Month_Str'],
            y=monthly_data['Expenses'],
            mode='lines+markers',
            name='Expenses',
            line=dict(color='red', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=monthly_data['Month_Str'],
            y=monthly_data['Savings'],
            mode='lines+markers',
            name='Savings',
            line=dict(color='blue', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='📈 Monthly Financial Trends',
            xaxis_title='Month',
            yaxis_title='Amount ($)',
            height=400,
            hovermode='x unified',
            yaxis_tickformat='$,.0f'
        )
        
        return fig
    
    def create_pie_chart(self, df):
        """Create pie chart for category spending."""
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        category_spending = expenses_df.groupby('Category')['Amount'].sum()
        
        if len(category_spending) == 0:
            return None
        
        fig = px.pie(
            values=category_spending.values,
            names=category_spending.index,
            title='🥧 Spending Distribution by Category'
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        
        return fig
    
    def create_amount_histogram(self, df):
        """Create histogram for amount distribution."""
        # Separate income and expenses
        income_data = df[df['Amount'] > 0]['Amount']
        expense_data = df[df['Amount'] < 0]['Amount'].abs()
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('💰 Income Distribution', '💸 Expense Distribution'),
            vertical_spacing=0.08,
            specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
        )
        
        # Income histogram
        if len(income_data) > 0:
            fig.add_trace(
                go.Histogram(
                    x=income_data,
                    nbinsx=20,
                    name='Income',
                    marker_color='rgba(76, 175, 80, 0.7)',
                    marker_line=dict(width=1, color='rgba(76, 175, 80, 1)'),
                    hovertemplate='Amount: $%{x:,.2f}<br>Count: %{y}<extra></extra>'
                ),
                row=1, col=1
            )
        
        # Expense histogram
        if len(expense_data) > 0:
            fig.add_trace(
                go.Histogram(
                    x=expense_data,
                    nbinsx=20,
                    name='Expenses',
                    marker_color='rgba(244, 67, 54, 0.7)',
                    marker_line=dict(width=1, color='rgba(244, 67, 54, 1)'),
                    hovertemplate='Amount: $%{x:,.2f}<br>Count: %{y}<extra></extra>'
                ),
                row=2, col=1
            )
        
        # Update layout
        fig.update_layout(
            title={
                'text': '📊 Amount Distribution Analysis',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#1f2937'}
            },
            height=600,
            showlegend=False,
            template='plotly_white'
        )
        
        # Update x-axes
        fig.update_xaxes(title_text="Amount ($)", tickformat='$,.0f', row=1, col=1)
        fig.update_xaxes(title_text="Amount ($)", tickformat='$,.0f', row=2, col=1)
        
        # Update y-axes
        fig.update_yaxes(title_text="Frequency", row=1, col=1)
        fig.update_yaxes(title_text="Frequency", row=2, col=1)
        
        return fig
    
    def get_insights(self, df, total_income, total_expenses, total_savings, savings_rate):
        """Generate financial insights."""
        insights = []
        
        # Top 3 expense categories
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        top_categories = expenses_df.groupby('Category')['Amount'].sum().sort_values(ascending=False).head(3)
        
        insights.append("🎯 **Top 3 Expense Categories:**")
        for i, (category, amount) in enumerate(top_categories.items(), 1):
            percentage = (amount / total_income * 100) if total_income > 0 else 0
            insights.append(f"{i}. **{category}**: ${amount:,.2f} ({percentage:.1f}% of income)")
        
        insights.append("")
        insights.append("💡 **Financial Insights:**")
        
        # Savings analysis
        if savings_rate >= 20:
            insights.append("✅ **Excellent!** You're saving 20%+ of your income!")
        elif savings_rate >= 10:
            insights.append("✅ **Good!** You're saving 10%+ of your income.")
        elif savings_rate >= 0:
            insights.append("⚠️ **Fair:** You're saving money, but could improve.")
        else:
            insights.append("🚨 **Alert:** You're spending more than you earn!")
        
        # Category insights
        if len(top_categories) > 0:
            top_category = top_categories.index[0]
            top_percentage = (top_categories.iloc[0] / total_income * 100) if total_income > 0 else 0
            
            if top_percentage > 50:
                insights.append(f"⚠️ High spending concentration in **{top_category}** ({top_percentage:.1f}%)")
            else:
                insights.append(f"✅ Balanced spending distribution across categories")
        
        # Recommendations
        insights.append("")
        insights.append("🔧 **Recommendations:**")
        
        if savings_rate < 10:
            insights.append("• Increase savings to at least 10% of income")
        
        if len(top_categories) > 0:
            top_percentage = (top_categories.iloc[0] / total_income * 100) if total_income > 0 else 0
            if top_percentage > 50:
                insights.append(f"• Review {top_categories.index[0]} expenses for optimization")
        
        if 'Uncategorized' in top_categories.head(3).index:
            insights.append("• Track and categorize unknown expenses")
        
        if len([r for r in [savings_rate < 10, top_percentage > 50] if r]) == 0:
            insights.append("• Keep up the excellent financial management!")
        
        return insights
    
    def create_and_save_pie_chart(self, df):
        """Create and save pie chart for PDF inclusion."""
        try:
            expenses_df = df[df['Amount'] < 0].copy()
            expenses_df['Amount'] = expenses_df['Amount'].abs()
            category_spending = expenses_df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
            
            if len(category_spending) == 0:
                return False
            
            # Create matplotlib pie chart
            plt.figure(figsize=(8, 6))
            colors = plt.cm.Set3(range(len(category_spending)))
            
            wedges, texts, autotexts = plt.pie(
                category_spending.values, 
                labels=category_spending.index,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                explode=[0.05 if i == 0 else 0 for i in range(len(category_spending))],
                shadow=True
            )
            
            # Customize text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
            
            for text in texts:
                text.set_fontsize(10)
                text.set_fontweight('bold')
            
            plt.title('Spending Distribution by Category', fontsize=14, fontweight='bold', pad=20)
            total_spending = category_spending.sum()
            plt.suptitle(f'Total Spending: ${total_spending:,.2f}', fontsize=11, y=0.02)
            
            plt.axis('equal')
            plt.tight_layout()
            plt.savefig('streamlit_category_pie.png', dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            return True
            
        except Exception as e:
            print(f"Error creating pie chart: {e}")
            return False

    def generate_pdf_report(self, df, total_income, total_expenses, total_savings, savings_rate):
        """Generate PDF report."""
        try:
            # First create the pie chart
            pie_chart_created = self.create_and_save_pie_chart(df)
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Title
            pdf.set_font('Arial', 'B', 20)
            pdf.cell(0, 15, 'Bank Statement Analysis Report', 0, 1, 'C')
            pdf.ln(10)
            
            # Date range
            date_min = df['Date'].min().strftime('%Y-%m-%d')
            date_max = df['Date'].max().strftime('%Y-%m-%d')
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 8, f'Analysis Period: {date_min} to {date_max}', 0, 1, 'C')
            pdf.ln(15)
            
            # Financial Overview
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Financial Overview', 0, 1, 'L')
            pdf.ln(5)
            
            # Summary box
            pdf.set_fill_color(240, 240, 240)
            pdf.rect(10, pdf.get_y(), 190, 50, 'F')
            
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(95, 10, f'Total Income:', 0, 0, 'L')
            pdf.cell(95, 10, f'${total_income:,.2f}', 0, 1, 'R')
            
            pdf.cell(95, 10, f'Total Expenses:', 0, 0, 'L')
            pdf.cell(95, 10, f'${total_expenses:,.2f}', 0, 1, 'R')
            
            pdf.cell(95, 10, f'Net Savings:', 0, 0, 'L')
            pdf.cell(95, 10, f'${total_savings:,.2f}', 0, 1, 'R')
            
            pdf.cell(95, 10, f'Savings Rate:', 0, 0, 'L')
            pdf.cell(95, 10, f'{savings_rate:.1f}%', 0, 1, 'R')
            
            pdf.ln(15)
            
            # Top Categories
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Top Spending Categories', 0, 1, 'L')
            pdf.ln(5)
            
            expenses_df = df[df['Amount'] < 0].copy()
            expenses_df['Amount'] = expenses_df['Amount'].abs()
            top_categories = expenses_df.groupby('Category')['Amount'].sum().sort_values(ascending=False).head(3)
            
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(10, 8, '#', 1, 0, 'C')
            pdf.cell(110, 8, 'Category', 1, 0, 'L')
            pdf.cell(35, 8, 'Amount', 1, 0, 'R')
            pdf.cell(35, 8, '% of Income', 1, 1, 'R')
            
            pdf.set_font('Arial', '', 10)
            for i, (category, amount) in enumerate(top_categories.items(), 1):
                percentage = (amount / total_income * 100) if total_income > 0 else 0
                pdf.cell(10, 8, str(i), 1, 0, 'C')
                pdf.cell(110, 8, category, 1, 0, 'L')
                pdf.cell(35, 8, f'${amount:,.2f}', 1, 0, 'R')
                pdf.cell(35, 8, f'{percentage:.1f}%', 1, 1, 'R')
            
            # Add pie chart if created successfully
            if pie_chart_created and os.path.exists('streamlit_category_pie.png'):
                pdf.ln(15)
                pdf.set_font('Arial', 'B', 16)
                pdf.cell(0, 10, 'Spending Distribution Chart', 0, 1, 'L')
                pdf.ln(5)
                
                # Calculate image position and size
                img_width = 120  # Width in mm
                img_x = (210 - img_width) / 2  # Center on A4 page
                
                # Add the pie chart image
                pdf.image('streamlit_category_pie.png', x=img_x, y=pdf.get_y(), w=img_width)
                
                # Move cursor down
                pdf.ln(img_width * 0.75)  # Approximate height adjustment
                
                # Clean up the temporary image file
                try:
                    os.unlink('streamlit_category_pie.png')
                except:
                    pass
            
            # Footer
            pdf.ln(20)
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 8, f'Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
            
            # Save to bytes
            try:
                # For newer fpdf2 versions, output() returns bytes or bytearray
                pdf_data = pdf.output(dest='S')
                
                if isinstance(pdf_data, str):
                    # If it's a string, encode it
                    return pdf_data.encode('latin-1')
                elif isinstance(pdf_data, bytearray):
                    # If it's a bytearray, convert to bytes
                    return bytes(pdf_data)
                else:
                    # If it's already bytes, return as is
                    return pdf_data
                    
            except Exception as pdf_error:
                # Fallback method using BytesIO
                try:
                    pdf_output = io.BytesIO()
                    pdf.output(pdf_output)
                    return pdf_output.getvalue()
                except:
                    # Final fallback - save to temporary file and read
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                        pdf.output(tmp_file.name)
                        with open(tmp_file.name, 'rb') as f:
                            pdf_bytes = f.read()
                        os.unlink(tmp_file.name)
                        return pdf_bytes
            
        except Exception as e:
            st.error(f"Error generating PDF: {e}")
            return None

def main():
    """Main Streamlit application."""
    
    # Styled Header
    st.markdown('<h1 class="main-header">💰 Bank Statement Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">📊 Upload your bank statement CSV and get comprehensive financial insights!</div>', unsafe_allow_html=True)
    
    # Initialize analyzer
    analyzer = StreamlitBankAnalyzer()
    
    # Sidebar
    st.sidebar.header("📋 Instructions")
    st.sidebar.markdown("""
    1. **Upload CSV**: Your file should have columns: Date, Description, Amount
    2. **View Analysis**: Check the metrics, charts, and insights
    3. **Download Report**: Generate a PDF summary
    
    **CSV Format Example:**
    ```
    Date,Description,Amount
    2024-01-01,PAYROLL DEPOSIT,3500.00
    2024-01-02,WALMART SUPERCENTER,-85.50
    2024-01-03,NETFLIX SUBSCRIPTION,-15.99
    ```
    """)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a CSV file", 
        type="csv",
        help="Upload your bank statement CSV file with Date, Description, and Amount columns"
    )
    
    if uploaded_file is not None:
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            
            # Display basic info
            st.success(f"✅ File uploaded successfully! Found {len(df)} transactions.")
            
            # Process the data
            processed_df = analyzer.process_dataframe(df)
            
            if processed_df is not None:
                # Calculate metrics
                total_income, total_expenses, total_savings, savings_rate = analyzer.calculate_metrics(processed_df)
                
                # Display metrics
                st.markdown('<div class="chart-header">📊 Financial Overview</div>', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        label="💵 Total Income",
                        value=f"${total_income:,.2f}",
                        delta=None
                    )
                
                with col2:
                    st.metric(
                        label="💸 Total Expenses",
                        value=f"${total_expenses:,.2f}",
                        delta=None
                    )
                
                with col3:
                    savings_color = "normal" if total_savings >= 0 else "inverse"
                    st.metric(
                        label="🏦 Net Savings",
                        value=f"${total_savings:,.2f}",
                        delta=f"{savings_rate:.1f}% savings rate"
                    )
                
                with col4:
                    st.metric(
                        label="📈 Savings Rate",
                        value=f"{savings_rate:.1f}%",
                        delta="Excellent!" if savings_rate >= 20 else "Good!" if savings_rate >= 10 else "Needs improvement"
                    )
                
                # Charts section
                st.markdown('<div class="chart-header">📈 Financial Visualizations</div>', unsafe_allow_html=True)
                
                # Amount Distribution Histogram (full width)
                st.subheader("💹 Amount Distribution Analysis")
                histogram_chart = analyzer.create_amount_histogram(processed_df)
                if histogram_chart:
                    st.plotly_chart(histogram_chart, use_container_width=True)
                
                # Create columns for other charts
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    # Category spending chart
                    category_chart = analyzer.create_category_spending_chart(processed_df)
                    if category_chart:
                        st.plotly_chart(category_chart, use_container_width=True)
                
                with chart_col2:
                    # Pie chart
                    pie_chart = analyzer.create_pie_chart(processed_df)
                    if pie_chart:
                        st.plotly_chart(pie_chart, use_container_width=True)
                
                # Monthly trends chart (full width)
                st.subheader("📊 Monthly Trends")
                monthly_chart = analyzer.create_monthly_trends_chart(processed_df)
                if monthly_chart:
                    st.plotly_chart(monthly_chart, use_container_width=True)
                
                # Insights section
                st.markdown('<div class="insight-header">💡 Financial Insights & Recommendations</div>', unsafe_allow_html=True)
                insights = analyzer.get_insights(processed_df, total_income, total_expenses, total_savings, savings_rate)
                
                for insight in insights:
                    if insight:  # Skip empty lines
                        st.markdown(insight)
                
                # Data preview
                with st.expander("📋 View Transaction Data"):
                    st.dataframe(processed_df, use_container_width=True)
                
                # PDF Download
                st.markdown('<div class="chart-header">📄 Generate & Download Report</div>', unsafe_allow_html=True)
                
                if st.button("🔽 Generate PDF Report", type="primary"):
                    with st.spinner("Generating PDF report..."):
                        pdf_data = analyzer.generate_pdf_report(
                            processed_df, total_income, total_expenses, total_savings, savings_rate
                        )
                        
                        if pdf_data:
                            st.download_button(
                                label="📥 Download PDF Report",
                                data=pdf_data,
                                file_name=f"financial_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                mime="application/pdf",
                                type="secondary"
                            )
                            st.success("✅ PDF report generated successfully!")
        
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
            st.info("Please ensure your CSV file has the correct format with Date, Description, and Amount columns.")
    
    else:
        # Show sample data format
        st.info("👆 Upload a CSV file to get started!")
        
        st.subheader("📝 Sample Data Format")
        sample_data = pd.DataFrame({
            'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Description': ['PAYROLL DEPOSIT', 'WALMART SUPERCENTER', 'NETFLIX SUBSCRIPTION'],
            'Amount': [3500.00, -85.50, -15.99]
        })
        st.dataframe(sample_data)
        
        # Create sample CSV download
        csv_buffer = io.StringIO()
        sample_data.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Download Sample CSV",
            data=csv_buffer.getvalue(),
            file_name="sample_bank_statement.csv",
            mime="text/csv"
        )
    
    # Footer
    st.markdown("""
    <div class="footer">
        Created by Venkat Chandrasekaran | 💰 Bank Statement Analyzer | Powered by Streamlit & AI
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
