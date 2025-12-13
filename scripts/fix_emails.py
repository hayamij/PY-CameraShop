"""
Update admin email in database
"""
import pyodbc

try:
    conn_str = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=CameraShopDB;'
        'Trusted_Connection=yes;'
    )
    
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # Update admin email
    cursor.execute("""
        UPDATE users 
        SET email = 'admin@camerashop.com'
        WHERE username = 'admin'
    """)
    
    # Update customer email
    cursor.execute("""
        UPDATE users 
        SET email = 'customer1@example.com'
        WHERE username = 'customer1'
    """)
    
    conn.commit()
    print("✅ Emails updated successfully!")
    print("   Admin: admin@camerashop.com / 123456")
    print("   Customer: customer1@example.com / 123456")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
