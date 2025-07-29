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
from datetime import timedelta
import calendar
import re
import base64
import secrets
import bcrypt
import os
from pathlib import Path

# Optional imports for OCR functionality
try:
    from PIL import Image
    import pytesseract
    import numpy as np
    import cv2
    OCR_AVAILABLE = True
except ImportError as e:
    OCR_AVAILABLE = False
    # Create dummy classes to prevent errors
    class Image:
        @staticmethod
        def open(*args, **kwargs):
            return None
    
    class np:
        @staticmethod
        def array(*args, **kwargs):
            return None
    
    def cv2(*args, **kwargs):
        return None

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
        self.data_dir = Path("user_data")
        self.init_data_storage()
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
    
    def init_data_storage(self):
        """Initialize data storage directory and load settings."""
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(exist_ok=True)
        
        # Load persistence settings
        if 'persistence_enabled' not in st.session_state:
            settings = self.load_settings()
            st.session_state.persistence_enabled = settings.get('persistence_enabled', False)
            st.session_state.first_time_user = settings.get('first_time_user', True)
    
    def get_persistence_enabled(self):
        """Check if data persistence is enabled."""
        return st.session_state.get('persistence_enabled', False)
    
    def load_settings(self):
        """Load app settings from file."""
        settings_file = self.data_dir / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"Error loading settings: {e}")
                return {}
        return {}
    
    def save_settings(self, settings):
        """Save app settings to file."""
        settings_file = self.data_dir / "settings.json"
        try:
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2, default=str)
        except Exception as e:
            st.error(f"Error saving settings: {e}")
    
    def get_user_filename(self, filename):
        """Get user-specific filename for data storage."""
        current_user = st.session_state.get('current_user', 'default')
        if current_user != 'default':
            base_name = filename.replace('.json', '')
            return f"{current_user}_{base_name}.json"
        return filename
    
    def save_to_file(self, filename, data):
        """Save data to user-specific JSON file."""
        if not self.get_persistence_enabled():
            return
        
        user_filename = self.get_user_filename(filename)
        filepath = self.data_dir / user_filename
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            st.error(f"Error saving {user_filename}: {e}")
    
    def load_from_file(self, filename, default=None):
        """Load data from user-specific JSON file."""
        if not self.get_persistence_enabled():
            return default if default is not None else []
        
        user_filename = self.get_user_filename(filename)
        filepath = self.data_dir / user_filename
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"Error loading {user_filename}: {e}")
                return default if default is not None else []
        return default if default is not None else []
    
    def setup_persistence_settings(self):
        """Setup persistence settings in sidebar."""
        st.sidebar.markdown("---")
        st.sidebar.header("💾 Data Persistence")
        
        current_user = st.session_state.get('current_user', '')
        is_test_user = current_user == 'test'
        
        if is_test_user:
            # Test user - show that data is temporary
            st.sidebar.warning("🧪 **Test User Mode**")
            st.sidebar.info("💡 Your data is temporary and will be cleared on logout - perfect for testing!")
            st.session_state.persistence_enabled = False
        else:
            # Regular users - show automatic persistence
            st.sidebar.success("💾 **Auto-Persistence Active**")
            st.sidebar.info("✅ Your data automatically saves and persists between sessions!")
            
            # For admin, show manual control option
            if 'admin' in st.session_state.get('user_permissions', []):
                current_enabled = st.session_state.get('persistence_enabled', True)
                persistence_enabled = st.sidebar.checkbox(
                    "🔧 Manual persistence control (Admin)",
                    value=current_enabled,
                    help="Admin can manually control persistence settings"
                )
                
                if persistence_enabled != current_enabled:
                    st.session_state.persistence_enabled = persistence_enabled
                    user_settings = self.load_user_settings(current_user)
                    user_settings['persistence_enabled'] = persistence_enabled
                    self.save_user_settings(current_user, user_settings)
                    
                    if persistence_enabled:
                        self.load_all_data_from_files()
                        st.sidebar.success("✅ Persistence re-enabled!")
                    else:
                        st.sidebar.warning("⚠️ Persistence disabled for this session!")
                    st.rerun()
            else:
                st.session_state.persistence_enabled = True
        
        # Show data management for persistent users
        if st.session_state.get('persistence_enabled', False):
            data_count = (
                len(st.session_state.get('manual_expenses', [])) +
                len(st.session_state.get('manual_subscriptions', [])) +
                len(st.session_state.get('grocery_items', []))
            )
            
            st.sidebar.info(f"📊 **Data Status:** {data_count} items stored")
            
            # Data management options
            with st.sidebar.expander("🗂️ Data Management"):
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Reload"):
                        self.load_all_data_from_files()
                        st.success("Data reloaded!")
                        st.rerun()
                
                with col2:
                    if st.button("💾 Save"):
                        self.save_all_data_to_files()
                        st.success("Data saved!")
                
                if not is_test_user:
                    if st.button("🗑️ Clear My Data", type="secondary"):
                        if st.button("⚠️ Confirm Clear Data"):
                            self.clear_all_saved_data()
                            st.success("Your data cleared!")
                            st.rerun()
        else:
            st.sidebar.info("📝 **Session Storage Only**\nData will be lost when you restart the app.")
    
    def load_all_data_from_files(self):
        """Load all data from persistent files into session state."""
        if not self.get_persistence_enabled():
            return
        
        # Load manual expenses
        expenses = self.load_from_file("manual_expenses.json", [])
        if expenses:
            st.session_state.manual_expenses = expenses
        
        # Load subscriptions
        subscriptions = self.load_from_file("manual_subscriptions.json", [])
        if subscriptions:
            st.session_state.manual_subscriptions = subscriptions
        
        # Load grocery items
        grocery_items = self.load_from_file("grocery_items.json", [])
        if grocery_items:
            st.session_state.grocery_items = grocery_items
    
    def save_all_data_to_files(self):
        """Save all current session data to persistent files."""
        if not self.get_persistence_enabled():
            return
        
        # Save manual expenses
        manual_expenses = st.session_state.get('manual_expenses', [])
        if manual_expenses:
            self.save_to_file("manual_expenses.json", manual_expenses)
        
        # Save subscriptions
        subscriptions = st.session_state.get('manual_subscriptions', [])
        if subscriptions:
            self.save_to_file("manual_subscriptions.json", subscriptions)
        
        # Save grocery items
        grocery_items = st.session_state.get('grocery_items', [])
        if grocery_items:
            self.save_to_file("grocery_items.json", grocery_items)
    
    def clear_all_saved_data(self):
        """Clear all saved data files and session state for current user."""
        # Clear session state
        for key in ['manual_expenses', 'manual_subscriptions', 'grocery_items']:
            if key in st.session_state:
                st.session_state[key] = []
        
        # Clear user-specific files
        current_user = st.session_state.get('current_user', 'default')
        for filename in ["manual_expenses.json", "manual_subscriptions.json", "grocery_items.json"]:
            user_filename = self.get_user_filename(filename)
            filepath = self.data_dir / user_filename
            if filepath.exists():
                try:
                    filepath.unlink()
                except Exception as e:
                    st.error(f"Error deleting {user_filename}: {e}")
    
    def process_dataframe(self, df):
        """Process the uploaded DataFrame and combine with manual entries."""
        try:
            processed_csv = None
            
            # Process CSV data if provided
            if df is not None and len(df) > 0:
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
                
                processed_csv = df
            
            # Combine with all manual entries
            combined_df = self.combine_all_transactions(processed_csv)
            
            if len(combined_df) > 0:
                return combined_df
            else:
                return processed_csv
            
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
    
    def load_manual_subscriptions(self):
        """Load manually entered subscriptions from session state or file."""
        if 'manual_subscriptions' not in st.session_state:
            # Try to load from file first
            subscriptions = self.load_from_file("manual_subscriptions.json", [])
            st.session_state.manual_subscriptions = subscriptions
        return st.session_state.manual_subscriptions
    
    def save_manual_subscriptions(self, subscriptions):
        """Save manually entered subscriptions to session state and file."""
        st.session_state.manual_subscriptions = subscriptions
        # Auto-save to file if persistence is enabled
        self.save_to_file("manual_subscriptions.json", subscriptions)
    
    def calculate_next_due_date(self, last_due_date, due_day_of_month):
        """Calculate the next due date based on the monthly cycle."""
        today = datetime.now().date()
        
        # Start from the last due date or today
        if last_due_date and last_due_date >= today:
            # If last due date is in the future, use it
            return last_due_date
        
        # Calculate next occurrence of the due day
        current_month = today.month
        current_year = today.year
        
        # Try current month first
        try:
            next_due = datetime(current_year, current_month, due_day_of_month).date()
            if next_due > today:
                return next_due
        except ValueError:
            # Day doesn't exist in current month (e.g., Feb 31)
            pass
        
        # Try next month
        next_month = current_month + 1 if current_month < 12 else 1
        next_year = current_year if current_month < 12 else current_year + 1
        
        # Find the last day of next month to handle edge cases
        last_day_of_month = calendar.monthrange(next_year, next_month)[1]
        actual_due_day = min(due_day_of_month, last_day_of_month)
        
        return datetime(next_year, next_month, actual_due_day).date()
    
    def manage_manual_subscriptions(self):
        """Interface to manage manual subscription entries."""
        st.markdown("### ✏️ Manage Your Subscriptions")
        st.markdown("**Add and manage your recurring subscriptions manually with specific due dates**")
        
        # Load existing subscriptions
        subscriptions = self.load_manual_subscriptions()
        
        # Add new subscription form
        with st.expander("➕ Add New Subscription", expanded=len(subscriptions) == 0):
            with st.form("add_subscription"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    service_name = st.text_input(
                        "Service Name*",
                        placeholder="Netflix, Spotify, Electric Bill...",
                        help="Name of the subscription or service"
                    )
                
                with col2:
                    amount = st.number_input(
                        "Monthly Amount*",
                        min_value=0.01,
                        value=10.00,
                        step=0.01,
                        help="Monthly payment amount"
                    )
                
                with col3:
                    due_day = st.number_input(
                        "Due Day of Month*",
                        min_value=1,
                        max_value=31,
                        value=15,
                        help="Day of the month when payment is due"
                    )
                
                category = st.selectbox(
                    "Category",
                    options=["Subscriptions", "Utilities", "Insurance", "Housing", "Other"],
                    help="Type of subscription for better organization"
                )
                
                notes = st.text_area(
                    "Notes (Optional)",
                    placeholder="Additional notes about this subscription...",
                    help="Optional notes for your reference"
                )
                
                submitted = st.form_submit_button("➕ Add Subscription", type="primary")
                
                if submitted:
                    if service_name and amount > 0:
                        # Calculate next due date
                        next_due = self.calculate_next_due_date(None, due_day)
                        
                        new_subscription = {
                            'id': f"{service_name}_{len(subscriptions)}_{datetime.now().timestamp()}",
                            'service_name': service_name,
                            'amount': amount,
                            'due_day': due_day,
                            'category': category,
                            'notes': notes,
                            'next_due_date': next_due,
                            'created_date': datetime.now().date(),
                            'active': True
                        }
                        
                        subscriptions.append(new_subscription)
                        self.save_manual_subscriptions(subscriptions)
                        st.success(f"✅ Added {service_name} - Next due: {next_due.strftime('%Y-%m-%d')}")
                        st.rerun()
                    else:
                        st.error("❌ Please fill in Service Name and Amount")
        
        # Display existing subscriptions
        if subscriptions:
            st.markdown("### 📋 Your Subscriptions")
            
            # Create editable table
            active_subscriptions = [sub for sub in subscriptions if sub.get('active', True)]
            
            if active_subscriptions:
                # Update next due dates for all subscriptions
                for sub in active_subscriptions:
                    sub['next_due_date'] = self.calculate_next_due_date(sub.get('next_due_date'), sub['due_day'])
                
                # Save updated dates
                self.save_manual_subscriptions(subscriptions)
                
                # Display subscriptions table
                df_display = []
                for i, sub in enumerate(active_subscriptions):
                    days_until = (sub['next_due_date'] - datetime.now().date()).days
                    status = "🚨 Due Soon!" if days_until <= 1 else f"📅 {days_until} days"
                    
                    df_display.append({
                        'Service': sub['service_name'],
                        'Category': sub['category'],
                        'Amount': f"${sub['amount']:,.2f}",
                        'Due Day': sub['due_day'],
                        'Next Due': sub['next_due_date'].strftime('%Y-%m-%d'),
                        'Status': status,
                        'Notes': sub.get('notes', '')[:50] + ('...' if len(sub.get('notes', '')) > 50 else '')
                    })
                
                # Display the table
                df = pd.DataFrame(df_display)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Next Due": st.column_config.DateColumn(),
                        "Amount": st.column_config.TextColumn(),
                        "Status": st.column_config.TextColumn()
                    }
                )
                
                # Management actions
                st.markdown("### ⚙️ Manage Subscriptions")
                
                # Delete subscription
                col1, col2 = st.columns(2)
                
                with col1:
                    if len(active_subscriptions) > 0:
                        service_to_delete = st.selectbox(
                            "Select subscription to remove:",
                            options=[sub['service_name'] for sub in active_subscriptions],
                            key="delete_subscription"
                        )
                        
                        if st.button("🗑️ Remove Selected", type="secondary"):
                            # Mark as inactive instead of deleting
                            for sub in subscriptions:
                                if sub['service_name'] == service_to_delete and sub.get('active', True):
                                    sub['active'] = False
                                    break
                            
                            self.save_manual_subscriptions(subscriptions)
                            st.success(f"✅ Removed {service_to_delete}")
                            st.rerun()
                
                with col2:
                    if st.button("🔄 Update All Due Dates", help="Recalculate next due dates for all subscriptions"):
                        updated_count = 0
                        for sub in active_subscriptions:
                            old_date = sub['next_due_date']
                            sub['next_due_date'] = self.calculate_next_due_date(sub['next_due_date'], sub['due_day'])
                            if sub['next_due_date'] != old_date:
                                updated_count += 1
                        
                        self.save_manual_subscriptions(subscriptions)
                        if updated_count > 0:
                            st.success(f"✅ Updated {updated_count} subscription due dates")
                        else:
                            st.info("📅 All due dates are already current")
                        st.rerun()
                
                # Summary metrics
                st.markdown("---")
                col1, col2, col3, col4 = st.columns(4)
                
                total_monthly = sum(sub['amount'] for sub in active_subscriptions)
                due_this_week = sum(1 for sub in active_subscriptions 
                                  if (sub['next_due_date'] - datetime.now().date()).days <= 7)
                due_tomorrow = sum(1 for sub in active_subscriptions 
                                 if (sub['next_due_date'] - datetime.now().date()).days == 1)
                
                with col1:
                    st.metric("💰 Total Monthly", f"${total_monthly:,.2f}")
                
                with col2:
                    st.metric("📅 Due This Week", due_this_week)
                
                with col3:
                    st.metric("🚨 Due Tomorrow", due_tomorrow)
                
                with col4:
                    st.metric("📊 Active Services", len(active_subscriptions))
            
            else:
                st.info("🎉 No active subscriptions. Add your first subscription above!")
        
        else:
            st.info("📝 No subscriptions added yet. Use the form above to add your first subscription.")
        
        return subscriptions
    
    def load_manual_expenses(self):
        """Load manually entered expenses from session state or file."""
        if 'manual_expenses' not in st.session_state:
            # Try to load from file first
            expenses = self.load_from_file("manual_expenses.json", [])
            st.session_state.manual_expenses = expenses
        return st.session_state.manual_expenses
    
    def save_manual_expenses(self, expenses):
        """Save manually entered expenses to session state and file."""
        st.session_state.manual_expenses = expenses
        # Auto-save to file if persistence is enabled
        self.save_to_file("manual_expenses.json", expenses)
    
    def get_expense_categories(self):
        """Get list of expense categories for dropdown."""
        return [
            'Groceries', 'Dining Out', 'Gas & Fuel', 'Utilities', 'Subscriptions',
            'Insurance', 'Healthcare', 'Transportation', 'Shopping', 'Entertainment',
            'Housing', 'Education', 'Personal Care', 'Gifts & Donations',
            'Travel', 'Automotive', 'Pet Care', 'Home Improvement', 'Other'
        ]
    
    def manage_manual_expenses(self):
        """Interface to manually enter expenses."""
        st.markdown("### ✏️ Manual Expense Entry")
        st.markdown("**Quickly add expenses on-the-go with automatic categorization**")
        
        # Quick expense entry form
        with st.form("quick_expense_entry", clear_on_submit=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                expense_description = st.text_input(
                    "Description*",
                    placeholder="Coffee at Starbucks, Gas fill-up, Grocery shopping...",
                    help="Brief description of the expense"
                )
            
            with col2:
                expense_category = st.selectbox(
                    "Category*",
                    options=self.get_expense_categories(),
                    help="Select the expense category"
                )
            
            with col3:
                expense_amount = st.number_input(
                    "Amount*",
                    min_value=0.01,
                    value=10.00,
                    step=0.01,
                    help="Expense amount in dollars"
                )
            
            col4, col5 = st.columns(2)
            
            with col4:
                expense_date = st.date_input(
                    "Date",
                    value=datetime.now().date(),
                    help="Date of the expense"
                )
            
            with col5:
                expense_type = st.selectbox(
                    "Type",
                    options=['Expense', 'Income'],
                    index=0,
                    help="Type of transaction"
                )
            
            # Optional notes
            expense_notes = st.text_area(
                "Notes (Optional)",
                placeholder="Additional details about this expense...",
                help="Optional notes for your reference"
            )
            
            submitted = st.form_submit_button("➕ Add Expense", type="primary")
            
            if submitted:
                if expense_description and expense_amount > 0:
                    # Create new expense entry
                    amount = expense_amount if expense_type == 'Income' else -expense_amount
                    
                    new_expense = {
                        'id': f"manual_{datetime.now().timestamp()}",
                        'Date': expense_date,
                        'Description': expense_description,
                        'Amount': amount,
                        'Category': expense_category,
                        'Type': expense_type,
                        'Notes': expense_notes,
                        'Source': 'Manual Entry',
                        'Created_At': datetime.now()
                    }
                    
                    # Save to storage
                    existing_expenses = self.load_manual_expenses()
                    existing_expenses.append(new_expense)
                    self.save_manual_expenses(existing_expenses)
                    
                    st.success(f"✅ Added {expense_type.lower()}: ${expense_amount:.2f} for {expense_description}")
                    st.rerun()
                else:
                    st.error("❌ Please fill in Description and Amount")
        
        # Display recent manual expenses
        manual_expenses = self.load_manual_expenses()
        
        if manual_expenses:
            st.markdown("### 📋 Recent Manual Entries")
            
            # Convert to DataFrame for display
            df = pd.DataFrame(manual_expenses)
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Sort by date (most recent first)
            df = df.sort_values('Date', ascending=False)
            
            # Display recent entries (last 10)
            recent_df = df.head(10).copy()
            recent_df['Date'] = recent_df['Date'].dt.strftime('%Y-%m-%d')
            recent_df['Amount'] = recent_df['Amount'].apply(lambda x: f"${abs(x):.2f}")
            
            display_columns = ['Date', 'Description', 'Category', 'Type', 'Amount']
            display_df = recent_df[display_columns]
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Summary metrics
            st.markdown("#### 📊 Manual Entry Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            total_expenses = df[df['Amount'] < 0]['Amount'].sum()
            total_income = df[df['Amount'] > 0]['Amount'].sum()
            total_entries = len(df)
            this_month = df[df['Date'].dt.month == datetime.now().month]
            this_month_total = this_month['Amount'].sum()
            
            with col1:
                st.metric("💸 Total Expenses", f"${abs(total_expenses):,.2f}")
            
            with col2:
                st.metric("💰 Total Income", f"${total_income:,.2f}")
            
            with col3:
                st.metric("📝 Total Entries", f"{total_entries:,}")
            
            with col4:
                st.metric("📅 This Month", f"${this_month_total:,.2f}")
            
            # Management options
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 View All Entries", help="See all manual expense entries"):
                    with st.expander("All Manual Entries", expanded=True):
                        full_df = df.copy()
                        full_df['Date'] = full_df['Date'].dt.strftime('%Y-%m-%d')
                        full_df['Amount'] = full_df['Amount'].apply(lambda x: f"${x:.2f}")
                        
                        st.dataframe(
                            full_df[['Date', 'Description', 'Category', 'Type', 'Amount', 'Notes']],
                            use_container_width=True,
                            hide_index=True
                        )
            
            with col2:
                if st.button("🗑️ Clear All Manual Entries", type="secondary"):
                    if st.button("⚠️ Confirm Delete All Manual Entries"):
                        st.session_state.manual_expenses = []
                        st.success("✅ All manual entries cleared!")
                        st.rerun()
        
        else:
            st.info("📝 No manual expenses added yet. Use the form above to add your first expense.")
    
    def combine_all_transactions(self, csv_df):
        """Combine CSV data with manual expenses and grocery items for comprehensive analysis."""
        all_transactions = []
        
        # Add CSV transactions
        if csv_df is not None and len(csv_df) > 0:
            csv_transactions = csv_df.copy()
            csv_transactions['Source'] = 'CSV Upload'
            all_transactions.append(csv_transactions)
        
        # Add manual expenses
        manual_expenses = self.load_manual_expenses()
        if manual_expenses:
            manual_df = pd.DataFrame(manual_expenses)
            manual_df['Date'] = pd.to_datetime(manual_df['Date'])
            manual_df['Month'] = manual_df['Date'].dt.to_period('M')
            manual_df['Source'] = 'Manual Entry'
            
            # Select only the columns we need to match CSV format
            manual_df = manual_df[['Date', 'Description', 'Amount', 'Category', 'Type', 'Month', 'Source']]
            all_transactions.append(manual_df)
        
        # Add grocery items as transactions
        grocery_items = self.load_grocery_items()
        if grocery_items:
            grocery_df = pd.DataFrame(grocery_items)
            grocery_df['Date'] = pd.to_datetime(grocery_df['date'])
            grocery_df['Description'] = grocery_df['item_name'] + ' @ ' + grocery_df['store']
            grocery_df['Amount'] = -grocery_df['price']  # Groceries are expenses
            grocery_df['Category'] = 'Groceries - ' + grocery_df['category']  # Subcategorize
            grocery_df['Type'] = 'Expense'
            grocery_df['Month'] = grocery_df['Date'].dt.to_period('M')
            grocery_df['Source'] = 'Grocery Receipt'
            
            # Select only the columns we need
            grocery_df = grocery_df[['Date', 'Description', 'Amount', 'Category', 'Type', 'Month', 'Source']]
            all_transactions.append(grocery_df)
        
        # Combine all dataframes
        if all_transactions:
            combined_df = pd.concat(all_transactions, ignore_index=True)
            combined_df = combined_df.sort_values('Date', ascending=False)
            return combined_df
        else:
            return pd.DataFrame()
    
    def load_grocery_items(self):
        """Load grocery items from session state or file."""
        if 'grocery_items' not in st.session_state:
            # Try to load from file first
            items = self.load_from_file("grocery_items.json", [])
            st.session_state.grocery_items = items
        return st.session_state.grocery_items
    
    def save_grocery_items(self, items):
        """Save grocery items to session state and file."""
        st.session_state.grocery_items = items
        # Auto-save to file if persistence is enabled
        self.save_to_file("grocery_items.json", items)
    
    def categorize_grocery_item(self, item_name):
        """Categorize grocery items into specific categories."""
        item_lower = str(item_name).lower()
        
        # Define grocery categories with keywords
        categories = {
            'Vegetables': [
                'lettuce', 'tomato', 'onion', 'carrot', 'celery', 'pepper', 'broccoli', 
                'spinach', 'cucumber', 'potato', 'sweet potato', 'corn', 'peas', 'beans',
                'cabbage', 'cauliflower', 'zucchini', 'squash', 'eggplant', 'mushroom',
                'avocado', 'garlic', 'ginger', 'kale', 'arugula', 'radish', 'turnip'
            ],
            'Fruits': [
                'apple', 'banana', 'orange', 'grape', 'strawberry', 'blueberry', 'cherry',
                'peach', 'pear', 'pineapple', 'mango', 'watermelon', 'cantaloupe', 'kiwi',
                'lemon', 'lime', 'grapefruit', 'raspberry', 'blackberry', 'plum', 'apricot'
            ],
            'Dairy & Milk': [
                'milk', 'yogurt', 'cheese', 'butter', 'cream', 'sour cream', 'cottage cheese',
                'greek yogurt', 'almond milk', 'soy milk', 'oat milk', 'coconut milk',
                'whipped cream', 'half and half', 'heavy cream', 'mozzarella', 'cheddar'
            ],
            'Snacks': [
                'chips', 'crackers', 'cookies', 'candy', 'chocolate', 'nuts', 'popcorn',
                'pretzels', 'granola bar', 'trail mix', 'gum', 'mints', 'ice cream',
                'frozen yogurt', 'cake', 'pie', 'donut', 'pastry', 'brownie', 'snack'
            ],
            'Meat & Protein': [
                'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'turkey', 'ham',
                'bacon', 'sausage', 'eggs', 'tofu', 'tempeh', 'beans', 'lentils',
                'ground beef', 'steak', 'ribs', 'lamb', 'shrimp', 'crab', 'lobster'
            ],
            'Bread & Grains': [
                'bread', 'bagel', 'muffin', 'cereal', 'oatmeal', 'rice', 'pasta', 'noodles',
                'flour', 'quinoa', 'barley', 'wheat', 'rolls', 'tortilla', 'pita',
                'crackers', 'granola', 'cornmeal', 'couscous'
            ],
            'Beverages': [
                'juice', 'soda', 'water', 'coffee', 'tea', 'beer', 'wine', 'energy drink',
                'sports drink', 'kombucha', 'coconut water', 'sparkling water', 'lemonade'
            ],
            'Household & Other': [
                'detergent', 'soap', 'shampoo', 'toothpaste', 'toilet paper', 'paper towel',
                'cleaning', 'dish soap', 'laundry', 'trash bag', 'aluminum foil', 'plastic wrap'
            ]
        }
        
        # Check each category
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in item_lower:
                    return category
        
        return 'Other'
    
    def preprocess_receipt_image(self, image):
        """Preprocess receipt image for better OCR results."""
        if not OCR_AVAILABLE:
            st.warning("OCR libraries not available. Image preprocessing skipped.")
            return image
            
        try:
            # Convert PIL Image to numpy array
            img_array = np.array(image)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(denoised, (1, 1), 0)
            
            # Apply threshold to get binary image
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Convert back to PIL Image
            processed_image = Image.fromarray(thresh)
            
            return processed_image
            
        except Exception as e:
            st.warning(f"Image preprocessing failed: {e}. Using original image.")
            return image
    
    def extract_text_from_receipt(self, image):
        """Extract text from receipt image using OCR."""
        if not OCR_AVAILABLE:
            st.error("❌ OCR functionality is not available in this deployment.")
            st.info("📱 Please use the manual entry option below to add your grocery items.")
            return ""
            
        try:
            # Preprocess the image
            processed_image = self.preprocess_receipt_image(image)
            
            # Perform OCR with specific configuration for receipts
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,$ \n'
            
            # Extract text
            text = pytesseract.image_to_string(processed_image, config=custom_config)
            
            return text.strip()
            
        except Exception as e:
            st.error(f"❌ OCR processing failed: {e}")
            st.info("📱 You can manually enter your grocery items below instead.")
            return ""
    
    def parse_receipt_text(self, text, receipt_date, store_name):
        """Parse OCR text to extract grocery items and prices."""
        lines = text.split('\n')
        items = []
        total_amount = 0
        
        # Common patterns for price matching
        price_patterns = [
            r'(\d+\.\d{2})',  # Standard price format like 12.34
            r'\$(\d+\.\d{2})',  # Price with dollar sign
            r'(\d+\.\d{2})\s*$',  # Price at end of line
        ]
        
        # Common item patterns (avoid store info, addresses, etc.)
        skip_patterns = [
            r'^\d{1,4}\s+\w+\s+st',  # Address patterns
            r'phone|tel|www|\.com',   # Contact info
            r'thank you|receipt|store|location',  # Store messages
            r'^total|subtotal|tax|change',  # Transaction totals
            r'^\s*$',  # Empty lines
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip common non-item lines
            if any(re.search(pattern, line.lower()) for pattern in skip_patterns):
                continue
            
            # Look for lines with prices
            for pattern in price_patterns:
                price_match = re.search(pattern, line)
                if price_match:
                    price = float(price_match.group(1))
                    
                    # Extract item name (everything before the price)
                    item_text = re.sub(pattern, '', line).strip()
                    
                    # Clean up item name
                    item_text = re.sub(r'^\d+\s*', '', item_text)  # Remove leading numbers
                    item_text = re.sub(r'\s+', ' ', item_text)      # Normalize spaces
                    
                    if len(item_text) > 2 and price > 0:  # Valid item
                        category = self.categorize_grocery_item(item_text)
                        
                        items.append({
                            'id': f"{receipt_date}_{store_name}_{len(items)}_{datetime.now().timestamp()}",
                            'date': receipt_date,
                            'store': store_name,
                            'item_name': item_text,
                            'category': category,
                            'price': price,
                            'created_at': datetime.now()
                        })
                        
                        total_amount += price
                    break
        
        return items, total_amount
    
    def manage_grocery_receipts(self):
        """Interface to manage grocery receipt uploads and item tracking."""
        st.markdown("### 🛒 Grocery Receipt Tracker")
        st.markdown("**Upload receipts and track your grocery spending by category**")
        
        # Create tabs for different functionalities
        tab1, tab2, tab3 = st.tabs(["📱 Upload Receipt", "📊 Item Categories", "📈 YTD Analysis"])
        
        with tab1:
            st.markdown("#### 📱 Upload Grocery Receipt")
            st.markdown("**Take a photo of your receipt or upload an image file**")
            
            # Show OCR availability status
            if not OCR_AVAILABLE:
                st.warning("⚠️ **OCR scanning is not available in this deployment.** You can still upload receipt images for reference, but will need to enter items manually.")
            
            # Receipt upload
            uploaded_file = st.file_uploader(
                "📷 Choose receipt image",
                type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
                help="Upload a clear photo of your grocery receipt. Works best with good lighting and minimal shadows.",
                accept_multiple_files=False
            )
            
            if uploaded_file is not None:
                # Display the uploaded image
                image = Image.open(uploaded_file)
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.image(image, caption="Uploaded Receipt", use_column_width=True)
                
                with col2:
                    # Receipt details form
                    with st.form("receipt_details"):
                        store_name = st.text_input(
                            "Store Name*",
                            placeholder="Walmart, Kroger, Target...",
                            help="Name of the grocery store"
                        )
                        
                        receipt_date = st.date_input(
                            "Receipt Date*",
                            value=datetime.now().date(),
                            help="Date of the grocery purchase"
                        )
                        
                        process_receipt = st.form_submit_button("🔍 Process Receipt", type="primary")
                        
                        if process_receipt and store_name:
                            with st.spinner("🔍 Processing receipt with OCR..."):
                                # Extract text from receipt
                                extracted_text = self.extract_text_from_receipt(image)
                                
                                if extracted_text:
                                    # Parse the extracted text
                                    items, total = self.parse_receipt_text(extracted_text, receipt_date, store_name)
                                    
                                    if items:
                                        # Save items to storage
                                        existing_items = self.load_grocery_items()
                                        existing_items.extend(items)
                                        self.save_grocery_items(existing_items)
                                        
                                        st.success(f"✅ Successfully processed receipt! Found {len(items)} items totaling ${total:.2f}")
                                        
                                        # Show processed items
                                        st.markdown("**Extracted Items:**")
                                        for item in items:
                                            st.write(f"• **{item['item_name']}** - {item['category']} - ${item['price']:.2f}")
                                        
                                        st.rerun()
                                    else:
                                        st.warning("⚠️ No grocery items found in the receipt. You can add items manually below.")
                                else:
                                    st.error("❌ Could not extract text from receipt. Please try manual entry.")
                        
                        elif process_receipt:
                            st.error("❌ Please enter the store name to process the receipt.")
            
            # Manual item entry option
            st.markdown("---")
            st.markdown("#### ✏️ Manual Item Entry")
            st.markdown("**Add grocery items manually if OCR doesn't work perfectly**")
            
            with st.form("manual_grocery_item"):
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    manual_item = st.text_input("Item Name*", placeholder="Organic Bananas, Whole Milk...")
                
                with col2:
                    manual_category = st.selectbox(
                        "Category",
                        options=['Vegetables', 'Fruits', 'Dairy & Milk', 'Snacks', 'Meat & Protein', 
                                'Bread & Grains', 'Beverages', 'Household & Other'],
                        help="Select the most appropriate category"
                    )
                
                with col3:
                    manual_price = st.number_input("Price*", min_value=0.01, value=1.00, step=0.01)
                
                with col4:
                    manual_date = st.date_input("Date", value=datetime.now().date())
                
                manual_store = st.text_input("Store Name*", placeholder="Store where you bought this item")
                
                add_manual_item = st.form_submit_button("➕ Add Item", type="secondary")
                
                if add_manual_item and manual_item and manual_store:
                    new_item = {
                        'id': f"{manual_date}_{manual_store}_{datetime.now().timestamp()}",
                        'date': manual_date,
                        'store': manual_store,
                        'item_name': manual_item,
                        'category': manual_category,
                        'price': manual_price,
                        'created_at': datetime.now()
                    }
                    
                    existing_items = self.load_grocery_items()
                    existing_items.append(new_item)
                    self.save_grocery_items(existing_items)
                    
                    st.success(f"✅ Added {manual_item} to {manual_category} category!")
                    st.rerun()
        
        with tab2:
            st.markdown("#### 📊 Your Grocery Items by Category")
            
            grocery_items = self.load_grocery_items()
            
            if grocery_items:
                # Convert to DataFrame for easier manipulation
                df = pd.DataFrame(grocery_items)
                df['date'] = pd.to_datetime(df['date'])
                df['month_year'] = df['date'].dt.strftime('%Y-%m')
                
                # Filter controls
                col1, col2 = st.columns(2)
                
                with col1:
                    # Category filter
                    categories = df['category'].unique().tolist()
                    selected_categories = st.multiselect(
                        "🏷️ Filter by Categories",
                        options=categories,
                        default=categories,
                        help="Select categories to display"
                    )
                
                with col2:
                    # Date range filter
                    min_date = df['date'].min().date()
                    max_date = df['date'].max().date()
                    
                    date_range = st.date_input(
                        "📅 Date Range",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date
                    )
                
                # Apply filters
                if len(date_range) == 2:
                    start_date, end_date = date_range
                    filtered_df = df[
                        (df['category'].isin(selected_categories)) &
                        (df['date'].dt.date >= start_date) &
                        (df['date'].dt.date <= end_date)
                    ]
                else:
                    filtered_df = df[df['category'].isin(selected_categories)]
                
                if len(filtered_df) > 0:
                    # Display items table
                    display_df = filtered_df[['date', 'store', 'item_name', 'category', 'price']].copy()
                    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
                    display_df['price'] = display_df['price'].apply(lambda x: f"${x:.2f}")
                    
                    # Rename columns
                    display_df.columns = ['Date', 'Store', 'Item', 'Category', 'Price']
                    
                    st.dataframe(
                        display_df.sort_values('Date', ascending=False),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Summary by category
                    st.markdown("#### 📈 Category Summary")
                    category_summary = filtered_df.groupby('category').agg({
                        'price': ['sum', 'count', 'mean'],
                        'item_name': lambda x: list(x.unique())[:3]  # Top 3 unique items
                    }).round(2)
                    
                    category_summary.columns = ['Total_Spent', 'Item_Count', 'Avg_Price', 'Sample_Items']
                    category_summary['Sample_Items'] = category_summary['Sample_Items'].apply(
                        lambda x: ', '.join(x) + ('...' if len(x) >= 3 else '')
                    )
                    
                    # Display summary
                    for category, row in category_summary.iterrows():
                        with st.expander(f"🏷️ {category} - ${row['Total_Spent']:.2f} ({row['Item_Count']} items)"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric("Total Spent", f"${row['Total_Spent']:.2f}")
                                st.metric("Average Price", f"${row['Avg_Price']:.2f}")
                            
                            with col2:
                                st.metric("Items Bought", f"{row['Item_Count']}")
                                st.write(f"**Sample Items:** {row['Sample_Items']}")
                    
                    # Delete functionality
                    st.markdown("---")
                    st.markdown("#### 🗑️ Manage Items")
                    
                    if st.button("🗑️ Clear All Grocery Data", type="secondary"):
                        if st.button("⚠️ Confirm Delete All", type="secondary"):
                            st.session_state.grocery_items = []
                            st.success("✅ All grocery data cleared!")
                            st.rerun()
                
                else:
                    st.info("📝 No items found for the selected filters.")
            
            else:
                st.info("📝 No grocery items added yet. Upload a receipt or add items manually in the first tab.")
        
        with tab3:
            st.markdown("#### 📈 Year-to-Date Grocery Analysis")
            
            grocery_items = self.load_grocery_items()
            
            if grocery_items:
                df = pd.DataFrame(grocery_items)
                df['date'] = pd.to_datetime(df['date'])
                
                # Year selection
                available_years = sorted(df['date'].dt.year.unique(), reverse=True)
                selected_year = st.selectbox(
                    "📅 Select Year",
                    options=available_years,
                    index=0,
                    help="Choose year for YTD analysis"
                )
                
                # Filter for selected year
                ytd_df = df[df['date'].dt.year == selected_year]
                
                if len(ytd_df) > 0:
                    # YTD Summary metrics
                    total_spent = ytd_df['price'].sum()
                    total_items = len(ytd_df)
                    avg_per_trip = ytd_df.groupby(['date', 'store'])['price'].sum().mean()
                    most_expensive = ytd_df.loc[ytd_df['price'].idxmax()]
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(f"🛒 {selected_year} Total", f"${total_spent:.2f}")
                    
                    with col2:
                        st.metric("📦 Total Items", f"{total_items:,}")
                    
                    with col3:
                        st.metric("🛍️ Avg per Trip", f"${avg_per_trip:.2f}")
                    
                    with col4:
                        st.metric("💰 Most Expensive", f"${most_expensive['price']:.2f}")
                    
                    # YTD by Category
                    st.markdown(f"#### 📊 {selected_year} Spending by Category")
                    
                    category_ytd = ytd_df.groupby('category').agg({
                        'price': ['sum', 'count', 'mean']
                    }).round(2)
                    category_ytd.columns = ['Total', 'Count', 'Average']
                    category_ytd['Percentage'] = (category_ytd['Total'] / total_spent * 100).round(1)
                    category_ytd = category_ytd.sort_values('Total', ascending=False)
                    
                    # Display YTD table
                    ytd_display = category_ytd.copy()
                    ytd_display['Total'] = ytd_display['Total'].apply(lambda x: f"${x:.2f}")
                    ytd_display['Average'] = ytd_display['Average'].apply(lambda x: f"${x:.2f}")
                    ytd_display['Percentage'] = ytd_display['Percentage'].apply(lambda x: f"{x:.1f}%")
                    
                    st.dataframe(
                        ytd_display,
                        use_container_width=True,
                        column_config={
                            "Total": "Total Spent",
                            "Count": "Items Count",
                            "Average": "Avg Price",
                            "Percentage": "% of Total"
                        }
                    )
                    
                    # Monthly trend
                    st.markdown(f"#### 📈 {selected_year} Monthly Grocery Spending")
                    
                    monthly_spending = ytd_df.groupby(ytd_df['date'].dt.month)['price'].sum()
                    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    
                    # Create monthly chart
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=[month_names[m-1] for m in monthly_spending.index],
                        y=monthly_spending.values,
                        marker_color='lightgreen',
                        hovertemplate="<b>%{x}</b><br>Spent: $%{y:.2f}<extra></extra>"
                    ))
                    
                    fig.update_layout(
                        title=f"{selected_year} Monthly Grocery Spending",
                        xaxis_title="Month",
                        yaxis_title="Amount Spent ($)",
                        height=400,
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Top items
                    st.markdown(f"#### 🏆 {selected_year} Top Grocery Items")
                    
                    top_items = ytd_df.nlargest(10, 'price')[['item_name', 'category', 'price', 'date', 'store']]
                    top_items['date'] = top_items['date'].dt.strftime('%Y-%m-%d')
                    top_items['price'] = top_items['price'].apply(lambda x: f"${x:.2f}")
                    top_items.columns = ['Item', 'Category', 'Price', 'Date', 'Store']
                    
                    st.dataframe(
                        top_items,
                        use_container_width=True,
                        hide_index=True
                    )
                
                else:
                    st.info(f"📝 No grocery data found for {selected_year}.")
            
            else:
                st.info("📝 No grocery items added yet. Upload receipts or add items manually to see YTD analysis.")
    
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
                index=0,  # Default to 1 day ahead
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
    
    def calculate_upcoming_payments(self, sms_config):
        """Calculate upcoming payments from manual subscriptions."""
        if not sms_config or not sms_config.get('enabled', False):
            return []
        
        # Get manual subscriptions
        subscriptions = self.load_manual_subscriptions()
        active_subscriptions = [sub for sub in subscriptions if sub.get('active', True)]
        
        if not active_subscriptions:
            return []
        
        upcoming_payments = []
        today = datetime.now().date()
        notification_days = sms_config['days_ahead']
        
        # Filter for monitored categories
        monitored_categories = [cat for cat, enabled in sms_config['categories'].items() if enabled]
        
        for sub in active_subscriptions:
            # Check if this category is being monitored
            if sub['category'] in monitored_categories:
                # Update the due date to ensure it's current
                next_due_date = self.calculate_next_due_date(sub.get('next_due_date'), sub['due_day'])
                days_until_payment = (next_due_date - today).days
                
                # Check if notification should be sent
                if days_until_payment == notification_days:
                    upcoming_payments.append({
                        'merchant': sub['service_name'],
                        'category': sub['category'],
                        'amount': sub['amount'],
                        'due_date': next_due_date,
                        'days_until': days_until_payment
                    })
        
        return upcoming_payments
    
    def initialize_users(self):
        """Initialize default users and load from persistent storage."""
        # Load users from file if they exist
        users_data = self.load_users_from_file()
        
        if not users_data:
            # Create default users if file doesn't exist
            admin_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
            test_password = bcrypt.hashpw("test123".encode('utf-8'), bcrypt.gensalt())
            
            users_data = {
                'admin': {
                    'password_hash': admin_password.decode('utf-8'),
                    'role': 'admin',
                    'created_at': datetime.now().isoformat(),
                    'permissions': ['read', 'write', 'admin']
                },
                'test': {
                    'password_hash': test_password.decode('utf-8'),
                    'role': 'user',
                    'created_at': datetime.now().isoformat(),
                    'permissions': ['read', 'write'],
                    'is_test_user': True
                }
            }
            self.save_users_to_file(users_data)
        
        # Convert password hashes back to bytes for session state
        for username, user_info in users_data.items():
            if isinstance(user_info['password_hash'], str):
                user_info['password_hash'] = user_info['password_hash'].encode('utf-8')
            if isinstance(user_info['created_at'], str):
                user_info['created_at'] = datetime.fromisoformat(user_info['created_at'])
        
        st.session_state.users = users_data
    
    def load_users_from_file(self):
        """Load users from persistent file storage."""
        users_file = self.data_dir / "users.json"
        if users_file.exists():
            try:
                with open(users_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"Error loading users: {e}")
                return {}
        return {}
    
    def save_users_to_file(self, users_data=None):
        """Save users to persistent file storage."""
        if users_data is None:
            users_data = st.session_state.get('users', {})
        
        # Convert data for JSON serialization
        serializable_users = {}
        for username, user_info in users_data.items():
            serializable_users[username] = {
                'password_hash': user_info['password_hash'].decode('utf-8') if isinstance(user_info['password_hash'], bytes) else user_info['password_hash'],
                'role': user_info['role'],
                'created_at': user_info['created_at'].isoformat() if isinstance(user_info['created_at'], datetime) else user_info['created_at'],
                'permissions': user_info['permissions'],
                'is_test_user': user_info.get('is_test_user', False)
            }
        
        users_file = self.data_dir / "users.json"
        try:
            with open(users_file, 'w') as f:
                json.dump(serializable_users, f, indent=2)
        except Exception as e:
            st.error(f"Error saving users: {e}")
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials."""
        if 'users' not in st.session_state:
            self.initialize_users()
        
        users = st.session_state.users
        if username in users:
            stored_hash = users[username]['password_hash']
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return True
        return False
    
    def create_user(self, username, password, role='user', permissions=None):
        """Create a new user and save to persistent storage."""
        if 'users' not in st.session_state:
            self.initialize_users()
        
        if permissions is None:
            permissions = ['read', 'write']
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        st.session_state.users[username] = {
            'password_hash': password_hash,
            'role': role,
            'created_at': datetime.now(),
            'permissions': permissions,
            'is_test_user': False
        }
        
        # Save to persistent storage
        self.save_users_to_file()
        
        # Setup automatic persistence for new user
        user_settings = {
            'persistence_enabled': True,
            'first_time_user': False,
            'created_by': st.session_state.get('current_user', 'system')
        }
        self.save_user_settings(username, user_settings)
        
        return True
    
    def login_interface(self):
        """Display login interface."""
        st.markdown("### 🔐 Login Required")
        st.markdown("**Please enter your credentials to access the Finance Analyzer**")
        
        # Check if already logged in
        if 'authenticated' in st.session_state and st.session_state.authenticated:
            return True
        
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                login_button = st.form_submit_button("🔓 Login", type="primary")
            
            if login_button:
                if self.authenticate_user(username, password):
                    st.session_state.authenticated = True
                    st.session_state.current_user = username
                    st.session_state.user_role = st.session_state.users[username]['role']
                    st.session_state.user_permissions = st.session_state.users[username]['permissions']
                    
                    # Setup user-specific persistence and load their data
                    self.setup_user_on_login(username)
                    
                    st.success(f"✅ Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        # Default credentials info
        with st.expander("📋 Available Login Credentials", expanded=False):
            st.markdown("""
            **👑 Admin Account (Persistent):**
            - Username: `admin`
            - Password: `admin123`
            - Role: Full access, user management
            
            **🧪 Test Account (Clears on logout):**
            - Username: `test`
            - Password: `test123`
            - Role: Regular user, data clears on logout
            - Perfect for testing features!
            
            **⚠️ Security Notes:**
            - Admin credentials persist permanently
            - Test user data is automatically cleared on logout
            - Create additional users for team members
            - Change default passwords for production use
            """)
        
        return False
    
    def setup_user_on_login(self, username):
        """Setup user-specific persistence and load their data on login."""
        # Enable persistence automatically for all users except test user
        is_test_user = st.session_state.users[username].get('is_test_user', False)
        
        if not is_test_user:
            # Enable persistence for regular users automatically
            st.session_state.persistence_enabled = True
            
            # Load user-specific settings
            user_settings = self.load_user_settings(username)
            user_settings['persistence_enabled'] = True
            user_settings['first_time_user'] = False
            self.save_user_settings(username, user_settings)
            
            # Load user's existing data if it exists
            self.load_all_data_from_files()
        else:
            # Test user - disable persistence but keep session data
            st.session_state.persistence_enabled = False
    
    def load_user_settings(self, username):
        """Load user-specific settings."""
        user_settings_file = self.data_dir / f"{username}_settings.json"
        if user_settings_file.exists():
            try:
                with open(user_settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"Error loading settings for {username}: {e}")
                return {}
        return {'persistence_enabled': True, 'first_time_user': True}
    
    def save_user_settings(self, username, settings):
        """Save user-specific settings."""
        user_settings_file = self.data_dir / f"{username}_settings.json"
        try:
            with open(user_settings_file, 'w') as f:
                json.dump(settings, f, indent=2, default=str)
        except Exception as e:
            st.error(f"Error saving settings for {username}: {e}")
    
    def admin_data_management_interface(self):
        """Admin-only interface for system-wide data management."""
        if not ('user_permissions' in st.session_state and 'admin' in st.session_state.user_permissions):
            st.error("❌ Access denied. Admin privileges required.")
            return
        
        st.markdown("**🗑️ System Data Management**")
        st.warning("⚠️ **Admin Only**: These actions affect all users' data!")
        
        # Show system data status
        all_users = list(st.session_state.get('users', {}).keys())
        total_data_files = 0
        
        for user in all_users:
            for data_type in ['manual_expenses', 'manual_subscriptions', 'grocery_items', 'settings']:
                user_file = self.data_dir / f"{user}_{data_type}.json"
                if user_file.exists():
                    total_data_files += 1
        
        st.info(f"📊 **System Status:**\n- {len(all_users)} total users\n- {total_data_files} data files on disk")
        
        # Clear all user data (keep user accounts)
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧹 Clear All User Data", help="Remove all expenses, subscriptions, and grocery data for ALL users (keeps user accounts)"):
                if st.button("⚠️ Confirm: Clear ALL User Data", type="secondary"):
                    self.clear_all_users_data()
                    st.success("✅ All user data cleared! User accounts preserved.")
                    st.rerun()
        
        with col2:
            if st.button("🗑️ Reset Entire System", help="Remove ALL data including user accounts (fresh start)", type="secondary"):
                if st.button("⚠️ CONFIRM: Complete System Reset", type="secondary"):
                    self.reset_entire_system()
                    st.success("✅ Complete system reset! Starting fresh.")
                    st.rerun()
        
        # Individual user data management
        st.markdown("**👤 Individual User Data Management**")
        
        non_admin_users = [u for u in all_users if u not in ['admin', 'test']]
        if non_admin_users:
            selected_user = st.selectbox("Select user to manage", non_admin_users)
            
            if selected_user:
                user_data_count = 0
                for data_type in ['manual_expenses', 'manual_subscriptions', 'grocery_items']:
                    user_file = self.data_dir / f"{selected_user}_{data_type}.json"
                    if user_file.exists():
                        try:
                            with open(user_file, 'r') as f:
                                data = json.load(f)
                                user_data_count += len(data) if isinstance(data, list) else 1
                        except:
                            pass
                
                st.info(f"📊 **{selected_user}**: {user_data_count} data items")
                
                if st.button(f"🗑️ Clear {selected_user}'s Data"):
                    if st.button(f"⚠️ Confirm: Clear {selected_user}'s Data"):
                        self.clear_specific_user_data(selected_user)
                        st.success(f"✅ {selected_user}'s data cleared!")
                        st.rerun()
        else:
            st.info("No regular users to manage (only admin/test exist)")
    
    def clear_all_users_data(self):
        """Clear all user data files while preserving user accounts."""
        try:
            data_types = ['manual_expenses', 'manual_subscriptions', 'grocery_items', 'settings']
            users = list(st.session_state.get('users', {}).keys())
            
            for user in users:
                for data_type in data_types:
                    user_file = self.data_dir / f"{user}_{data_type}.json"
                    if user_file.exists():
                        user_file.unlink()
            
            # Clear session state for all users
            for key in ['manual_expenses', 'manual_subscriptions', 'grocery_items']:
                if key in st.session_state:
                    st.session_state[key] = []
                    
        except Exception as e:
            st.error(f"Error clearing user data: {e}")
    
    def clear_specific_user_data(self, username):
        """Clear data for a specific user."""
        try:
            data_types = ['manual_expenses', 'manual_subscriptions', 'grocery_items', 'settings']
            
            for data_type in data_types:
                user_file = self.data_dir / f"{username}_{data_type}.json"
                if user_file.exists():
                    user_file.unlink()
                    
        except Exception as e:
            st.error(f"Error clearing data for {username}: {e}")
    
    def reset_entire_system(self):
        """Complete system reset - remove all data and users except admin."""
        try:
            # Remove all data files
            for file_path in self.data_dir.glob("*.json"):
                if file_path.name != "users.json":  # Keep users.json for now
                    file_path.unlink()
            
            # Reset users to just admin and test
            admin_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
            test_password = bcrypt.hashpw("test123".encode('utf-8'), bcrypt.gensalt())
            
            fresh_users = {
                'admin': {
                    'password_hash': admin_password,
                    'role': 'admin',
                    'created_at': datetime.now(),
                    'permissions': ['read', 'write', 'admin'],
                    'is_test_user': False
                },
                'test': {
                    'password_hash': test_password,
                    'role': 'user',
                    'created_at': datetime.now(),
                    'permissions': ['read', 'write'],
                    'is_test_user': True
                }
            }
            
            st.session_state.users = fresh_users
            self.save_users_to_file()
            
            # Clear session state
            for key in ['manual_expenses', 'manual_subscriptions', 'grocery_items']:
                if key in st.session_state:
                    st.session_state[key] = []
                    
        except Exception as e:
            st.error(f"Error during system reset: {e}")
    
    def user_management_interface(self):
        """Interface for managing users (admin only)."""
        if not ('user_permissions' in st.session_state and 'admin' in st.session_state.user_permissions):
            st.error("❌ Access denied. Admin privileges required.")
            return
        
        st.markdown("### 👥 User Management")
        
        # Create new user
        with st.expander("➕ Create New User"):
            with st.form("create_user"):
                new_username = st.text_input("Username*", placeholder="Enter new username")
                new_password = st.text_input("Password*", type="password", placeholder="Enter password")
                new_role = st.selectbox("Role", options=['user', 'admin'], index=0)
                
                permissions = st.multiselect(
                    "Permissions",
                    options=['read', 'write', 'admin'],
                    default=['read', 'write'],
                    help="Select user permissions"
                )
                
                if st.form_submit_button("👤 Create User"):
                    if new_username and new_password:
                        if new_username not in st.session_state.users:
                            self.create_user(new_username, new_password, new_role, permissions)
                            st.success(f"✅ User '{new_username}' created successfully!")
                            st.info(f"💾 **Auto-persistence enabled** for {new_username} - their data will be saved permanently!")
                            st.rerun()
                        else:
                            st.error("❌ Username already exists!")
                    else:
                        st.error("❌ Please fill in all required fields")
        
        # Display existing users
        st.markdown("#### 📋 Existing Users")
        
        users = st.session_state.users
        user_data = []
        
        for username, user_info in users.items():
            user_data.append({
                'Username': username,
                'Role': user_info['role'],
                'Permissions': ', '.join(user_info['permissions']),
                'Created': user_info['created_at'].strftime('%Y-%m-%d')
            })
        
        if user_data:
            df = pd.DataFrame(user_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Delete user
        with st.expander("🗑️ Delete User"):
            user_to_delete = st.selectbox(
                "Select user to delete",
                options=[u for u in users.keys() if u not in ['admin', 'test']],
                help="Cannot delete admin or test users"
            )
            
            if st.button("🗑️ Delete User", type="secondary"):
                if user_to_delete and user_to_delete not in ['admin', 'test']:
                    del st.session_state.users[user_to_delete]
                    self.save_users_to_file()  # Save changes
                    st.success(f"✅ User '{user_to_delete}' deleted!")
                    st.rerun()
    
    def logout(self):
        """Logout current user and handle test user data clearing."""
        if st.sidebar.button("🚪 Logout"):
            # Check if current user is test user and clear their data
            current_user = st.session_state.get('current_user')
            if current_user == 'test':
                self.clear_test_user_data()
                st.sidebar.success("🧹 Test user data cleared!")
            
            # Clear session authentication
            for key in ['authenticated', 'current_user', 'user_role', 'user_permissions']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    def clear_test_user_data(self):
        """Clear all data for test user."""
        # Clear session state data
        for key in ['manual_expenses', 'manual_subscriptions', 'grocery_items']:
            if key in st.session_state:
                st.session_state[key] = []
        
        # Clear test user's files if they exist
        test_files = ["manual_expenses.json", "manual_subscriptions.json", "grocery_items.json"]
        for filename in test_files:
            filepath = self.data_dir / f"test_{filename}"
            if filepath.exists():
                try:
                    filepath.unlink()
                except Exception as e:
                    pass  # Ignore errors when clearing test data
    
    def create_notification_dashboard(self, sms_config):
        """Create a dashboard showing upcoming payments and notification status for manual subscriptions."""
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
                4. Choose notification preferences (default: 1 day ahead)
                5. Select which payment categories to monitor
                
                **Step 4: Add Your Subscriptions**
                1. Use the "Manage Your Subscriptions" section above to add your services
                2. Enter service name, amount, and due day of month
                3. The app will calculate next due dates automatically
                
                **Step 5: Test & Use**
                1. Click "Send Test SMS" to verify setup
                2. Use "Send Payment Alerts Now" for immediate notifications
                3. Alerts will be sent automatically based on your preferences
                
                **💡 Tips:**
                - Twilio free trial works with verified numbers only
                - For production use, upgrade your Twilio account
                - SMS costs about $0.0075 per message
                - Keep your Twilio credentials secure
                - Focus on manually entered subscriptions only
                """)
            return
        
        # Get upcoming payments from manual subscriptions
        upcoming_payments = self.calculate_upcoming_payments(sms_config)
        
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
    
    # Initialize analyzer
    analyzer = StreamlitBankAnalyzer()
    
    # Initialize user system
    analyzer.initialize_users()
    
    # Authentication check
    if not analyzer.login_interface():
        st.stop()
    
    # Show user info in sidebar
    if 'current_user' in st.session_state:
        st.sidebar.markdown(f"👤 **Logged in as:** {st.session_state.current_user}")
        st.sidebar.markdown(f"🔑 **Role:** {st.session_state.user_role}")
        analyzer.logout()
        
        # Admin user management
        if 'admin' in st.session_state.user_permissions:
            with st.sidebar.expander("👥 User Management"):
                analyzer.user_management_interface()
            
            with st.sidebar.expander("🗑️ System Data Management (Admin Only)"):
                analyzer.admin_data_management_interface()
        
        # Data persistence settings
        analyzer.setup_persistence_settings()
    
    # Styled Header
    st.markdown('<h1 class="main-header">💰 Bank Statement Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">📊 Upload your bank statement CSV and get comprehensive financial insights!</div>', unsafe_allow_html=True)
    
    # Show OCR status
    if not OCR_AVAILABLE:
        st.info("ℹ️ **Note:** OCR scanning for receipts is disabled. To enable automatic receipt text extraction, install optional dependencies: `pip install -r requirements-ocr.txt`")
    
    # Quick Expense Entry (TOP PRIORITY - Most Used Feature)
    st.markdown('<div class="chart-header">⚡ Quick Expense Entry</div>', unsafe_allow_html=True)
    analyzer.manage_manual_expenses()
    
    # Sidebar
    st.sidebar.header("📋 Instructions")
    current_user = st.session_state.get('current_user', '')
    is_test_user = current_user == 'test'
    
    if is_test_user:
        st.sidebar.markdown("""
        🧪 **Test User Guide:**
        1. **Quick Entry**: Add test expenses at the top
        2. **Upload CSV**: Try importing sample data (optional)
        3. **View Overview**: See sample financial metrics and charts
        4. **Test Features**: Try subscriptions, groceries, and SMS alerts
        5. **Export Reports**: Generate sample PDF/Excel reports
        6. **Logout**: All test data automatically clears on logout!
        """)
    else:
        st.sidebar.markdown("""
        💾 **Your data auto-saves permanently!**
        1. **Quick Entry**: Add expenses instantly at the top of the page
        2. **Upload CSV**: Import bank statement data (optional)
        3. **View Overview**: See your financial metrics and charts
        4. **Get Insights**: Review personalized financial recommendations
        5. **Manage Items**: Use tabs for subscriptions, groceries, and SMS alerts
        6. **Export Reports**: Generate PDF/Excel reports in the Reports tab
        """)
    
    st.sidebar.markdown("""
    
    **⚡ Quick Expense Entry (Top Priority):**
    - ✏️ **Instant Access**: Add expenses immediately at the top
    - 📅 **Auto-Date**: Date defaults to today for quick entry
    - 🏷️ **Category Dropdown**: 19 preset categories for easy selection
    - 💰 **Amount & Notes**: Quick amount entry with optional notes
    - 🔄 **Real-time Integration**: Instantly appears in all charts and reports
    
    **⚙️ Management Tabs (Organized):**
    - 📋 **Subscriptions**: Track recurring payments with SMS alerts
    - 🛒 **Groceries**: Receipt scanning and item categorization
    - 📱 **SMS Alerts**: Setup payment reminders via Twilio
    
    **📊 Reports & Data (Bottom):**
    - 📄 **PDF Reports**: Professional financial summaries
    - 📊 **Excel Export**: Detailed multi-sheet analysis
    - 📋 **Data View**: Browse all your transaction data
    
    **Interactive Features:**
    - 🔍 **Date & Category Filters**: Focus on specific time periods or categories
    - 📊 **Interactive Charts**: Hover for details, zoom, pan, toggle data
    - 📈 **Real-time Updates**: All charts update based on your filters
    
    **Report Options:**
    - 📄 **PDF**: Visual summary with charts
    - 📊 **Excel**: 9 detailed sheets including transaction analysis
    
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
    
    # Always process data (CSV + manual entries)
    try:
        df = None
        if uploaded_file is not None:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ File uploaded successfully! Found {len(df)} transactions.")
        
        # Process the data (includes manual entries even without CSV)
        processed_df = analyzer.process_dataframe(df)
        
        # Show data source summary
        if processed_df is not None and len(processed_df) > 0:
            sources = processed_df['Source'].value_counts()
            source_info = " | ".join([f"{source}: {count}" for source, count in sources.items()])
            st.info(f"📊 **Data Sources:** {source_info}")
        
        # Continue with analysis even if no CSV (manual entries only)
        if processed_df is not None and len(processed_df) > 0:
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
                
                # Category spending chart (full width)
                st.subheader("💰 Category Spending Analysis")
                category_chart = analyzer.create_category_spending_chart(filtered_df)
                if category_chart:
                    st.plotly_chart(category_chart, use_container_width=True)
                
                # Monthly trends chart (full width)
                st.subheader("📊 Monthly Trends & Savings Rate")
                monthly_chart = analyzer.create_monthly_trends_chart(filtered_df)
                if monthly_chart:
                    st.plotly_chart(monthly_chart, use_container_width=True)
                

                
                # Enhanced Insights section with optimization
                st.markdown('<div class="insight-header">💡 Financial Insights & Recommendations</div>', unsafe_allow_html=True)
                
                # Create columns for different types of insights
                insight_col1, insight_col2 = st.columns([1, 1])
                
                with insight_col1:
                    st.markdown("#### 📊 General Financial Insights")
                    general_insights = analyzer.get_insights(filtered_df, total_income, total_expenses, total_savings, savings_rate)
                    for insight in general_insights:
                        if insight:  # Skip empty lines
                            st.markdown(insight)
                
                with insight_col2:
                    st.markdown("#### 🎯 Expense Optimization Tips")
                    optimization_insights = analyzer.create_expense_optimization_insights(filtered_df)
                    for insight in optimization_insights:
                        if insight:  # Skip empty lines
                            st.markdown(insight)
                
                # Quick Management Section
                st.markdown('<div class="chart-header">⚙️ Expense & Subscription Management</div>', unsafe_allow_html=True)
                
                # Create tabs for better organization
                mgmt_tab1, mgmt_tab2, mgmt_tab3 = st.tabs(["📋 Subscriptions", "🛒 Grocery Receipts", "📱 SMS Alerts"])
                
                with mgmt_tab1:
                    # Manage manual subscriptions
                    subscriptions = analyzer.manage_manual_subscriptions()
                
                with mgmt_tab2:
                    # Manage grocery receipts
                    analyzer.manage_grocery_receipts()
                
                with mgmt_tab3:
                    # SMS Notification Dashboard
                    analyzer.create_notification_dashboard(sms_config)
                
                # Reports & Data Section
                st.markdown('<div class="chart-header">📊 Reports & Data Export</div>', unsafe_allow_html=True)
                
                # Create tabs for reports and data
                report_tab1, report_tab2 = st.tabs(["📄 Generate Reports", "📋 View Data"])
                
                with report_tab1:
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
                
                with report_tab2:
                    # Data preview
                    st.markdown("#### 📋 Filtered Transaction Data")
                    st.dataframe(filtered_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        st.info("Please ensure your CSV file has the correct format with Date, Description, and Amount columns.")
    
    # Show welcome message if no data
    if uploaded_file is None and len(analyzer.load_manual_expenses()) == 0 and len(analyzer.load_grocery_items()) == 0:
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
