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
from io import BytesIO

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
    /* Main app background */
    .main {
        background-color: #f4f7f9;
    }
    
    /* Enhanced header styling */
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
    
    /* Standard headers with improved colors */
    h1, h2, h3 {
        color: #004080;
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
    
    /* Enhanced button styling */
    .stButton > button {
        background-color: #008CBA !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-size: 16px !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #005f73 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Container styling for cards */
    .css-1offfwp, .element-container {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
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
    
    /* Enhanced sidebar styling */
    .css-1d391kg {
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
    }
    
    /* Metric value styling */
    [data-testid="metric-container"] {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #008CBA;
    }
    
    /* Data frame styling */
    .stDataFrame {
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
    }
    
    /* File uploader styling */
    .stFileUploader {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        border: 2px dashed #008CBA;
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
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.1);
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
        """Create interactive category spending bar chart using Plotly."""
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        
        # Get detailed category statistics
        category_stats = expenses_df.groupby('Category').agg({
            'Amount': ['sum', 'mean', 'count', 'min', 'max']
        }).round(2)
        category_stats.columns = ['Total', 'Average', 'Count', 'Min', 'Max']
        category_stats = category_stats.sort_values('Total', ascending=True)
        
        if len(category_stats) == 0:
            return None
        
        # Create interactive bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=category_stats['Total'],
            y=category_stats.index,
            orientation='h',
            marker=dict(
                color=category_stats['Total'],
                colorscale='Viridis',
                colorbar=dict(title="Amount ($)"),
                line=dict(color='rgba(50,50,50,0.8)', width=1)
            ),
            hovertemplate=(
                "<b>%{y}</b><br>" +
                "Total Spent: $%{x:,.2f}<br>" +
                "Average Transaction: $%{customdata[0]:,.2f}<br>" +
                "Number of Transactions: %{customdata[1]}<br>" +
                "Smallest Transaction: $%{customdata[2]:,.2f}<br>" +
                "Largest Transaction: $%{customdata[3]:,.2f}<br>" +
                "<extra></extra>"
            ),
            customdata=category_stats[['Average', 'Count', 'Min', 'Max']].values,
            name="Category Spending"
        ))
        
        fig.update_layout(
            title={
                'text': '📊 Interactive Category-wise Spending Analysis',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            xaxis_title="Amount ($)",
            yaxis_title="Category",
            height=450,
            showlegend=False,
            xaxis_tickformat='$,.0f',
            template='plotly_white',
            hovermode='closest',
            # Enable zooming and panning
            xaxis=dict(fixedrange=False),
            yaxis=dict(fixedrange=False)
        )
        
        # Add annotations for better interactivity
        fig.add_annotation(
            text="💡 Hover over bars for detailed statistics<br>🔍 Use toolbar to zoom and pan",
            xref="paper", yref="paper",
            x=1, y=1.15, xanchor="right", yanchor="top",
            showarrow=False,
            font=dict(size=10, color="gray")
        )
        
        return fig
    
    def create_monthly_trends_chart(self, df):
        """Create interactive monthly trends line chart with enhanced features."""
        monthly_data = df.groupby('Month').agg({
            'Amount': lambda x: [x[x > 0].sum(), abs(x[x < 0].sum()), len(x)]
        }).reset_index()
        
        monthly_data['Income'] = monthly_data['Amount'].apply(lambda x: x[0])
        monthly_data['Expenses'] = monthly_data['Amount'].apply(lambda x: x[1])
        monthly_data['Savings'] = monthly_data['Income'] - monthly_data['Expenses']
        monthly_data['Savings_Rate'] = ((monthly_data['Savings'] / monthly_data['Income']) * 100).round(1)
        monthly_data['Transaction_Count'] = monthly_data['Amount'].apply(lambda x: x[2])
        monthly_data['Month_Str'] = monthly_data['Month'].astype(str)
        
        # Create subplot with secondary y-axis for savings rate
        fig = make_subplots(
            specs=[[{"secondary_y": True}]],
            subplot_titles=['📈 Interactive Monthly Financial Trends']
        )
        
        # Income line
        fig.add_trace(
            go.Scatter(
                x=monthly_data['Month_Str'],
                y=monthly_data['Income'],
                mode='lines+markers',
                name='💰 Income',
                line=dict(color='#2E8B57', width=3, dash='solid'),
                marker=dict(size=10, symbol='circle'),
                hovertemplate=(
                    "<b>%{x}</b><br>" +
                    "Income: $%{y:,.2f}<br>" +
                    "Transactions: %{customdata}<br>" +
                    "<extra></extra>"
                ),
                customdata=monthly_data['Transaction_Count']
            ),
            secondary_y=False
        )
        
        # Expenses line
        fig.add_trace(
            go.Scatter(
                x=monthly_data['Month_Str'],
                y=monthly_data['Expenses'],
                mode='lines+markers',
                name='💸 Expenses',
                line=dict(color='#DC143C', width=3, dash='solid'),
                marker=dict(size=10, symbol='square'),
                hovertemplate=(
                    "<b>%{x}</b><br>" +
                    "Expenses: $%{y:,.2f}<br>" +
                    "Transactions: %{customdata}<br>" +
                    "<extra></extra>"
                ),
                customdata=monthly_data['Transaction_Count']
            ),
            secondary_y=False
        )
        
        # Savings line
        fig.add_trace(
            go.Scatter(
                x=monthly_data['Month_Str'],
                y=monthly_data['Savings'],
                mode='lines+markers',
                name='🏦 Net Savings',
                line=dict(color='#4169E1', width=3, dash='solid'),
                marker=dict(size=10, symbol='diamond'),
                hovertemplate=(
                    "<b>%{x}</b><br>" +
                    "Net Savings: $%{y:,.2f}<br>" +
                    "Savings Rate: %{customdata}%<br>" +
                    "<extra></extra>"
                ),
                customdata=monthly_data['Savings_Rate']
            ),
            secondary_y=False
        )
        
        # Savings rate line (on secondary y-axis)
        fig.add_trace(
            go.Scatter(
                x=monthly_data['Month_Str'],
                y=monthly_data['Savings_Rate'],
                mode='lines+markers',
                name='📊 Savings Rate (%)',
                line=dict(color='#FF8C00', width=2, dash='dot'),
                marker=dict(size=8, symbol='star'),
                hovertemplate=(
                    "<b>%{x}</b><br>" +
                    "Savings Rate: %{y:.1f}%<br>" +
                    "Net Savings: $%{customdata:,.2f}<br>" +
                    "<extra></extra>"
                ),
                customdata=monthly_data['Savings'],
                yaxis="y2"
            ),
            secondary_y=True
        )
        
        # Add zero line for reference
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Update layout
        fig.update_layout(
            title={
                'text': '📈 Interactive Monthly Financial Trends & Savings Rate',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            height=500,
            hovermode='x unified',
            template='plotly_white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            # Enable zooming and panning
            xaxis=dict(fixedrange=False),
            yaxis=dict(fixedrange=False)
        )
        
        # Set y-axes titles
        fig.update_xaxes(title_text="Month")
        fig.update_yaxes(title_text="Amount ($)", tickformat='$,.0f', secondary_y=False)
        fig.update_yaxes(title_text="Savings Rate (%)", tickformat='.1f', secondary_y=True)
        
        # Add annotation
        fig.add_annotation(
            text="💡 Click legend items to toggle visibility<br>🔍 Use toolbar for zoom, pan, and selection",
            xref="paper", yref="paper",
            x=0, y=1.15, xanchor="left", yanchor="top",
            showarrow=False,
            font=dict(size=10, color="gray")
        )
        
        return fig
    
    def create_pie_chart(self, df):
        """Create interactive pie chart for category spending with drill-down capability."""
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        
        # Get detailed statistics for each category
        category_stats = expenses_df.groupby('Category').agg({
            'Amount': ['sum', 'mean', 'count'],
            'Description': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'Various'
        }).round(2)
        
        category_stats.columns = ['Total', 'Average', 'Count', 'Most_Common']
        total_expenses = category_stats['Total'].sum()
        category_stats['Percentage'] = ((category_stats['Total'] / total_expenses) * 100).round(1)
        category_stats = category_stats.sort_values('Total', ascending=False)
        
        if len(category_stats) == 0:
            return None
        
        # Create interactive pie chart
        fig = go.Figure()
        
        colors = px.colors.qualitative.Set3[:len(category_stats)]
        
        fig.add_trace(go.Pie(
            labels=category_stats.index,
            values=category_stats['Total'],
            hole=0.4,  # Create a donut chart for better visual appeal
            marker=dict(
                colors=colors,
                line=dict(color='white', width=2)
            ),
            textinfo='label+percent',
            textposition='auto',
            hovertemplate=(
                "<b>%{label}</b><br>" +
                "Amount: $%{value:,.2f}<br>" +
                "Percentage: %{percent}<br>" +
                "Transactions: %{customdata[0]}<br>" +
                "Average: $%{customdata[1]:,.2f}<br>" +
                "Most Common: %{customdata[2]}<br>" +
                "<extra></extra>"
            ),
            customdata=category_stats[['Count', 'Average', 'Most_Common']].values,
            name="Category Spending",
            # Add pull effect for largest slice
            pull=[0.1 if i == 0 else 0 for i in range(len(category_stats))]
        ))
        
        # Add center text for donut chart
        total_spent = category_stats['Total'].sum()
        fig.add_annotation(
            text=f"Total<br>Expenses<br><b>${total_spent:,.0f}</b>",
            x=0.5, y=0.5,
            font_size=14,
            showarrow=False,
            font=dict(color="darkblue")
        )
        
        fig.update_layout(
            title={
                'text': '🥧 Interactive Spending Distribution by Category',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            height=450,
            template='plotly_white',
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.01
            ),
            # Enable interactivity
            annotations=[
                dict(
                    text="💡 Click slices to highlight<br>🔍 Hover for detailed info",
                    x=0, y=1.15,
                    xref="paper", yref="paper",
                    xanchor="left", yanchor="top",
                    showarrow=False,
                    font=dict(size=10, color="gray")
                )
            ]
        )
        
        return fig
    
    def create_amount_histogram(self, df):
        """Create interactive histogram for amount distribution with statistical overlay."""
        # Separate income and expenses
        income_data = df[df['Amount'] > 0]['Amount']
        expense_data = df[df['Amount'] < 0]['Amount'].abs()
        
        # Calculate statistics
        income_stats = {
            'mean': income_data.mean() if len(income_data) > 0 else 0,
            'median': income_data.median() if len(income_data) > 0 else 0,
            'std': income_data.std() if len(income_data) > 0 else 0,
            'count': len(income_data)
        }
        
        expense_stats = {
            'mean': expense_data.mean() if len(expense_data) > 0 else 0,
            'median': expense_data.median() if len(expense_data) > 0 else 0,
            'std': expense_data.std() if len(expense_data) > 0 else 0,
            'count': len(expense_data)
        }
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=(
                f'💰 Income Distribution (n={income_stats["count"]})',
                f'💸 Expense Distribution (n={expense_stats["count"]})'
            ),
            vertical_spacing=0.12,
            specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
        )
        
        # Income histogram with statistical lines
        if len(income_data) > 0:
            fig.add_trace(
                go.Histogram(
                    x=income_data,
                    nbinsx=25,
                    name='Income Frequency',
                    marker_color='rgba(46, 139, 87, 0.7)',
                    marker_line=dict(width=1, color='rgba(46, 139, 87, 1)'),
                    hovertemplate=(
                        'Range: $%{x:,.0f}<br>' +
                        'Frequency: %{y}<br>' +
                        'Percentage: %{customdata:.1f}%<br>' +
                        '<extra></extra>'
                    ),
                    customdata=[(income_data.value_counts(bins=25, normalize=True) * 100).values] * len(income_data)
                ),
                row=1, col=1
            )
            
            # Add mean line for income
            fig.add_vline(
                x=income_stats['mean'], line_dash="dash", line_color="darkgreen",
                annotation_text=f"Mean: ${income_stats['mean']:,.0f}",
                annotation_position="top",
                row=1, col=1
            )
            
            # Add median line for income
            fig.add_vline(
                x=income_stats['median'], line_dash="dot", line_color="green",
                annotation_text=f"Median: ${income_stats['median']:,.0f}",
                annotation_position="bottom",
                row=1, col=1
            )
        
        # Expense histogram with statistical lines
        if len(expense_data) > 0:
            fig.add_trace(
                go.Histogram(
                    x=expense_data,
                    nbinsx=25,
                    name='Expense Frequency',
                    marker_color='rgba(220, 20, 60, 0.7)',
                    marker_line=dict(width=1, color='rgba(220, 20, 60, 1)'),
                    hovertemplate=(
                        'Range: $%{x:,.0f}<br>' +
                        'Frequency: %{y}<br>' +
                        'Percentage: %{customdata:.1f}%<br>' +
                        '<extra></extra>'
                    ),
                    customdata=[(expense_data.value_counts(bins=25, normalize=True) * 100).values] * len(expense_data)
                ),
                row=2, col=1
            )
            
            # Add mean line for expenses
            fig.add_vline(
                x=expense_stats['mean'], line_dash="dash", line_color="darkred",
                annotation_text=f"Mean: ${expense_stats['mean']:,.0f}",
                annotation_position="top",
                row=2, col=1
            )
            
            # Add median line for expenses
            fig.add_vline(
                x=expense_stats['median'], line_dash="dot", line_color="red",
                annotation_text=f"Median: ${expense_stats['median']:,.0f}",
                annotation_position="bottom",
                row=2, col=1
            )
        
        # Update layout
        fig.update_layout(
            title={
                'text': '📊 Interactive Amount Distribution Analysis with Statistics',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#1f2937'}
            },
            height=700,
            showlegend=False,
            template='plotly_white',
            # Enable zooming and panning
            xaxis=dict(fixedrange=False),
            yaxis=dict(fixedrange=False),
            xaxis2=dict(fixedrange=False),
            yaxis2=dict(fixedrange=False)
        )
        
        # Update x-axes
        fig.update_xaxes(title_text="Amount ($)", tickformat='$,.0f', row=1, col=1)
        fig.update_xaxes(title_text="Amount ($)", tickformat='$,.0f', row=2, col=1)
        
        # Update y-axes
        fig.update_yaxes(title_text="Frequency", row=1, col=1)
        fig.update_yaxes(title_text="Frequency", row=2, col=1)
        
        # Add comprehensive annotation
        stats_text = (
            f"📈 Income Stats: Mean=${income_stats['mean']:,.0f}, "
            f"Median=${income_stats['median']:,.0f}, σ=${income_stats['std']:,.0f}<br>"
            f"💸 Expense Stats: Mean=${expense_stats['mean']:,.0f}, "
            f"Median=${expense_stats['median']:,.0f}, σ=${expense_stats['std']:,.0f}<br>"
            f"💡 Dashed=Mean, Dotted=Median | 🔍 Use toolbar for zoom/pan"
        )
        
        fig.add_annotation(
            text=stats_text,
            xref="paper", yref="paper",
            x=0.5, y=1.15, xanchor="center", yanchor="top",
            showarrow=False,
            font=dict(size=10, color="gray"),
            bordercolor="lightgray",
            borderwidth=1,
            bgcolor="rgba(255,255,255,0.8)"
        )
        
        return fig
    
    def create_transaction_timeline(self, df):
        """Create interactive transaction timeline scatter plot."""
        # Create a copy and prepare data
        timeline_df = df.copy()
        timeline_df['AbsAmount'] = timeline_df['Amount'].abs()
        timeline_df['Color'] = timeline_df['Amount'].apply(lambda x: 'Income' if x > 0 else 'Expense')
        
        # Create interactive scatter plot
        fig = go.Figure()
        
        # Income transactions
        income_df = timeline_df[timeline_df['Amount'] > 0]
        if len(income_df) > 0:
            fig.add_trace(go.Scatter(
                x=income_df['Date'],
                y=income_df['Amount'],
                mode='markers',
                name='💰 Income',
                marker=dict(
                    size=income_df['AbsAmount'] / income_df['AbsAmount'].max() * 30 + 5,
                    color='#2E8B57',
                    opacity=0.7,
                    line=dict(width=1, color='darkgreen'),
                    symbol='circle'
                ),
                hovertemplate=(
                    "<b>%{text}</b><br>" +
                    "Date: %{x}<br>" +
                    "Amount: $%{y:,.2f}<br>" +
                    "Category: %{customdata}<br>" +
                    "<extra></extra>"
                ),
                text=income_df['Description'],
                customdata=income_df['Category']
            ))
        
        # Expense transactions
        expense_df = timeline_df[timeline_df['Amount'] < 0]
        if len(expense_df) > 0:
            fig.add_trace(go.Scatter(
                x=expense_df['Date'],
                y=expense_df['Amount'],
                mode='markers',
                name='💸 Expenses',
                marker=dict(
                    size=expense_df['AbsAmount'] / expense_df['AbsAmount'].max() * 30 + 5,
                    color='#DC143C',
                    opacity=0.7,
                    line=dict(width=1, color='darkred'),
                    symbol='square'
                ),
                hovertemplate=(
                    "<b>%{text}</b><br>" +
                    "Date: %{x}<br>" +
                    "Amount: $%{y:,.2f}<br>" +
                    "Category: %{customdata}<br>" +
                    "<extra></extra>"
                ),
                text=expense_df['Description'],
                customdata=expense_df['Category']
            ))
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Calculate running balance
        timeline_df_sorted = timeline_df.sort_values('Date')
        timeline_df_sorted['RunningBalance'] = timeline_df_sorted['Amount'].cumsum()
        
        # Add running balance line
        fig.add_trace(go.Scatter(
            x=timeline_df_sorted['Date'],
            y=timeline_df_sorted['RunningBalance'],
            mode='lines',
            name='💼 Running Balance',
            line=dict(color='#4169E1', width=2, dash='dot'),
            hovertemplate=(
                "Date: %{x}<br>" +
                "Running Balance: $%{y:,.2f}<br>" +
                "<extra></extra>"
            ),
            yaxis='y2'
        ))
        
        # Create subplot with secondary y-axis
        fig.update_layout(
            title={
                'text': '📅 Interactive Transaction Timeline & Running Balance',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            xaxis_title="Date",
            yaxis_title="Transaction Amount ($)",
            yaxis2=dict(
                title="Running Balance ($)",
                overlaying="y",
                side="right",
                tickformat='$,.0f'
            ),
            height=500,
            template='plotly_white',
            hovermode='closest',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            # Enable zooming and panning
            xaxis=dict(fixedrange=False),
            yaxis=dict(fixedrange=False, tickformat='$,.0f')
        )
        
        # Add annotation
        fig.add_annotation(
            text="💡 Bubble size = transaction amount | Click legend to toggle<br>🔍 Use toolbar for zoom, pan, and selection",
            xref="paper", yref="paper",
            x=0, y=1.15, xanchor="left", yanchor="top",
            showarrow=False,
            font=dict(size=10, color="gray")
        )
        
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

    def generate_excel_report(self, df, total_income, total_expenses, total_savings, savings_rate):
        """Generate Excel report with multiple sheets."""
        try:
            # Create a BytesIO object to store the Excel file
            excel_buffer = BytesIO()
            
            # Create Excel writer object
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                # Sheet 1: Raw Transaction Data
                df_export = df.copy()
                df_export['Date'] = df_export['Date'].dt.strftime('%Y-%m-%d')
                df_export.to_excel(writer, sheet_name='Transaction Data', index=False)
                
                # Sheet 2: Financial Summary
                summary_data = {
                    'Metric': ['Total Income', 'Total Expenses', 'Net Savings', 'Savings Rate (%)', 
                              'Analysis Period Start', 'Analysis Period End', 'Total Transactions'],
                    'Value': [f'${total_income:,.2f}', f'${total_expenses:,.2f}', 
                             f'${total_savings:,.2f}', f'{savings_rate:.1f}%',
                             df['Date'].min().strftime('%Y-%m-%d'),
                             df['Date'].max().strftime('%Y-%m-%d'),
                             len(df)]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Financial Summary', index=False)
                
                # Sheet 3: Category Analysis
                expenses_df = df[df['Amount'] < 0].copy()
                expenses_df['Amount'] = expenses_df['Amount'].abs()
                category_analysis = expenses_df.groupby('Category').agg({
                    'Amount': ['sum', 'mean', 'count']
                }).round(2)
                category_analysis.columns = ['Total Spent', 'Average Transaction', 'Transaction Count']
                category_analysis['% of Total Expenses'] = (category_analysis['Total Spent'] / total_expenses * 100).round(1)
                category_analysis = category_analysis.sort_values('Total Spent', ascending=False)
                category_analysis.to_excel(writer, sheet_name='Category Analysis')
                
                # Sheet 4: Monthly Analysis
                monthly_data = df.groupby('Month').agg({
                    'Amount': lambda x: [x[x > 0].sum(), abs(x[x < 0].sum()), len(x)]
                }).reset_index()
                monthly_data['Income'] = monthly_data['Amount'].apply(lambda x: x[0])
                monthly_data['Expenses'] = monthly_data['Amount'].apply(lambda x: x[1])
                monthly_data['Savings'] = monthly_data['Income'] - monthly_data['Expenses']
                monthly_data['Savings Rate (%)'] = ((monthly_data['Savings'] / monthly_data['Income']) * 100).round(1)
                monthly_data['Transaction Count'] = monthly_data['Amount'].apply(lambda x: x[2])
                monthly_data = monthly_data[['Month', 'Income', 'Expenses', 'Savings', 'Savings Rate (%)', 'Transaction Count']]
                monthly_data['Month'] = monthly_data['Month'].astype(str)
                monthly_data.to_excel(writer, sheet_name='Monthly Analysis', index=False)
                
                # Sheet 5: Top Transactions
                top_income = df[df['Amount'] > 0].nlargest(10, 'Amount')[['Date', 'Description', 'Amount', 'Category']]
                top_expenses = df[df['Amount'] < 0].nsmallest(10, 'Amount')[['Date', 'Description', 'Amount', 'Category']]
                top_expenses['Amount'] = top_expenses['Amount'].abs()
                
                # Create a combined sheet for top transactions
                top_transactions = pd.DataFrame()
                if len(top_income) > 0:
                    top_income_formatted = top_income.copy()
                    top_income_formatted['Type'] = 'Income'
                    top_transactions = pd.concat([top_transactions, top_income_formatted])
                
                if len(top_expenses) > 0:
                    top_expenses_formatted = top_expenses.copy()
                    top_expenses_formatted['Type'] = 'Expense'
                    top_transactions = pd.concat([top_transactions, top_expenses_formatted])
                
                if len(top_transactions) > 0:
                    top_transactions['Date'] = pd.to_datetime(top_transactions['Date']).dt.strftime('%Y-%m-%d')
                    top_transactions = top_transactions[['Date', 'Description', 'Amount', 'Category', 'Type']]
                    top_transactions.to_excel(writer, sheet_name='Top Transactions', index=False)
            
            excel_buffer.seek(0)
            return excel_buffer.getvalue()
            
        except Exception as e:
            st.error(f"Error generating Excel: {e}")
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
    2. **Filter Data**: Use interactive filters below to focus analysis
    3. **Explore Charts**: All visualizations are interactive with zoom/pan
    4. **Download Reports**: Generate PDF or Excel summaries
    
    **Interactive Features:**
    - 🔍 **Date & Category Filters**: Focus on specific time periods or categories
    - 📊 **Interactive Charts**: Hover for details, zoom, pan, toggle data
    - 📈 **Real-time Updates**: All charts update based on your filters
    
    **Report Options:**
    - 📄 **PDF**: Visual summary with charts
    - 📊 **Excel**: Detailed data with multiple sheets
    
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
                # Add date range filter in sidebar
                st.sidebar.markdown("---")
                st.sidebar.header("🔍 Interactive Filters")
                
                min_date = processed_df['Date'].min().date()
                max_date = processed_df['Date'].max().date()
                
                date_range = st.sidebar.date_input(
                    "📅 Select Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    help="Filter transactions by date range"
                )
                
                # Apply date filter
                if len(date_range) == 2:
                    start_date, end_date = date_range
                    filtered_df = processed_df[
                        (processed_df['Date'].dt.date >= start_date) & 
                        (processed_df['Date'].dt.date <= end_date)
                    ].copy()
                    
                    if len(filtered_df) == 0:
                        st.warning("⚠️ No transactions found in the selected date range.")
                        filtered_df = processed_df
                else:
                    filtered_df = processed_df
                
                # Add category filter
                available_categories = processed_df['Category'].unique().tolist()
                selected_categories = st.sidebar.multiselect(
                    "🏷️ Filter by Categories",
                    options=available_categories,
                    default=available_categories,
                    help="Select categories to include in analysis"
                )
                
                # Apply category filter
                if selected_categories:
                    filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]
                
                # Show filter info
                if len(filtered_df) != len(processed_df):
                    st.sidebar.success(f"✅ Showing {len(filtered_df):,} of {len(processed_df):,} transactions")
                else:
                    st.sidebar.info(f"📊 Showing all {len(processed_df):,} transactions")
                
                # Calculate metrics using filtered data
                total_income, total_expenses, total_savings, savings_rate = analyzer.calculate_metrics(filtered_df)
                
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
                histogram_chart = analyzer.create_amount_histogram(filtered_df)
                if histogram_chart:
                    st.plotly_chart(histogram_chart, use_container_width=True)
                
                # Create columns for other charts
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    # Category spending chart
                    category_chart = analyzer.create_category_spending_chart(filtered_df)
                    if category_chart:
                        st.plotly_chart(category_chart, use_container_width=True)
                
                with chart_col2:
                    # Pie chart
                    pie_chart = analyzer.create_pie_chart(filtered_df)
                    if pie_chart:
                        st.plotly_chart(pie_chart, use_container_width=True)
                
                # Monthly trends chart (full width)
                st.subheader("📊 Monthly Trends & Savings Rate")
                monthly_chart = analyzer.create_monthly_trends_chart(filtered_df)
                if monthly_chart:
                    st.plotly_chart(monthly_chart, use_container_width=True)
                
                # Transaction timeline chart (full width)
                st.subheader("📅 Transaction Timeline & Running Balance")
                timeline_chart = analyzer.create_transaction_timeline(filtered_df)
                if timeline_chart:
                    st.plotly_chart(timeline_chart, use_container_width=True)
                
                # Insights section
                st.markdown('<div class="insight-header">💡 Financial Insights & Recommendations</div>', unsafe_allow_html=True)
                insights = analyzer.get_insights(filtered_df, total_income, total_expenses, total_savings, savings_rate)
                
                for insight in insights:
                    if insight:  # Skip empty lines
                        st.markdown(insight)
                
                # Data preview
                with st.expander("📋 View Filtered Transaction Data"):
                    st.dataframe(filtered_df, use_container_width=True)
                
                # PDF Download
                st.markdown('<div class="chart-header">📄 Generate & Download Report</div>', unsafe_allow_html=True)
                
                # Create two columns for download buttons
                pdf_col, excel_col = st.columns(2)
                
                with pdf_col:
                    if st.button("🔽 Generate PDF Report", type="primary"):
                        with st.spinner("Generating PDF report..."):
                            pdf_data = analyzer.generate_pdf_report(
                                filtered_df, total_income, total_expenses, total_savings, savings_rate
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
                
                with excel_col:
                    if st.button("📊 Generate Excel Report", type="primary"):
                        with st.spinner("Generating Excel report..."):
                            excel_data = analyzer.generate_excel_report(
                                filtered_df, total_income, total_expenses, total_savings, savings_rate
                            )
                            
                            if excel_data:
                                st.download_button(
                                    label="📥 Download Excel Report",
                                    data=excel_data,
                                    file_name=f"financial_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    type="secondary"
                                )
                                st.success("✅ Excel report generated successfully!")
        
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
