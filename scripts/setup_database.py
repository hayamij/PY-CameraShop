"""
Simple Database Setup Script
Just run this file to initialize the database with all sample data
"""
import sqlite3
import os

# Database file path
DB_PATH = 'instance/camerashop.db'
SQL_FILE = 'database-setup-sqlite.sql'

def setup_database():
    """Initialize database from SQL file"""
    
    # Ensure instance directory exists
    os.makedirs('instance', exist_ok=True)
    
    # Remove existing database
    if os.path.exists(DB_PATH):
        print(f"🗑️  Removing existing database: {DB_PATH}")
        os.remove(DB_PATH)
    
    # Read SQL script
    print(f"📖 Reading SQL script: {SQL_FILE}")
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Execute SQL script
    print(f"🔧 Creating database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()
    
    print("\n✅ Database setup complete!")
    print("\n🔑 Test Accounts:")
    print("   Admin: admin@gmail.com / 123456")
    print("   User:  user@gmail.com / 123456")
    print("\n🎉 You can now run: python run.py")

if __name__ == '__main__':
    setup_database()
