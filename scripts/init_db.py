"""
Database Initialization Script
Reads and executes database-setup.sql to create schema and populate sample data
"""
import sqlite3
import os
import sys

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def init_database(db_path: str = 'instance/camerashop.db', sql_file: str = 'database-setup-sqlite.sql'):
    """
    Initialize database with schema and sample data
    
    Args:
        db_path: Path to SQLite database file
        sql_file: Path to SQL setup script (use SQLite version)
    """
    # Ensure instance directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Delete existing database if it exists
    if os.path.exists(db_path):
        print(f"⚠️  Removing existing database: {db_path}")
        os.remove(db_path)
    
    # Read SQL script
    if not os.path.exists(sql_file):
        print(f"❌ Error: SQL file not found: {sql_file}")
        return False
    
    print(f"📖 Reading SQL script: {sql_file}")
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Connect to database and execute script
    print(f"🔧 Creating database: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Execute the entire script
        cursor.executescript(sql_script)
        
        conn.commit()
        
        # Verify data
        print("\n✅ Database created successfully!")
        print("\n📊 Data Summary:")
        print("─" * 50)
        
        cursor.execute("""
            SELECT 'Roles' as Table_Name, COUNT(*) as Count FROM roles
            UNION ALL
            SELECT 'Users', COUNT(*) FROM users
            UNION ALL
            SELECT 'Categories', COUNT(*) FROM categories
            UNION ALL
            SELECT 'Brands', COUNT(*) FROM brands
            UNION ALL
            SELECT 'Products', COUNT(*) FROM products
            UNION ALL
            SELECT 'Carts', COUNT(*) FROM carts
            UNION ALL
            SELECT 'Cart Items', COUNT(*) FROM cart_items
            UNION ALL
            SELECT 'Orders', COUNT(*) FROM orders
            UNION ALL
            SELECT 'Order Items', COUNT(*) FROM order_items
        """)
        
        results = cursor.fetchall()
        for table_name, count in results:
            print(f"{table_name:.<30} {count:>3}")
        
        print("─" * 50)
        print("\n🔑 Test Accounts:")
        print("   Admin:     admin@camerashop.com / 123456")
        print("   Customer1: customer1@example.com / 123456")
        print("   Customer2: customer2@example.com / 123456")
        print("\n✨ Database initialization complete!")
        
        cursor.close()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == '__main__':
    # Run from project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.chdir(project_root)
    
    print("="*70)
    print(" 🏛️  PY-CAMERASHOP DATABASE INITIALIZATION")
    print(" Clean Architecture Implementation - Infrastructure Layer")
    print("="*70)
    print()
    
    success = init_database()
    
    if success:
        print("\n🎉 You can now run the application!")
        print("   python run.py")
        sys.exit(0)
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1)
