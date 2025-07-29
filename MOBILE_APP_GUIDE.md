# 📱 Mobile App & Offline Deployment Guide

This guide explains how to convert your Bank Statement Analyzer into a mobile app that works offline with password protection.

## 🎯 **Mobile App Options**

### **Option 1: Progressive Web App (PWA) - Recommended**

#### **✅ Advantages:**
- Works on all devices (Android, iOS, Desktop)
- No app store approval needed
- Offline functionality with service workers
- Native-like experience
- Easy to update and maintain

#### **📱 Implementation Steps:**

1. **Install PWA Dependencies:**
```bash
pip install streamlit-pwa-runtime
```

2. **Create PWA Configuration:**
```python
# Add to app.py
import streamlit as st
from streamlit_pwa import pwa_runtime

# Enable PWA
pwa_runtime.enable_pwa()

# Configure PWA settings
st.set_page_config(
    page_title="Finance Analyzer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
    # PWA settings
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Finance Analyzer - Your Personal Financial Assistant"
    }
)
```

3. **Add Service Worker (create `static/sw.js`):**
```javascript
const CACHE_NAME = 'finance-analyzer-v1';
const urlsToCache = [
  '/',
  '/static/manifest.json',
  '/static/icon-192x192.png',
  '/static/icon-512x512.png'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});
```

4. **Create Web App Manifest (`static/manifest.json`):**
```json
{
  "name": "Finance Analyzer",
  "short_name": "FinanceApp",
  "description": "Personal Finance Management Tool",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#4CAF50",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "categories": ["finance", "productivity", "utilities"]
}
```

### **Option 2: Native Mobile App**

#### **🔧 Using Kivy + Python:**

1. **Install Kivy:**
```bash
pip install kivy kivymd buildozer
```

2. **Create Mobile Interface:**
```python
# mobile_app.py
from kivy.app import App
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel

class FinanceApp(MDApp):
    def build(self):
        screen = MDScreen()
        
        # Add expense entry form
        expense_field = MDTextField(
            hint_text="Enter expense amount",
            helper_text="Amount in dollars",
            mode="rectangle"
        )
        
        submit_button = MDRaisedButton(
            text="Add Expense",
            on_release=self.add_expense
        )
        
        screen.add_widget(expense_field)
        screen.add_widget(submit_button)
        
        return screen
    
    def add_expense(self, instance):
        # Expense logic here
        pass

FinanceApp().run()
```

3. **Create buildozer.spec for Android:**
```ini
[app]
title = Finance Analyzer
package.name = financeanalyzer
package.domain = com.yourname.financeanalyzer

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0
requirements = python3,kivy,kivymd,pandas,numpy

[buildozer]
log_level = 2

[android]
package = com.yourname.financeanalyzer
permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,CAMERA
```

## 🔒 **Offline Data Storage Solutions**

### **Option 1: SQLite Database (Recommended)**

```python
import sqlite3
import json
from datetime import datetime

class OfflineStorage:
    def __init__(self, db_path="finance_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password_hash TEXT,
                role TEXT,
                permissions TEXT,
                created_at TIMESTAMP
            )
        ''')
        
        # Expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                date DATE,
                description TEXT,
                amount REAL,
                category TEXT,
                expense_type TEXT,
                source TEXT,
                notes TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Subscriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                service_name TEXT,
                amount REAL,
                due_day INTEGER,
                category TEXT,
                notes TEXT,
                next_due_date DATE,
                active BOOLEAN,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Grocery items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grocery_items (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                date DATE,
                store TEXT,
                item_name TEXT,
                category TEXT,
                price REAL,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_expense(self, user_id, expense_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO expenses (user_id, date, description, amount, category, expense_type, source, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, expense_data['date'], expense_data['description'],
            expense_data['amount'], expense_data['category'], expense_data['type'],
            expense_data['source'], expense_data.get('notes', ''), datetime.now()
        ))
        
        conn.commit()
        conn.close()
    
    def get_user_expenses(self, user_id, start_date=None, end_date=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM expenses WHERE user_id = ?"
        params = [user_id]
        
        if start_date and end_date:
            query += " AND date BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        
        cursor.execute(query, params)
        expenses = cursor.fetchall()
        conn.close()
        
        return expenses
```

### **Option 2: Encrypted JSON Files**

```python
import json
import os
from cryptography.fernet import Fernet

class EncryptedStorage:
    def __init__(self, data_dir="user_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.key = self.load_or_create_key()
        self.cipher = Fernet(self.key)
    
    def load_or_create_key(self):
        key_file = os.path.join(self.data_dir, "key.key")
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key
    
    def save_user_data(self, username, data):
        filename = os.path.join(self.data_dir, f"{username}.json")
        encrypted_data = self.cipher.encrypt(json.dumps(data).encode())
        
        with open(filename, "wb") as f:
            f.write(encrypted_data)
    
    def load_user_data(self, username):
        filename = os.path.join(self.data_dir, f"{username}.json")
        if not os.path.exists(filename):
            return {}
        
        with open(filename, "rb") as f:
            encrypted_data = f.read()
        
        decrypted_data = self.cipher.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
```

## 📲 **Deployment Options**

### **1. Local Deployment (Recommended for Offline)**

```bash
# Create standalone executable
pip install pyinstaller

# Generate executable
pyinstaller --onefile --windowed app.py

# Or create a package
pyinstaller --onedir --windowed app.py
```

### **2. Local Server with Auto-Start**

```python
# create_desktop_app.py
import subprocess
import webbrowser
import time
import threading
from streamlit.web import cli as stcli
import sys

def run_streamlit():
    """Run streamlit app"""
    sys.argv = ["streamlit", "run", "app.py", "--server.headless", "true", "--server.port", "8521"]
    stcli.main()

def open_browser():
    """Open browser after delay"""
    time.sleep(3)
    webbrowser.open('http://localhost:8521')

if __name__ == "__main__":
    # Start streamlit in background
    streamlit_thread = threading.Thread(target=run_streamlit)
    streamlit_thread.daemon = True
    streamlit_thread.start()
    
    # Open browser
    open_browser()
    
    # Keep alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
```

### **3. Docker Container for Easy Distribution**

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

```bash
# Build and run
docker build -t finance-analyzer .
docker run -p 8501:8501 -v $(pwd)/user_data:/app/user_data finance-analyzer
```

## 🔐 **Enhanced Security Features**

### **Multi-Factor Authentication**

```python
import pyotp
import qrcode

class MFAManager:
    def generate_secret(self, username):
        secret = pyotp.random_base32()
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=username,
            issuer_name="Finance Analyzer"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        return secret, qr
    
    def verify_token(self, secret, token):
        totp = pyotp.TOTP(secret)
        return totp.verify(token)
```

### **Data Backup & Sync**

```python
import zipfile
from datetime import datetime

class BackupManager:
    def create_backup(self, data_dir, backup_dir="backups"):
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"finance_backup_{timestamp}.zip")
        
        with zipfile.ZipFile(backup_file, 'w') as zipf:
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, data_dir))
        
        return backup_file
    
    def restore_backup(self, backup_file, data_dir):
        with zipfile.ZipFile(backup_file, 'r') as zipf:
            zipf.extractall(data_dir)
```

## 📱 **Mobile-Specific Features**

### **Camera Integration for Receipts**

```python
# For web-based camera access
import streamlit as st
from streamlit_webrtc import webrtc_streamer
import cv2

def mobile_camera_component():
    st.markdown("### 📷 Take Photo with Camera")
    
    webrtc_ctx = webrtc_streamer(
        key="receipt-camera",
        mode=WebRtcMode.SENDONLY,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    
    if webrtc_ctx.video_frame:
        img = webrtc_ctx.video_frame.to_ndarray(format="bgr24")
        return img
    
    return None
```

### **Push Notifications**

```python
# For PWA push notifications
def setup_push_notifications():
    notification_script = """
    <script>
    if ('serviceWorker' in navigator && 'PushManager' in window) {
        navigator.serviceWorker.register('/static/sw.js')
        .then(function(registration) {
            return registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: 'YOUR_VAPID_KEY'
            });
        })
        .then(function(subscription) {
            console.log('Push subscription successful');
        });
    }
    
    function sendNotification(title, body) {
        if (Notification.permission === 'granted') {
            new Notification(title, { body: body });
        }
    }
    </script>
    """
    
    st.components.v1.html(notification_script, height=0)
```

## 🚀 **Quick Start Commands**

```bash
# 1. Install additional dependencies
pip install -r requirements.txt
pip install pyinstaller streamlit-pwa-runtime

# 2. Create standalone app
pyinstaller --onefile --windowed app.py

# 3. Or run as PWA
streamlit run app.py --server.headless true

# 4. For mobile development
pip install kivy kivymd buildozer
buildozer android debug
```

## 💡 **Best Practices**

1. **Data Security:** Always encrypt sensitive data
2. **Offline Sync:** Implement data synchronization when online
3. **Error Handling:** Graceful handling of network failures
4. **Battery Optimization:** Minimize background processing
5. **Storage Management:** Implement data cleanup and archiving
6. **User Experience:** Touch-friendly interfaces and gestures
7. **Performance:** Optimize for mobile CPU and memory constraints

## 📞 **Support & Customization**

For custom mobile app development or enterprise deployment, this framework provides the foundation for:

- Custom branding and themes
- Enterprise SSO integration
- Advanced reporting and analytics
- Multi-tenant architecture
- Cloud sync capabilities
- White-label solutions

Your Finance Analyzer is now ready to be deployed as a secure, offline-capable mobile application! 🎉 