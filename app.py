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
import json
import hashlib

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
            'Groceries': ['walmart', 'kroger', 'trader joe', 'target', 'safeway', 'whole foods', 'costco', 'sams club', 'publix', 'aldi', 'food lion', 'harris teeter', 'giant', 'stop shop', 'wegmans', 'meijer', 'heb', 'food max', 'supermarket', 'grocery'],
            'Subscriptions': ['netflix', 'youtube', 'apple music', 'spotify', 'amazon prime', 'disney plus', 'hulu', 'hbo', 'paramount', 'peacock', 'adobe', 'microsoft', 'google one', 'icloud', 'dropbox', 'gym', 'fitness', 'subscription', 'monthly', 'annual', 'prime video'],
            'Utilities': ['electricity', 'electric', 'gas company', 'water', 'sewer', 'internet', 'cable', 'phone', 'cellular', 'verizon', 'att', 'tmobile', 'sprint', 'comcast', 'xfinity', 'spectrum', 'cox', 'utility', 'power', 'energy'],
            'Gas & Fuel': ['shell', 'exxon', 'mobil', 'chevron', 'bp', 'texaco', 'citgo', 'sunoco', 'marathon', 'speedway', 'wawa', '7-eleven', 'gas station', 'fuel', 'gasoline', 'petrol'],
            'Dining Out': ['starbucks', 'mcdonalds', 'burger king', 'subway', 'chipotle', 'panera', 'chick-fil-a', 'taco bell', 'pizza', 'restaurant', 'cafe', 'diner', 'fast food', 'delivery', 'takeout', 'doordash', 'uber eats', 'grubhub'],
            'Transportation': ['uber', 'lyft', 'taxi', 'bus', 'metro', 'train', 'parking', 'toll', 'car rental', 'maintenance', 'auto repair', 'oil change'],
            'Healthcare': ['pharmacy', 'cvs', 'walgreens', 'doctor', 'medical', 'dental', 'hospital', 'clinic', 'health', 'prescription', 'copay'],
            'Insurance': ['insurance', 'policy', 'premium', 'auto insurance', 'health insurance', 'life insurance', 'home insurance'],
            'Housing': ['rent', 'mortgage', 'hoa', 'property tax', 'home depot', 'lowes', 'maintenance', 'repair'],
            'Credit Card / Transfers': ['chase', 'zelle', 'venmo', 'paypal', 'credit card', 'payment', 'transfer'],
            'Income': ['salary', 'deposit', 'payroll', 'wages', 'bonus', 'refund', 'cashback'],
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
            height=500,  # Increased height for better spacing
            showlegend=False,
            xaxis_tickformat='$,.0f',
            template='plotly_white',
            hovermode='closest',
            # Enable zooming and panning
            xaxis=dict(fixedrange=False),
            yaxis=dict(fixedrange=False),
            # Add margins to prevent text overlap
            margin=dict(l=120, r=20, t=80, b=60)
        )
        
        # Add annotations for better interactivity with proper spacing
        fig.add_annotation(
            text="💡 Hover for detailed stats | 🔍 Use toolbar to zoom/pan",
            xref="paper", yref="paper",
            x=1, y=-0.15, xanchor="right", yanchor="top",
            showarrow=False,
            font=dict(size=9, color="gray")
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
            height=550,  # Increased height for better spacing
            hovermode='x unified',
            template='plotly_white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,  # Moved legend below chart
                xanchor="center",
                x=0.5
            ),
            # Enable zooming and panning
            xaxis=dict(fixedrange=False),
            yaxis=dict(fixedrange=False),
            # Add margins to prevent overlap
            margin=dict(l=60, r=60, t=80, b=120)
        )
        
        # Set y-axes titles
        fig.update_xaxes(title_text="Month")
        fig.update_yaxes(title_text="Amount ($)", tickformat='$,.0f', secondary_y=False)
        fig.update_yaxes(title_text="Savings Rate (%)", tickformat='.1f', secondary_y=True)
        
        # Add annotation with better positioning
        fig.add_annotation(
            text="💡 Click legend to toggle | 🔍 Toolbar for zoom/pan/select",
            xref="paper", yref="paper",
            x=0.5, y=-0.35, xanchor="center", yanchor="top",
            showarrow=False,
            font=dict(size=9, color="gray")
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
            hole=0.3,  # Reduced hole size for better text space
            marker=dict(
                colors=colors,
                line=dict(color='white', width=2)
            ),
            textinfo='label+percent',
            textposition='auto',
            textfont=dict(size=11),  # Slightly larger text
            insidetextorientation='radial',  # Better text orientation
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
            pull=[0.05 if i == 0 else 0 for i in range(len(category_stats))],  # Reduced pull
            sort=False  # Keep original order to prevent label jumping
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
            height=500,  # Increased height
            template='plotly_white',
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02,
                font=dict(size=10)  # Smaller legend font
            ),
            # Add margins for better spacing
            margin=dict(l=20, r=150, t=80, b=80),
            # Enable interactivity
            annotations=[
                dict(
                    text="💡 Click slices to highlight | 🔍 Hover for details",
                    x=0.5, y=-0.15,
                    xref="paper", yref="paper",
                    xanchor="center", yanchor="top",
                    showarrow=False,
                    font=dict(size=9, color="gray")
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
                annotation_text=f"μ: ${income_stats['mean']:,.0f}",
                annotation_position="top right",
                annotation_font_size=9,
                row=1, col=1
            )
            
            # Add median line for income
            fig.add_vline(
                x=income_stats['median'], line_dash="dot", line_color="green",
                annotation_text=f"M: ${income_stats['median']:,.0f}",
                annotation_position="bottom right",
                annotation_font_size=9,
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
                annotation_text=f"μ: ${expense_stats['mean']:,.0f}",
                annotation_position="top right",
                annotation_font_size=9,
                row=2, col=1
            )
            
            # Add median line for expenses
            fig.add_vline(
                x=expense_stats['median'], line_dash="dot", line_color="red",
                annotation_text=f"M: ${expense_stats['median']:,.0f}",
                annotation_position="bottom right",
                annotation_font_size=9,
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
            height=750,  # Increased height for better spacing
            showlegend=False,
            template='plotly_white',
            # Enable zooming and panning
            xaxis=dict(fixedrange=False),
            yaxis=dict(fixedrange=False),
            xaxis2=dict(fixedrange=False),
            yaxis2=dict(fixedrange=False),
            # Add margins to prevent overlap
            margin=dict(l=60, r=60, t=120, b=120)
        )
        
        # Update x-axes
        fig.update_xaxes(title_text="Amount ($)", tickformat='$,.0f', row=1, col=1)
        fig.update_xaxes(title_text="Amount ($)", tickformat='$,.0f', row=2, col=1)
        
        # Update y-axes
        fig.update_yaxes(title_text="Frequency", row=1, col=1)
        fig.update_yaxes(title_text="Frequency", row=2, col=1)
        
        # Add comprehensive annotation with better formatting
        stats_text = (
            f"📈 Income: μ=${income_stats['mean']:,.0f}, M=${income_stats['median']:,.0f}, "
            f"σ=${income_stats['std']:,.0f} | "
            f"💸 Expense: μ=${expense_stats['mean']:,.0f}, M=${expense_stats['median']:,.0f}, "
            f"σ=${expense_stats['std']:,.0f}"
        )
        
        fig.add_annotation(
            text=stats_text,
            xref="paper", yref="paper",
            x=0.5, y=-0.12, xanchor="center", yanchor="top",
            showarrow=False,
            font=dict(size=9, color="gray"),
            bordercolor="lightgray",
            borderwidth=1,
            bgcolor="rgba(255,255,255,0.9)"
        )
        
        # Add legend for symbols
        fig.add_annotation(
            text="μ=Mean, M=Median, σ=Std Dev | 🔍 Toolbar for zoom/pan",
            xref="paper", yref="paper",
            x=0.5, y=-0.18, xanchor="center", yanchor="top",
            showarrow=False,
            font=dict(size=8, color="gray")
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
            height=550,  # Increased height
            template='plotly_white',
            hovermode='closest',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,  # Moved legend below
                xanchor="center",
                x=0.5,
                font=dict(size=10)
            ),
            # Enable zooming and panning
            xaxis=dict(fixedrange=False),
            yaxis=dict(fixedrange=False, tickformat='$,.0f'),
            # Add margins for better spacing
            margin=dict(l=60, r=60, t=80, b=120)
        )
        
        # Add annotation with better positioning
        fig.add_annotation(
            text="💡 Bubble size = amount | Click legend to toggle | 🔍 Toolbar for zoom/pan/select",
            xref="paper", yref="paper",
            x=0.5, y=-0.35, xanchor="center", yanchor="top",
            showarrow=False,
            font=dict(size=9, color="gray")
        )
        
        return fig
    
    def create_recurring_expenses_analysis(self, df):
        """Create analysis for recurring/repetitive expenses."""
        # Focus on key recurring categories
        recurring_categories = ['Subscriptions', 'Utilities', 'Gas & Fuel', 'Groceries', 'Insurance', 'Housing']
        
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        expenses_df['YearMonth'] = expenses_df['Date'].dt.to_period('M')
        
        # Filter for recurring categories
        recurring_df = expenses_df[expenses_df['Category'].isin(recurring_categories)]
        
        if len(recurring_df) == 0:
            return None
        
        # Calculate monthly spending by category
        monthly_recurring = recurring_df.groupby(['YearMonth', 'Category'])['Amount'].sum().reset_index()
        monthly_recurring['YearMonth_str'] = monthly_recurring['YearMonth'].astype(str)
        
        # Create stacked bar chart
        fig = go.Figure()
        
        colors = {
            'Subscriptions': '#FF6B6B',
            'Utilities': '#4ECDC4', 
            'Gas & Fuel': '#45B7D1',
            'Groceries': '#96CEB4',
            'Insurance': '#FFEAA7',
            'Housing': '#DDA0DD'
        }
        
        for category in recurring_categories:
            category_data = monthly_recurring[monthly_recurring['Category'] == category]
            if len(category_data) > 0:
                fig.add_trace(go.Bar(
                    x=category_data['YearMonth_str'],
                    y=category_data['Amount'],
                    name=f'{category}',
                    marker_color=colors.get(category, '#95A5A6'),
                    hovertemplate=(
                        f"<b>{category}</b><br>" +
                        "Month: %{x}<br>" +
                        "Amount: $%{y:,.2f}<br>" +
                        "<extra></extra>"
                    )
                ))
        
        # Calculate YTD totals for annotation
        current_year = df['Date'].dt.year.max()
        ytd_data = recurring_df[recurring_df['Date'].dt.year == current_year]
        ytd_totals = ytd_data.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        
        fig.update_layout(
            title={
                'text': '📅 Monthly Recurring Expenses Tracker',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            xaxis_title="Month",
            yaxis_title="Amount ($)",
            height=500,
            template='plotly_white',
            barmode='stack',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=60, r=60, t=80, b=140)
        )
        
        # Add YTD summary annotation
        ytd_text = f"🗓️ {current_year} YTD Totals: " + " | ".join([f"{cat}: ${amt:,.0f}" for cat, amt in ytd_totals.head(3).items()])
        fig.add_annotation(
            text=ytd_text,
            xref="paper", yref="paper",
            x=0.5, y=-0.35, xanchor="center", yanchor="top",
            showarrow=False,
            font=dict(size=9, color="gray"),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="lightgray",
            borderwidth=1
        )
        
        return fig
    
    def create_ytd_spending_breakdown(self, df):
        """Create YTD spending breakdown by category."""
        current_year = df['Date'].dt.year.max()
        ytd_data = df[(df['Date'].dt.year == current_year) & (df['Amount'] < 0)].copy()
        ytd_data['Amount'] = ytd_data['Amount'].abs()
        
        if len(ytd_data) == 0:
            return None
        
        # Calculate YTD spending by category
        ytd_spending = ytd_data.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        total_ytd = ytd_spending.sum()
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=ytd_spending.index,
            x=ytd_spending.values,
            orientation='h',
            marker=dict(
                color=ytd_spending.values,
                colorscale='RdYlBu_r',
                colorbar=dict(title="Amount ($)"),
                line=dict(color='rgba(50,50,50,0.8)', width=1)
            ),
            hovertemplate=(
                "<b>%{y}</b><br>" +
                "YTD Spending: $%{x:,.2f}<br>" +
                "% of Total: %{customdata:.1f}%<br>" +
                "<extra></extra>"
            ),
            customdata=[(amt/total_ytd*100) for amt in ytd_spending.values]
        ))
        
        fig.update_layout(
            title={
                'text': f'📊 {current_year} Year-to-Date Spending Breakdown',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            xaxis_title="Amount ($)",
            yaxis_title="Category",
            height=500,
            template='plotly_white',
            showlegend=False,
            xaxis_tickformat='$,.0f',
            margin=dict(l=120, r=60, t=80, b=80)
        )
        
        # Add total spending annotation
        fig.add_annotation(
            text=f"💰 Total YTD Spending: ${total_ytd:,.2f}",
            xref="paper", yref="paper",
            x=1, y=-0.15, xanchor="right", yanchor="top",
            showarrow=False,
            font=dict(size=10, color="darkblue", weight="bold"),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="darkblue",
            borderwidth=1
        )
        
        return fig
    
    def create_expense_optimization_insights(self, df):
        """Generate detailed expense optimization recommendations."""
        current_year = df['Date'].dt.year.max()
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        
        insights = []
        insights.append("🎯 **Expense Optimization Analysis**")
        insights.append("")
        
        # 1. Identify highest spending categories
        category_spending = expenses_df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        top_3_categories = category_spending.head(3)
        
        insights.append("📈 **Top 3 Expense Categories to Target:**")
        for i, (category, amount) in enumerate(top_3_categories.items(), 1):
            monthly_avg = amount / len(expenses_df['Date'].dt.to_period('M').unique())
            insights.append(f"{i}. **{category}**: ${amount:,.2f} YTD (${monthly_avg:,.0f}/month avg)")
        insights.append("")
        
        # 2. Subscription analysis
        subscription_expenses = expenses_df[expenses_df['Category'] == 'Subscriptions']
        if len(subscription_expenses) > 0:
            monthly_subs = subscription_expenses.groupby(subscription_expenses['Date'].dt.to_period('M'))['Amount'].sum()
            avg_monthly_subs = monthly_subs.mean()
            insights.append("🔄 **Subscription Analysis:**")
            insights.append(f"• Average monthly subscriptions: **${avg_monthly_subs:.2f}**")
            insights.append(f"• Annual projected cost: **${avg_monthly_subs * 12:,.2f}**")
            
            # Find individual subscriptions
            sub_merchants = subscription_expenses.groupby('Description')['Amount'].agg(['sum', 'count']).sort_values('sum', ascending=False)
            if len(sub_merchants) > 0:
                insights.append("• Top subscription expenses:")
                for desc, row in sub_merchants.head(3).iterrows():
                    insights.append(f"  - {desc}: ${row['sum']:,.2f} ({row['count']} transactions)")
            insights.append("")
        
        # 3. Recurring expense patterns
        recurring_cats = ['Utilities', 'Gas & Fuel', 'Groceries', 'Insurance']
        for cat in recurring_cats:
            cat_data = expenses_df[expenses_df['Category'] == cat]
            if len(cat_data) > 0:
                monthly_avg = cat_data.groupby(cat_data['Date'].dt.to_period('M'))['Amount'].sum().mean()
                total_spent = cat_data['Amount'].sum()
                insights.append(f"💡 **{cat}**: ${total_spent:,.2f} YTD (${monthly_avg:,.0f}/month avg)")
        
        insights.append("")
        insights.append("🔧 **Optimization Recommendations:**")
        
        # 4. Generate specific recommendations
        if len(subscription_expenses) > 0 and avg_monthly_subs > 50:
            insights.append(f"• **Review subscriptions**: You're spending ${avg_monthly_subs:.0f}/month. Cancel unused services to save ${avg_monthly_subs * 0.3:.0f}+/month")
        
        grocery_spending = expenses_df[expenses_df['Category'] == 'Groceries']['Amount'].sum()
        if grocery_spending > 0:
            monthly_grocery = grocery_spending / len(expenses_df['Date'].dt.to_period('M').unique())
            if monthly_grocery > 400:
                insights.append(f"• **Grocery optimization**: ${monthly_grocery:.0f}/month is above average. Try meal planning and bulk buying")
        
        dining_spending = expenses_df[expenses_df['Category'] == 'Dining Out']['Amount'].sum()
        if dining_spending > 0:
            monthly_dining = dining_spending / len(expenses_df['Date'].dt.to_period('M').unique())
            if monthly_dining > 200:
                potential_savings = monthly_dining * 0.5
                insights.append(f"• **Dining out**: ${monthly_dining:.0f}/month. Cooking more could save ${potential_savings:.0f}/month")
        
        gas_spending = expenses_df[expenses_df['Category'] == 'Gas & Fuel']['Amount'].sum()
        if gas_spending > 0:
            monthly_gas = gas_spending / len(expenses_df['Date'].dt.to_period('M').unique())
            insights.append(f"• **Fuel efficiency**: Track gas spending patterns to optimize routes and find cheaper stations")
        
        # 5. Overall savings potential
        total_monthly = expenses_df.groupby(expenses_df['Date'].dt.to_period('M'))['Amount'].sum().mean()
        potential_monthly_savings = (avg_monthly_subs * 0.2 if len(subscription_expenses) > 0 else 0) + \
                                  (monthly_dining * 0.3 if dining_spending > 0 else 0)
        
        if potential_monthly_savings > 50:
            annual_savings = potential_monthly_savings * 12
            insights.append("")
            insights.append(f"💰 **Potential Savings**: ${potential_monthly_savings:.0f}/month = **${annual_savings:,.0f}/year**")
        
        return insights
    
    def create_recurring_expenses_calendar(self, df):
        """Create a calendar view of recurring expenses."""
        recurring_categories = ['Subscriptions', 'Utilities', 'Gas & Fuel', 'Insurance']
        
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        
        # Filter for recurring categories
        recurring_df = expenses_df[expenses_df['Category'].isin(recurring_categories)]
        
        if len(recurring_df) == 0:
            return None
        
        # Group by date and category
        daily_expenses = recurring_df.groupby(['Date', 'Category'])['Amount'].sum().reset_index()
        
        # Create scatter plot with dates
        fig = go.Figure()
        
        colors = {
            'Subscriptions': '#FF6B6B',
            'Utilities': '#4ECDC4', 
            'Gas & Fuel': '#45B7D1',
            'Insurance': '#FFEAA7'
        }
        
        for category in recurring_categories:
            cat_data = daily_expenses[daily_expenses['Category'] == category]
            if len(cat_data) > 0:
                fig.add_trace(go.Scatter(
                    x=cat_data['Date'],
                    y=cat_data['Amount'],
                    mode='markers',
                    name=category,
                    marker=dict(
                        size=cat_data['Amount'] / cat_data['Amount'].max() * 20 + 8,
                        color=colors.get(category, '#95A5A6'),
                        opacity=0.7,
                        line=dict(width=1, color='white')
                    ),
                    hovertemplate=(
                        f"<b>{category}</b><br>" +
                        "Date: %{x}<br>" +
                        "Amount: $%{y:,.2f}<br>" +
                        "<extra></extra>"
                    )
                ))
        
        fig.update_layout(
            title={
                'text': '📅 Recurring Expenses Calendar View',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            xaxis_title="Date",
            yaxis_title="Amount ($)",
            height=400,
            template='plotly_white',
            hovermode='closest',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=60, r=60, t=80, b=100)
        )
        
        # Add annotation
        fig.add_annotation(
            text="💡 Bubble size = expense amount | Identify patterns in recurring payments",
            xref="paper", yref="paper",
            x=0.5, y=-0.35, xanchor="center", yanchor="top",
            showarrow=False,
            font=dict(size=9, color="gray")
        )
        
        return fig
    
    def create_recurring_expenses_table(self, df):
        """Create detailed table view of recurring expenses with dates and amounts."""
        recurring_categories = ['Subscriptions', 'Utilities', 'Gas & Fuel', 'Groceries', 'Insurance', 'Housing']
        
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        
        # Filter for recurring categories
        recurring_df = expenses_df[expenses_df['Category'].isin(recurring_categories)]
        
        if len(recurring_df) == 0:
            return None
        
        # Group by merchant/description to identify recurring patterns
        merchant_analysis = recurring_df.groupby(['Description', 'Category']).agg({
            'Amount': ['mean', 'count', 'sum', 'std'],
            'Date': ['min', 'max']
        }).round(2)
        
        # Flatten column names
        merchant_analysis.columns = ['Avg_Amount', 'Frequency', 'Total_Spent', 'Amount_Variance', 'First_Payment', 'Last_Payment']
        
        # Calculate monthly frequency and next expected payment
        merchant_analysis['Days_Between_Payments'] = (
            (merchant_analysis['Last_Payment'] - merchant_analysis['First_Payment']).dt.days / 
            (merchant_analysis['Frequency'] - 1)
        ).fillna(0).round(0)
        
        # Estimate next payment date
        merchant_analysis['Next_Expected_Payment'] = (
            merchant_analysis['Last_Payment'] + 
            pd.to_timedelta(merchant_analysis['Days_Between_Payments'], unit='days')
        )
        
        # Add payment pattern classification
        def classify_payment_pattern(row):
            if row['Frequency'] >= 3:
                if 25 <= row['Days_Between_Payments'] <= 35:
                    return 'Monthly'
                elif 85 <= row['Days_Between_Payments'] <= 95:
                    return 'Quarterly'
                elif 360 <= row['Days_Between_Payments'] <= 370:
                    return 'Annual'
                elif row['Days_Between_Payments'] < 10:
                    return 'Weekly/Frequent'
                else:
                    return 'Irregular'
            else:
                return 'One-time/New'
        
        merchant_analysis['Payment_Pattern'] = merchant_analysis.apply(classify_payment_pattern, axis=1)
        
        # Sort by category and total spent
        merchant_analysis = merchant_analysis.reset_index()
        merchant_analysis = merchant_analysis.sort_values(['Category', 'Total_Spent'], ascending=[True, False])
        
        return merchant_analysis
    
    def create_detailed_payment_schedule(self, df):
        """Create a detailed payment schedule table showing all recurring payment dates."""
        recurring_categories = ['Subscriptions', 'Utilities', 'Gas & Fuel', 'Insurance']
        
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        
        # Filter for recurring categories and focus on likely recurring payments
        recurring_df = expenses_df[expenses_df['Category'].isin(recurring_categories)]
        
        if len(recurring_df) == 0:
            return None
        
        # Group to find merchants with multiple payments
        merchant_counts = recurring_df.groupby('Description').size()
        recurring_merchants = merchant_counts[merchant_counts >= 2].index
        
        # Filter for only recurring merchants
        schedule_df = recurring_df[recurring_df['Description'].isin(recurring_merchants)].copy()
        
        if len(schedule_df) == 0:
            return None
        
        # Add useful columns for schedule analysis
        schedule_df['Day_of_Month'] = schedule_df['Date'].dt.day
        schedule_df['Month_Year'] = schedule_df['Date'].dt.strftime('%Y-%m')
        schedule_df['Days_Since_Last'] = schedule_df.groupby('Description')['Date'].diff().dt.days
        
        # Sort by merchant and date
        schedule_df = schedule_df.sort_values(['Description', 'Date'])
        
        # Select relevant columns for display
        display_columns = ['Date', 'Description', 'Category', 'Amount', 'Day_of_Month', 'Days_Since_Last']
        schedule_display = schedule_df[display_columns].copy()
        
        # Format the date for better display
        schedule_display['Date'] = schedule_display['Date'].dt.strftime('%Y-%m-%d')
        schedule_display['Amount'] = schedule_display['Amount'].apply(lambda x: f"${x:,.2f}")
        
        return schedule_display
    
    def setup_sms_notifications(self):
        """Setup SMS notification preferences in sidebar."""
        st.sidebar.markdown("---")
        st.sidebar.header("📱 SMS Notifications")
        
        # SMS notification toggle
        enable_sms = st.sidebar.checkbox(
            "🔔 Enable SMS Alerts", 
            value=False,
            help="Get SMS notifications when recurring payments are due"
        )
        
        sms_config = {}
        
        if enable_sms:
            st.sidebar.markdown("**📞 Contact Information:**")
            mobile_number = st.sidebar.text_input(
                "Mobile Number",
                placeholder="+1234567890",
                help="Enter your mobile number with country code (e.g., +1234567890)"
            )
            
            st.sidebar.markdown("**🔧 Twilio Configuration:**")
            st.sidebar.info("💡 Get free Twilio credentials at twilio.com")
            
            account_sid = st.sidebar.text_input(
                "Twilio Account SID",
                type="password",
                help="Your Twilio Account SID from the console"
            )
            
            auth_token = st.sidebar.text_input(
                "Twilio Auth Token",
                type="password", 
                help="Your Twilio Auth Token from the console"
            )
            
            twilio_number = st.sidebar.text_input(
                "Twilio Phone Number",
                placeholder="+1234567890",
                help="Your Twilio phone number (from/sender number)"
            )
            
            st.sidebar.markdown("**⏰ Notification Preferences:**")
            days_ahead = st.sidebar.selectbox(
                "Notify me _ days before due date:",
                options=[1, 2, 3, 5, 7],
                index=2,
                help="How many days in advance to send notifications"
            )
            
            notification_time = st.sidebar.time_input(
                "Notification Time",
                value=datetime.now().replace(hour=9, minute=0, second=0, microsecond=0).time(),
                help="What time of day to send notifications"
            )
            
            # Categories to monitor
            st.sidebar.markdown("**📋 Monitor Categories:**")
            monitor_subscriptions = st.sidebar.checkbox("📺 Subscriptions", value=True)
            monitor_utilities = st.sidebar.checkbox("⚡ Utilities", value=True)
            monitor_insurance = st.sidebar.checkbox("🛡️ Insurance", value=True)
            monitor_housing = st.sidebar.checkbox("🏠 Housing", value=False)
            
            if mobile_number and account_sid and auth_token and twilio_number:
                sms_config = {
                    'enabled': True,
                    'mobile_number': mobile_number,
                    'account_sid': account_sid,
                    'auth_token': auth_token,
                    'twilio_number': twilio_number,
                    'days_ahead': days_ahead,
                    'notification_time': notification_time,
                    'categories': {
                        'Subscriptions': monitor_subscriptions,
                        'Utilities': monitor_utilities,
                        'Insurance': monitor_insurance,
                        'Housing': monitor_housing
                    }
                }
                
                st.sidebar.success("✅ SMS notifications configured!")
            elif enable_sms:
                st.sidebar.warning("⚠️ Please fill all fields to enable SMS notifications")
        
        return sms_config
    
    def send_sms_notification(self, sms_config, message):
        """Send SMS notification using Twilio."""
        try:
            # Try to import Twilio
            try:
                from twilio.rest import Client
            except ImportError:
                st.error("❌ Twilio package not installed. Please install with: pip install twilio")
                return False
            
            # Create Twilio client
            client = Client(sms_config['account_sid'], sms_config['auth_token'])
            
            # Send message
            message = client.messages.create(
                body=message,
                from_=sms_config['twilio_number'],
                to=sms_config['mobile_number']
            )
            
            return True
            
        except Exception as e:
            st.error(f"❌ Failed to send SMS: {str(e)}")
            return False
    
    def calculate_upcoming_payments(self, df, sms_config):
        """Calculate upcoming payments and send notifications if needed."""
        if not sms_config or not sms_config.get('enabled', False):
            return []
        
        # Get recurring expenses table
        recurring_table = self.create_recurring_expenses_table(df)
        if recurring_table is None or len(recurring_table) == 0:
            return []
        
        upcoming_payments = []
        today = datetime.now().date()
        notification_days = sms_config['days_ahead']
        
        # Filter for monitored categories
        monitored_categories = [cat for cat, enabled in sms_config['categories'].items() if enabled]
        filtered_table = recurring_table[recurring_table['Category'].isin(monitored_categories)]
        
        for _, row in filtered_table.iterrows():
            # Only check monthly and regular payments
            if row['Payment_Pattern'] in ['Monthly', 'Quarterly']:
                next_payment_date = pd.to_datetime(row['Next_Expected_Payment']).date()
                days_until_payment = (next_payment_date - today).days
                
                # Check if notification should be sent
                if days_until_payment == notification_days:
                    upcoming_payments.append({
                        'merchant': row['Description'],
                        'category': row['Category'],
                        'amount': row['Avg_Amount'],
                        'due_date': next_payment_date,
                        'days_until': days_until_payment
                    })
        
        return upcoming_payments
    
    def create_notification_dashboard(self, df, sms_config):
        """Create a dashboard showing upcoming payments and notification status."""
        st.markdown("### 📱 SMS Notification Dashboard")
        
        if not sms_config or not sms_config.get('enabled', False):
            st.info("📋 SMS notifications are not configured. Enable them in the sidebar to track upcoming payments.")
            
            # Show setup guide
            with st.expander("📋 How to Setup SMS Notifications", expanded=False):
                st.markdown("""
                **Step 1: Get Twilio Account (Free)**
                1. Go to [twilio.com](https://www.twilio.com) and sign up for a free account
                2. Verify your phone number
                3. Get $15 free credit (enough for ~500 SMS messages)
                
                **Step 2: Get Your Credentials**
                1. From your Twilio Console Dashboard, copy:
                   - Account SID
                   - Auth Token
                   - Your Twilio phone number
                
                **Step 3: Configure in Sidebar**
                1. Check "🔔 Enable SMS Alerts" in the sidebar
                2. Enter your mobile number with country code (e.g., +1234567890)
                3. Paste your Twilio credentials
                4. Choose notification preferences
                5. Select which payment categories to monitor
                
                **Step 4: Test & Use**
                1. Click "Send Test SMS" to verify setup
                2. The app will automatically calculate due dates based on your payment history
                3. Use "Send Payment Alerts Now" to get immediate notifications
                
                **💡 Tips:**
                - Twilio free trial works with verified numbers only
                - For production use, upgrade your Twilio account
                - SMS costs about $0.0075 per message
                - Keep your Twilio credentials secure
                """)
            return
        
        # Get upcoming payments
        upcoming_payments = self.calculate_upcoming_payments(df, sms_config)
        
        # Display notification settings
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📱 Mobile Number", sms_config['mobile_number'][-4:].rjust(10, '*'))
        
        with col2:
            monitored_cats = [cat for cat, enabled in sms_config['categories'].items() if enabled]
            st.metric("📋 Monitored Categories", len(monitored_cats))
        
        with col3:
            st.metric("⏰ Alert Days Ahead", f"{sms_config['days_ahead']} days")
        
        # Show upcoming payments
        st.markdown("#### 🔔 Upcoming Payment Alerts")
        
        if upcoming_payments:
            # Create a DataFrame for display
            payments_df = pd.DataFrame(upcoming_payments)
            payments_df['Amount'] = payments_df['amount'].apply(lambda x: f"${x:,.2f}")
            payments_df['Due Date'] = payments_df['due_date'].apply(lambda x: x.strftime('%Y-%m-%d'))
            payments_df['Days Until'] = payments_df['days_until']
            
            display_payments = payments_df[['merchant', 'category', 'Amount', 'Due Date', 'Days Until']]
            display_payments.columns = ['Merchant/Service', 'Category', 'Amount', 'Due Date', 'Days Until']
            
            st.dataframe(display_payments, use_container_width=True, hide_index=True)
            
            # Test SMS button
            if st.button("📤 Send Test SMS", help="Send a test notification to verify SMS setup"):
                test_message = f"🏦 Bank Statement Analyzer Test\n\nYour SMS notifications are working! You have {len(upcoming_payments)} upcoming payments to monitor.\n\nNext alert will be sent {sms_config['days_ahead']} days before due dates."
                
                with st.spinner("Sending test SMS..."):
                    if self.send_sms_notification(sms_config, test_message):
                        st.success("✅ Test SMS sent successfully!")
                    else:
                        st.error("❌ Failed to send test SMS. Please check your Twilio configuration.")
            
            # Auto-send notifications button
            if st.button("🚀 Send Payment Alerts Now", help="Send SMS alerts for all upcoming payments"):
                with st.spinner("Sending payment alerts..."):
                    success_count = 0
                    for payment in upcoming_payments:
                        message = f"💰 Payment Reminder\n\n{payment['merchant']} ({payment['category']})\nAmount: ${payment['amount']:,.2f}\nDue: {payment['due_date'].strftime('%m/%d/%Y')}\n\n🏦 Bank Statement Analyzer"
                        
                        if self.send_sms_notification(sms_config, message):
                            success_count += 1
                    
                    if success_count == len(upcoming_payments):
                        st.success(f"✅ Sent {success_count} payment alerts successfully!")
                    else:
                        st.warning(f"⚠️ Sent {success_count} of {len(upcoming_payments)} alerts. Some may have failed.")
        
        else:
            st.info("🎉 No payment alerts needed at this time. All your recurring payments are on track!")
            
            # Still offer test SMS option
            if st.button("📤 Send Test SMS", help="Send a test notification to verify SMS setup"):
                test_message = f"🏦 Bank Statement Analyzer Test\n\nYour SMS notifications are working! No payments due in the next {sms_config['days_ahead']} days.\n\nStay tuned for future alerts!"
                
                with st.spinner("Sending test SMS..."):
                    if self.send_sms_notification(sms_config, test_message):
                        st.success("✅ Test SMS sent successfully!")
                    else:
                        st.error("❌ Failed to send test SMS. Please check your Twilio configuration.")
        
        # Show monitoring status
        st.markdown("#### 📊 Monitoring Status")
        monitor_data = []
        for category, enabled in sms_config['categories'].items():
            status = "✅ Active" if enabled else "⏸️ Disabled"
            monitor_data.append({'Category': category, 'Status': status})
        
        monitor_df = pd.DataFrame(monitor_data)
        st.dataframe(monitor_df, use_container_width=True, hide_index=True)
    
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
                
                # Sheet 6: Recurring Expenses Analysis
                recurring_categories = ['Subscriptions', 'Utilities', 'Gas & Fuel', 'Groceries', 'Insurance', 'Housing']
                expenses_df_recurring = df[df['Amount'] < 0].copy()
                expenses_df_recurring['Amount'] = expenses_df_recurring['Amount'].abs()
                recurring_expenses = expenses_df_recurring[expenses_df_recurring['Category'].isin(recurring_categories)]
                
                if len(recurring_expenses) > 0:
                    # Monthly recurring breakdown
                    recurring_monthly = recurring_expenses.groupby([
                        recurring_expenses['Date'].dt.to_period('M'), 'Category'
                    ])['Amount'].sum().reset_index()
                    recurring_monthly['Month'] = recurring_monthly['Date'].astype(str)
                    recurring_monthly = recurring_monthly[['Month', 'Category', 'Amount']]
                    recurring_monthly.to_excel(writer, sheet_name='Recurring Expenses', index=False)
                
                # Sheet 7: YTD Summary by Category
                current_year = df['Date'].dt.year.max()
                ytd_expenses = df[(df['Date'].dt.year == current_year) & (df['Amount'] < 0)].copy()
                ytd_expenses['Amount'] = ytd_expenses['Amount'].abs()
                
                if len(ytd_expenses) > 0:
                    ytd_summary = ytd_expenses.groupby('Category').agg({
                        'Amount': ['sum', 'mean', 'count'],
                        'Date': ['min', 'max']
                    }).round(2)
                    ytd_summary.columns = ['Total_Spent', 'Avg_Transaction', 'Transaction_Count', 'First_Transaction', 'Last_Transaction']
                    ytd_summary['Monthly_Average'] = (ytd_summary['Total_Spent'] / 
                                                    len(ytd_expenses['Date'].dt.to_period('M').unique())).round(2)
                    ytd_summary = ytd_summary.sort_values('Total_Spent', ascending=False)
                    ytd_summary.to_excel(writer, sheet_name='YTD Summary', index=True)
                
                # Sheet 8: Subscription Details
                subscription_expenses = expenses_df_recurring[expenses_df_recurring['Category'] == 'Subscriptions']
                if len(subscription_expenses) > 0:
                    subscription_details = subscription_expenses.groupby('Description').agg({
                        'Amount': ['sum', 'mean', 'count'],
                        'Date': ['min', 'max']
                    }).round(2)
                    subscription_details.columns = ['Total_Cost', 'Avg_Cost', 'Frequency', 'First_Seen', 'Last_Seen']
                    subscription_details['Annual_Projection'] = (subscription_details['Total_Cost'] * 
                                                               (365 / subscription_details['Frequency'])).round(2)
                    subscription_details = subscription_details.sort_values('Total_Cost', ascending=False)
                    subscription_details.to_excel(writer, sheet_name='Subscription Details', index=True)
                
                # Sheet 9: Detailed Payment Schedule
                schedule_df = expenses_df_recurring.copy()
                merchant_counts = schedule_df.groupby('Description').size()
                recurring_merchants = merchant_counts[merchant_counts >= 2].index
                detailed_schedule = schedule_df[schedule_df['Description'].isin(recurring_merchants)].copy()
                
                if len(detailed_schedule) > 0:
                    detailed_schedule['Day_of_Month'] = detailed_schedule['Date'].dt.day
                    detailed_schedule['Days_Since_Last'] = detailed_schedule.groupby('Description')['Date'].diff().dt.days
                    detailed_schedule = detailed_schedule.sort_values(['Description', 'Date'])
                    
                    export_schedule = detailed_schedule[['Date', 'Description', 'Category', 'Amount', 'Day_of_Month', 'Days_Since_Last']].copy()
                    export_schedule['Date'] = export_schedule['Date'].dt.strftime('%Y-%m-%d')
                    export_schedule.to_excel(writer, sheet_name='Payment Schedule', index=False)
            
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
    4. **Analyze Recurring Expenses**: Track subscriptions, utilities, groceries, fuel
    5. **Setup SMS Alerts**: Get notified when payments are due
    6. **Download Reports**: Generate PDF or Excel summaries
    
    **🔄 Recurring Expenses Analysis:**
    - 📊 **Monthly Tracking**: Subscriptions, utilities, groceries, gas & fuel
    - 📈 **YTD Breakdown**: Year-to-date spending by category
    - 📅 **Calendar View**: Identify patterns in recurring payments
    - 📋 **Payment Tables**: Detailed tables with due dates and amounts
    - 🔍 **Search & Filter**: Find specific payments and merchants
    - 🎯 **Optimization Tips**: Find ways to reduce unwanted expenses
    
    **📱 SMS Payment Alerts:**
    - 🔔 **Due Date Reminders**: Get SMS alerts before payments are due
    - ⚙️ **Custom Settings**: Choose notification timing and categories
    - 📲 **Twilio Integration**: Secure SMS delivery via Twilio API
    - 🔧 **Test & Manage**: Send test messages and manage alerts
    
    **Interactive Features:**
    - 🔍 **Date & Category Filters**: Focus on specific time periods or categories
    - 📊 **Interactive Charts**: Hover for details, zoom, pan, toggle data
    - 📈 **Real-time Updates**: All charts update based on your filters
    
    **Report Options:**
    - 📄 **PDF**: Visual summary with charts
    - 📊 **Excel**: 9 detailed sheets including recurring expense tables
    
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
                
                # Setup SMS notifications
                sms_config = analyzer.setup_sms_notifications()
                
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
                
                # Recurring Expenses Analysis Section
                st.markdown('<div class="chart-header">🔄 Recurring Expenses Analysis</div>', unsafe_allow_html=True)
                
                # Create columns for recurring expense charts
                recurring_col1, recurring_col2 = st.columns(2)
                
                with recurring_col1:
                    st.subheader("📊 Monthly Recurring Expenses")
                    recurring_chart = analyzer.create_recurring_expenses_analysis(filtered_df)
                    if recurring_chart:
                        st.plotly_chart(recurring_chart, use_container_width=True)
                
                with recurring_col2:
                    st.subheader("📈 YTD Spending Breakdown")
                    ytd_chart = analyzer.create_ytd_spending_breakdown(filtered_df)
                    if ytd_chart:
                        st.plotly_chart(ytd_chart, use_container_width=True)
                
                # Recurring expenses calendar (full width)
                st.subheader("📅 Recurring Expenses Calendar")
                calendar_chart = analyzer.create_recurring_expenses_calendar(filtered_df)
                if calendar_chart:
                    st.plotly_chart(calendar_chart, use_container_width=True)
                
                # Recurring Expenses Tables Section
                st.markdown('<div class="chart-header">📋 Recurring Expenses Tables</div>', unsafe_allow_html=True)
                
                # Create tabs for different table views
                table_tab1, table_tab2 = st.tabs(["📊 Payment Summary", "📅 Detailed Schedule"])
                
                with table_tab1:
                    st.subheader("📊 Recurring Payment Summary")
                    st.markdown("**Overview of your recurring expenses with payment patterns and next expected dates**")
                    
                    recurring_table = analyzer.create_recurring_expenses_table(filtered_df)
                    if recurring_table is not None and len(recurring_table) > 0:
                        # Format the table for better display
                        display_table = recurring_table.copy()
                        display_table['Avg_Amount'] = display_table['Avg_Amount'].apply(lambda x: f"${x:,.2f}")
                        display_table['Total_Spent'] = display_table['Total_Spent'].apply(lambda x: f"${x:,.2f}")
                        display_table['Amount_Variance'] = display_table['Amount_Variance'].apply(lambda x: f"${x:,.2f}")
                        display_table['First_Payment'] = display_table['First_Payment'].dt.strftime('%Y-%m-%d')
                        display_table['Last_Payment'] = display_table['Last_Payment'].dt.strftime('%Y-%m-%d')
                        display_table['Next_Expected_Payment'] = display_table['Next_Expected_Payment'].dt.strftime('%Y-%m-%d')
                        display_table['Days_Between_Payments'] = display_table['Days_Between_Payments'].astype(int)
                        
                        # Rename columns for better readability
                        display_table = display_table.rename(columns={
                            'Description': 'Merchant/Service',
                            'Category': 'Category',
                            'Avg_Amount': 'Avg Amount',
                            'Frequency': 'Count',
                            'Total_Spent': 'Total Spent',
                            'Amount_Variance': 'Amount Variance',
                            'First_Payment': 'First Payment',
                            'Last_Payment': 'Last Payment',
                            'Days_Between_Payments': 'Days Between',
                            'Next_Expected_Payment': 'Next Expected',
                            'Payment_Pattern': 'Pattern'
                        })
                        
                        # Display the table
                        st.dataframe(
                            display_table,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Pattern": st.column_config.TextColumn(
                                    help="Payment frequency pattern (Monthly, Quarterly, etc.)"
                                ),
                                "Next Expected": st.column_config.DateColumn(
                                    help="Estimated next payment date based on historical pattern"
                                ),
                                "Days Between": st.column_config.NumberColumn(
                                    help="Average days between payments"
                                )
                            }
                        )
                        
                        # Add summary statistics
                        st.markdown("---")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            monthly_recurring = recurring_table[recurring_table['Payment_Pattern'] == 'Monthly']
                            monthly_total = monthly_recurring['Avg_Amount'].sum() if len(monthly_recurring) > 0 else 0
                            st.metric("💳 Monthly Recurring", f"${monthly_total:,.2f}")
                        
                        with col2:
                            total_recurring_services = len(recurring_table)
                            st.metric("🔄 Recurring Services", total_recurring_services)
                        
                        with col3:
                            subscription_total = recurring_table[recurring_table['Category'] == 'Subscriptions']['Total_Spent'].sum()
                            st.metric("📺 Subscriptions YTD", f"${subscription_total:,.2f}")
                        
                        with col4:
                            utilities_total = recurring_table[recurring_table['Category'] == 'Utilities']['Total_Spent'].sum()
                            st.metric("⚡ Utilities YTD", f"${utilities_total:,.2f}")
                    
                    else:
                        st.info("📝 No recurring expenses found in the selected data range.")
                
                with table_tab2:
                    st.subheader("📅 Detailed Payment Schedule")
                    st.markdown("**Complete history of all recurring payments with exact dates and amounts**")
                    
                    payment_schedule = analyzer.create_detailed_payment_schedule(filtered_df)
                    if payment_schedule is not None and len(payment_schedule) > 0:
                        # Add search functionality
                        search_term = st.text_input(
                            "🔍 Search payments:", 
                            placeholder="Search by merchant name, category, or amount...",
                            help="Filter the payment schedule by typing keywords"
                        )
                        
                        # Filter based on search
                        if search_term:
                            mask = (
                                payment_schedule['Description'].str.contains(search_term, case=False, na=False) |
                                payment_schedule['Category'].str.contains(search_term, case=False, na=False) |
                                payment_schedule['Amount'].str.contains(search_term, case=False, na=False)
                            )
                            filtered_schedule = payment_schedule[mask]
                        else:
                            filtered_schedule = payment_schedule
                        
                        # Rename columns for better display
                        filtered_schedule = filtered_schedule.rename(columns={
                            'Date': 'Payment Date',
                            'Description': 'Merchant/Service',
                            'Category': 'Category',
                            'Amount': 'Amount',
                            'Day_of_Month': 'Day of Month',
                            'Days_Since_Last': 'Days Since Last'
                        })
                        
                        # Display the filtered table
                        st.dataframe(
                            filtered_schedule,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Payment Date": st.column_config.DateColumn(),
                                "Day of Month": st.column_config.NumberColumn(
                                    help="Day of the month when payment was made"
                                ),
                                "Days Since Last": st.column_config.NumberColumn(
                                    help="Number of days since the previous payment to the same merchant"
                                )
                            }
                        )
                        
                        # Show count of filtered results
                        if search_term:
                            st.caption(f"Showing {len(filtered_schedule)} of {len(payment_schedule)} payments")
                        else:
                            st.caption(f"Total payments shown: {len(payment_schedule)}")
                    
                    else:
                        st.info("📝 No detailed payment schedule available for the selected data range.")
                
                # SMS Notification Dashboard
                st.markdown('<div class="chart-header">📱 SMS Payment Alerts</div>', unsafe_allow_html=True)
                analyzer.create_notification_dashboard(filtered_df, sms_config)
                
                # Enhanced Insights section with optimization
                st.markdown('<div class="insight-header">💡 Financial Insights & Expense Optimization</div>', unsafe_allow_html=True)
                
                # Create columns for different types of insights
                insight_col1, insight_col2 = st.columns([1, 1])
                
                with insight_col1:
                    st.markdown("#### 📊 General Financial Insights")
                    general_insights = analyzer.get_insights(filtered_df, total_income, total_expenses, total_savings, savings_rate)
                    for insight in general_insights:
                        if insight:  # Skip empty lines
                            st.markdown(insight)
                
                with insight_col2:
                    st.markdown("#### 🎯 Expense Optimization Recommendations")
                    optimization_insights = analyzer.create_expense_optimization_insights(filtered_df)
                    for insight in optimization_insights:
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
