"""
MechanicGo database layer — dual backend.

- If DB_HOST is set (e.g. external MySQL on Railway), the original MySQL
  logic below is used unchanged.
- Otherwise the app automatically falls back to a local SQLite file, so it
  can run on free hosts (e.g. Render free tier) with zero external services.
  The SQLite path exposes the same get_db()/init_db() interface to app.py.
"""
import os
import re
import math
import sqlite3
import datetime

from dotenv import load_dotenv

load_dotenv()

USE_SQLITE = not os.getenv("DB_HOST")

if not USE_SQLITE:
    try:
        import mysql.connector
        from mysql.connector import pooling
    except ImportError:
        print("mysql-connector-python not installed; falling back to SQLite")
        USE_SQLITE = True

# ─── SQLite backend ──────────────────────────────────────────────────────────

SQLITE_PATH = os.getenv("SQLITE_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "mechanicgo.db"))


def _safe_acos(x):
    """MySQL ACOS returns NULL out of domain; emulate to avoid float noise crashes."""
    try:
        return math.acos(max(-1.0, min(1.0, float(x))))
    except (ValueError, TypeError):
        return None


def _translate_sql(sql):
    """Translate the MySQL-flavoured SQL used in app.py into SQLite dialect."""
    sql = sql.replace("%s", "?")
    sql = re.sub(r"NOW\(\)", "datetime('now')", sql, flags=re.IGNORECASE)
    sql = re.sub(
        r"DATE_SUB\(datetime\('now'\),\s*INTERVAL\s+(\d+)\s+DAY\)",
        r"datetime('now', '-\1 days')",
        sql,
        flags=re.IGNORECASE,
    )
    return sql


class _SQLiteCursor:
    """Cursor wrapper: dict rows, %-placeholder and NOW() translation."""

    def __init__(self, cur):
        self._cur = cur

    def execute(self, sql, params=()):
        params = tuple(
            p.strftime("%Y-%m-%d %H:%M:%S") if isinstance(p, (datetime.datetime, datetime.date)) else p
            for p in params
        )
        self._cur.execute(_translate_sql(sql), params)
        return self

    def fetchone(self):
        row = self._cur.fetchone()
        return dict(row) if row is not None else None

    def fetchall(self):
        return [dict(r) for r in self._cur.fetchall()]

    @property
    def lastrowid(self):
        return self._cur.lastrowid

    def close(self):
        self._cur.close()


class _SQLiteConn:
    def __init__(self, conn):
        self._conn = conn

    def cursor(self, dictionary=False):
        return _SQLiteCursor(self._conn.cursor())

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def _new_sqlite_conn():
    conn = sqlite3.connect(SQLITE_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    # Register math functions used by the nearest-mechanic query in app.py
    conn.create_function("RADIANS", 1, math.radians)
    conn.create_function("ACOS", 1, _safe_acos)
    conn.create_function("COS", 1, math.cos)
    conn.create_function("SIN", 1, math.sin)
    return conn


def _sqlite_get_db():
    return _SQLiteConn(_new_sqlite_conn())


def _sqlite_init_db():
    conn = _new_sqlite_conn()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role TEXT DEFAULT 'user',
            phone VARCHAR(20),
            profile_pic VARCHAR(255),
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token VARCHAR(100) UNIQUE NOT NULL,
            role VARCHAR(20) NOT NULL,
            expires_at DATETIME NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mechanics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            specialty VARCHAR(100) DEFAULT 'General',
            bio TEXT,
            experience_years INTEGER DEFAULT 0,
            latitude REAL,
            longitude REAL,
            is_available INTEGER DEFAULT 1,
            rating REAL DEFAULT 0.00,
            total_jobs INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sos_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mechanic_id INTEGER,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            issue_type VARCHAR(100) DEFAULT 'General',
            description TEXT,
            status TEXT DEFAULT 'searching',
            estimated_arrival INTEGER,
            actual_arrival TIMESTAMP NULL,
            completed_at TIMESTAMP NULL,
            fare REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (mechanic_id) REFERENCES mechanics(id) ON DELETE SET NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER UNIQUE NOT NULL,
            mechanic_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
            review TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (request_id) REFERENCES sos_requests(id) ON DELETE CASCADE,
            FOREIGN KEY (mechanic_id) REFERENCES mechanics(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title VARCHAR(200) NOT NULL,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'info',
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            method TEXT DEFAULT 'cash',
            status TEXT DEFAULT 'pending',
            transaction_id VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (request_id) REFERENCES sos_requests(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Create default admin user if not exists
    cursor.execute("SELECT id FROM users WHERE email='admin@mechanicgo.com'")
    if not cursor.fetchone():
        import hashlib
        pw = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?,?,?,'admin')",
            ("Admin", "admin@mechanicgo.com", pw)
        )

    conn.commit()
    conn.close()
    print("Database initialized successfully (SQLite)")


# ─── MySQL backend (original code, unchanged) ────────────────────────────────

if not USE_SQLITE:
    db_config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "port": int(os.getenv("DB_PORT", 3306))
    }

    try:
        connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="mechanicgo_pool", pool_size=10, **db_config
        )
    except mysql.connector.Error as err:
        print(f"Pool error (will retry on first request): {err}")
        connection_pool = None


def _mysql_get_db():
    global connection_pool
    if connection_pool is None:
        connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="mechanicgo_pool2", pool_size=10, **db_config
        )
    return connection_pool.get_connection()


def _mysql_init_db():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306))
    )

    cursor = conn.cursor()
    db_name = os.getenv("DB_NAME", "mechanicgo")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    cursor.execute(f"USE {db_name}")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('user', 'mechanic', 'admin') DEFAULT 'user',
            phone VARCHAR(20),
            profile_pic VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            token VARCHAR(100) UNIQUE NOT NULL,
            role VARCHAR(20) NOT NULL,
            expires_at DATETIME NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mechanics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT UNIQUE NOT NULL,
            specialty VARCHAR(100) DEFAULT 'General',
            bio TEXT,
            experience_years INT DEFAULT 0,
            latitude DECIMAL(10,8),
            longitude DECIMAL(11,8),
            is_available BOOLEAN DEFAULT TRUE,
            rating DECIMAL(3,2) DEFAULT 0.00,
            total_jobs INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sos_requests (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            mechanic_id INT,
            latitude DECIMAL(10,8) NOT NULL,
            longitude DECIMAL(11,8) NOT NULL,
            issue_type VARCHAR(100) DEFAULT 'General',
            description TEXT,
            status ENUM('searching', 'dispatched', 'in_progress', 'completed', 'cancelled') DEFAULT 'searching',
            estimated_arrival INT,
            actual_arrival TIMESTAMP NULL,
            completed_at TIMESTAMP NULL,
            fare DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (mechanic_id) REFERENCES mechanics(id) ON DELETE SET NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            request_id INT UNIQUE NOT NULL,
            mechanic_id INT NOT NULL,
            user_id INT NOT NULL,
            rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
            review TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (request_id) REFERENCES sos_requests(id) ON DELETE CASCADE,
            FOREIGN KEY (mechanic_id) REFERENCES mechanics(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(200) NOT NULL,
            message TEXT NOT NULL,
            type ENUM('info', 'success', 'warning', 'error') DEFAULT 'info',
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            request_id INT NOT NULL,
            user_id INT NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            method ENUM('cash', 'card', 'upi') DEFAULT 'cash',
            status ENUM('pending', 'completed', 'refunded') DEFAULT 'pending',
            transaction_id VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (request_id) REFERENCES sos_requests(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Create default admin user if not exists
    cursor.execute("SELECT id FROM users WHERE email='admin@mechanicgo.com'")
    if not cursor.fetchone():
        import hashlib
        pw = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (%s,%s,%s,'admin')",
            ("Admin", "admin@mechanicgo.com", pw)
        )

    conn.commit()
    conn.close()
    print("Database initialized successfully (MySQL)")


# ─── Public interface ────────────────────────────────────────────────────────

def get_db():
    if USE_SQLITE:
        return _sqlite_get_db()
    return _mysql_get_db()


def init_db():
    if USE_SQLITE:
        return _sqlite_init_db()
    return _mysql_init_db()
