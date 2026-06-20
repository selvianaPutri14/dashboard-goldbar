# ==========================================================
# database.py
# GoldSight - Gold Price Prediction System
# ==========================================================

import sqlite3
from pathlib import Path

# ==========================================================
# DATABASE CONFIG
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "goldbar.db"

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# ==========================================================
# ADMINS
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT,
    role TEXT DEFAULT 'admin',
    status TEXT DEFAULT 'aktif',
    last_login DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ==========================================================
# ADMIN LOGIN LOGS
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS admin_login_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER,
    ip_address TEXT,
    browser TEXT,
    operating_system TEXT,
    login_time DATETIME,
    logout_time DATETIME,
    FOREIGN KEY(admin_id) REFERENCES admins(id)
)
""")

# ==========================================================
# ACTIVITY LOGS
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER,
    aktivitas TEXT,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(admin_id) REFERENCES admins(id)
)
""")

# ==========================================================
# VISITOR LOGS
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS visitor_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT,
    country TEXT,
    city TEXT,
    browser TEXT,
    device TEXT,
    halaman TEXT,
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ==========================================================
# FEEDBACK
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    email TEXT,
    rating INTEGER,
    pesan TEXT,
    status TEXT DEFAULT 'baru',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ==========================================================
# HISTORICAL GOLD PRICE
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS gold_price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal DATE NOT NULL,
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    volume INTEGER,
    source TEXT DEFAULT 'Yahoo Finance',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ==========================================================
# YAHOO FINANCE DATA
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS yahoo_finance_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    datetime DATETIME,
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    volume INTEGER,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ==========================================================
# GOLD PREDICTIONS
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS gold_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_date DATE,
    predicted_price REAL,
    algorithm TEXT,
    accuracy REAL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ==========================================================
# FAQ
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS faq (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(created_by) REFERENCES admins(id)
)
""")

# ==========================================================
# INFORMATION
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS information (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    updated_by INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(updated_by) REFERENCES admins(id)
)
""")

# ==========================================================
# WEBSITE SETTINGS
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS website_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_name TEXT,
    logo TEXT,
    favicon TEXT,
    footer_text TEXT,
    maintenance_mode INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ==========================================================
# ARTICLES
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    thumbnail TEXT,
    content TEXT,
    author_id INTEGER,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(author_id) REFERENCES admins(id)
)
""")

# ==========================================================
# NOTIFICATIONS
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    message TEXT,
    status TEXT DEFAULT 'unread',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ==========================================================
# IMPORT LOGS
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS import_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    imported_by INTEGER,
    file_name TEXT,
    total_rows INTEGER,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(imported_by) REFERENCES admins(id)
)
""")

# ==========================================================
# MACHINE LEARNING MODELS
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS ml_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT,
    algorithm TEXT,
    accuracy REAL,
    training_date DATETIME,
    file_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ==========================================================
# DEFAULT ADMIN
# username : admin
# password : admin123
# ==========================================================

cursor.execute("""
INSERT OR IGNORE INTO admins (
    id,
    nama,
    username,
    password,
    email,
    role
)
VALUES (
    1,
    'Super Admin',
    'admin',
    'admin123',
    'admin@gmail.com',
    'superadmin'
)
""")

# ==========================================================
# DEFAULT FAQ
# ==========================================================

cursor.execute("""
INSERT OR IGNORE INTO faq (
    id,
    question,
    answer,
    created_by
)
VALUES (
    1,
    'Apa itu GoldSight?',
    'GoldSight adalah sistem prediksi harga emas.',
    1
)
""")

# ==========================================================
# DEFAULT INFORMATION
# ==========================================================

cursor.execute("""
INSERT OR IGNORE INTO information (
    id,
    title,
    content,
    updated_by
)
VALUES (
    1,
    'Tentang Sistem',
    'Sistem prediksi harga emas berbasis Machine Learning.',
    1
)
""")

# ==========================================================
# WEBSITE SETTINGS
# ==========================================================

cursor.execute("""
INSERT OR IGNORE INTO website_settings (
    id,
    site_name,
    footer_text
)
VALUES (
    1,
    'GoldSight',
    '© GoldSight 2026'
)
""")

# ==========================================================
# COMMIT
# ==========================================================

conn.commit()

print("Database goldbar.db berhasil dibuat.")

conn.close()