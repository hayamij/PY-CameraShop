"""
Initialize SQL Server Database for Docker - Run database-setup.sql
"""
import pyodbc
import os
import time
import sys

def wait_for_sqlserver(max_retries=30, delay=2):
    """Wait for SQL Server to be ready"""
    conn_str = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=sqlserver;'
        'UID=sa;'
        'PWD=YourStrong@Password123;'
        'DATABASE=master;'
    )
    
    print("⏳ Waiting for SQL Server to be ready...")
    for i in range(max_retries):
        try:
            conn = pyodbc.connect(conn_str, timeout=5)
            conn.close()
            print("✅ SQL Server is ready!")
            return True
        except Exception as e:
            print(f"  Attempt {i+1}/{max_retries}: SQL Server not ready yet...")
            time.sleep(delay)
    
    print("❌ SQL Server failed to start in time")
    return False

def run_sql_file():
    sql_file = 'database-setup.sql'
    
    if not os.path.exists(sql_file):
        print(f"❌ File not found: {sql_file}")
        return False
    
    print(f"📖 Reading SQL file: {sql_file}")
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Split by GO statements
    sql_batches = [batch.strip() for batch in sql_content.split('GO') if batch.strip()]
    
    try:
        # Connect with SQL Server Authentication for Docker
        conn_str = (
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=sqlserver;'
            'UID=sa;'
            'PWD=YourStrong@Password123;'
            'DATABASE=master;'
        )
        
        print("🔌 Connecting to SQL Server...")
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        
        print("🔧 Executing SQL batches...")
        for i, batch in enumerate(sql_batches, 1):
            if batch:
                try:
                    cursor.execute(batch)
                    print(f"  ✅ Batch {i}/{len(sql_batches)} executed")
                except Exception as e:
                    error_msg = str(e)
                    # Ignore "database already exists" and similar warnings
                    if 'already exists' not in error_msg.lower():
                        print(f"  ⚠️  Batch {i} warning: {error_msg[:150]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Database initialized successfully!")
        print("\n🔑 Test Accounts:")
        print("   Admin: admin@gmail.com / admin123")
        print("   Customer: user@gmail.com / user123")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 SQL Server Database Initialization Script (Docker)")
    print("=" * 60)
    
    # Wait for SQL Server to be ready
    if not wait_for_sqlserver():
        sys.exit(1)
    
    # Run SQL setup script
    if run_sql_file():
        print("\n✅ All done! Application can now start.")
        sys.exit(0)
    else:
        print("\n❌ Initialization failed!")
        sys.exit(1)
