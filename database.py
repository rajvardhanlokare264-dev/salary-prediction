import sqlite3
import hashlib
from sqlite3 import Error

def create_connection():
    try:
        conn = sqlite3.connect('users.db')
        return conn
    except Error as e:
        print(e)
        return None

def init_db():
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL
                )
            ''')
            conn.commit()
        except Error as e:
            print(e)
        finally:
            conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, email):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            hashed_password = hash_password(password)
            cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                         (username, hashed_password, email))
            conn.commit()
            return True
        except Error as e:
            print(e)
            return False
        finally:
            conn.close()

def verify_user(username, password):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            hashed_password = hash_password(password)
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                         (username, hashed_password))
            user = cursor.fetchone()
            return user is not None
        except Error as e:
            print(e)
            return False
        finally:
            conn.close()

# Initialize the database when this module is imported
init_db()
