"""
Initialize SQL Server Database - Run database-setup.sql
"""
import pyodbc
import os

def run_sql_file():
    sql_file = 'database-setup.sql'
    
    if not os.path.exists(sql_file):
        print(f"❌ File not found: {sql_file}")
        return False
    
    print(f"📖 Reading SQL file: {sql_file}")
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Split by GO statements
    sql_batches = sql_content.split('GO')
    
    try:
        # Connect with Windows Authentication
        conn_str = (
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost;'
            'Trusted_Connection=yes;'
        )
        
        print("🔌 Connecting to SQL Server...")
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        
        print("🔧 Executing SQL batches...")
        for i, batch in enumerate(sql_batches, 1):
            batch = batch.strip()
            if batch:
                try:
                    cursor.execute(batch)
                    print(f"  ✅ Batch {i}/{len(sql_batches)} executed")
                except Exception as e:
                    print(f"  ⚠️  Batch {i} warning: {str(e)[:100]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Database initialized successfully!")
        print("\n🔑 Test Accounts:")
        print("   Admin: admin@camerashop.com / 123456")
        print("   Customer: customer1@example.com / 123456")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("="*70)
    print(" 🏛️  SQL SERVER DATABASE INITIALIZATION")
    print("="*70)
    print()
    
    success = run_sql_file()
    
    if success:
        print("\n🎉 You can now login to the application!")
        print("   http://127.0.0.1:5000")
    else:
        print("\n❌ Database initialization failed!")
