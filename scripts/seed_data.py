"""
Seed Data Script - Create initial admin user and sample data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.factory import create_app
from app.infrastructure.database.db import db
from app.infrastructure.database.models import (
    UserModel, CategoryModel, BrandModel, ProductModel
)
from flask_bcrypt import Bcrypt
from datetime import datetime


def seed_admin_user(bcrypt):
    """Create default admin user"""
    print("Creating admin user...")
    
    # Check if admin exists
    admin = UserModel.query.filter_by(username='admin').first()
    if admin:
        print("  ⚠️  Admin user already exists")
        return admin
    
    # Create admin
    admin = UserModel(
        username='adminn',
        email='admin@camerashop.com',
        password_hash=bcrypt.generate_password_hash('123123').decode('utf-8'),
        full_name='Administrator',
        phone_number='0123456789',
        address='123 Admin Street, Camera City',
        role='ADMIN',
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    db.session.add(admin)
    db.session.commit()
    print("  ✅ Admin user created (username: adminn, password: 123123)")
    return admin


def seed_customers(bcrypt):
    """Create sample customer accounts"""
    print("\nCreating sample customers...")
    
    customers = [
        {
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'password123',
            'full_name': 'John Doe',
            'phone_number': '0987654321',
            'address': '456 Customer Ave, Photo Town'
        },
        {
            'username': 'jane_smith',
            'email': 'jane@example.com',
            'password': 'password123',
            'full_name': 'Jane Smith',
            'phone_number': '0976543210',
            'address': '789 Buyer Blvd, Camera District'
        }
    ]
    
    created = 0
    for customer_data in customers:
        existing = UserModel.query.filter_by(username=customer_data['username']).first()
        if existing:
            print(f"  ⚠️  Customer '{customer_data['username']}' already exists")
            continue
        
        customer = UserModel(
            username=customer_data['username'],
            email=customer_data['email'],
            password_hash=bcrypt.generate_password_hash(customer_data['password']).decode('utf-8'),
            full_name=customer_data['full_name'],
            phone_number=customer_data['phone_number'],
            address=customer_data['address'],
            role='CUSTOMER',
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(customer)
        created += 1
    
    db.session.commit()
    print(f"  ✅ Created {created} customer accounts")


def seed_categories():
    """Create product categories"""
    print("\nCreating categories...")
    
    categories = [
        {'name': 'Máy ảnh DSLR', 'slug': 'may-anh-dslr', 'description': 'Máy ảnh DSLR chuyên nghiệp'},
        {'name': 'Máy ảnh Mirrorless', 'slug': 'may-anh-mirrorless', 'description': 'Máy ảnh không gương lật hiện đại'},
        {'name': 'Ống kính', 'slug': 'ong-kinh', 'description': 'Ống kính cho các loại máy ảnh'},
        {'name': 'Phụ kiện', 'slug': 'phu-kien', 'description': 'Phụ kiện máy ảnh đa dạng'},
        {'name': 'Tripod & Gimbal', 'slug': 'tripod-gimbal', 'description': 'Chân máy và gimbal ổn định'},
    ]
    
    created = 0
    for cat_data in categories:
        existing = CategoryModel.query.filter_by(slug=cat_data['slug']).first()
        if existing:
            print(f"  ⚠️  Category '{cat_data['name']}' already exists")
            continue
        
        category = CategoryModel(
            name=cat_data['name'],
            slug=cat_data['slug'],
            description=cat_data['description'],
            created_at=datetime.utcnow()
        )
        db.session.add(category)
        created += 1
    
    db.session.commit()
    print(f"  ✅ Created {created} categories")


def seed_brands():
    """Create camera brands"""
    print("\nCreating brands...")
    
    brands = [
        {'name': 'Canon', 'description': 'Thương hiệu máy ảnh hàng đầu từ Nhật Bản'},
        {'name': 'Nikon', 'description': 'Máy ảnh chuyên nghiệp chất lượng cao'},
        {'name': 'Sony', 'description': 'Công nghệ mirrorless tiên tiến'},
        {'name': 'Fujifilm', 'description': 'Phong cách nhiếp ảnh cổ điển'},
        {'name': 'Sigma', 'description': 'Ống kính chất lượng cao'},
    ]
    
    created = 0
    for brand_data in brands:
        existing = BrandModel.query.filter_by(name=brand_data['name']).first()
        if existing:
            print(f"  ⚠️  Brand '{brand_data['name']}' already exists")
            continue
        
        brand = BrandModel(
            name=brand_data['name'],
            description=brand_data['description'],
            created_at=datetime.utcnow()
        )
        db.session.add(brand)
        created += 1
    
    db.session.commit()
    print(f"  ✅ Created {created} brands")


def seed_products():
    """Create sample products"""
    print("\nCreating products...")
    
    # Get categories and brands
    dslr_cat = CategoryModel.query.filter_by(slug='may-anh-dslr').first()
    mirrorless_cat = CategoryModel.query.filter_by(slug='may-anh-mirrorless').first()
    lens_cat = CategoryModel.query.filter_by(slug='ong-kinh').first()
    
    canon = BrandModel.query.filter_by(name='Canon').first()
    nikon = BrandModel.query.filter_by(name='Nikon').first()
    sony = BrandModel.query.filter_by(name='Sony').first()
    sigma = BrandModel.query.filter_by(name='Sigma').first()
    
    products = [
        {
            'name': 'Canon EOS 90D',
            'description': 'Máy ảnh DSLR 32.5MP, video 4K, AF 45 điểm',
            'price': 32999000,
            'stock_quantity': 15,
            'category_id': dslr_cat.id if dslr_cat else None,
            'brand_id': canon.id if canon else None,
            'is_visible': True
        },
        {
            'name': 'Nikon D850',
            'description': 'Máy ảnh DSLR Full-frame 45.7MP, video 4K',
            'price': 75999000,
            'stock_quantity': 8,
            'category_id': dslr_cat.id if dslr_cat else None,
            'brand_id': nikon.id if nikon else None,
            'is_visible': True
        },
        {
            'name': 'Sony A7 IV',
            'description': 'Máy ảnh Mirrorless Full-frame 33MP, video 4K 60p',
            'price': 62999000,
            'stock_quantity': 12,
            'category_id': mirrorless_cat.id if mirrorless_cat else None,
            'brand_id': sony.id if sony else None,
            'is_visible': True
        },
        {
            'name': 'Canon EOS R6 Mark II',
            'description': 'Máy ảnh Mirrorless Full-frame 24.2MP, video 6K',
            'price': 68999000,
            'stock_quantity': 10,
            'category_id': mirrorless_cat.id if mirrorless_cat else None,
            'brand_id': canon.id if canon else None,
            'is_visible': True
        },
        {
            'name': 'Sigma 24-70mm f/2.8 DG DN Art',
            'description': 'Ống kính zoom chuẩn cho Mirrorless',
            'price': 28999000,
            'stock_quantity': 20,
            'category_id': lens_cat.id if lens_cat else None,
            'brand_id': sigma.id if sigma else None,
            'is_visible': True
        },
        {
            'name': 'Canon RF 50mm f/1.8 STM',
            'description': 'Ống kính Fix giá rẻ chất lượng cao',
            'price': 5999000,
            'stock_quantity': 30,
            'category_id': lens_cat.id if lens_cat else None,
            'brand_id': canon.id if canon else None,
            'is_visible': True
        },
    ]
    
    created = 0
    for prod_data in products:
        existing = ProductModel.query.filter_by(name=prod_data['name']).first()
        if existing:
            print(f"  ⚠️  Product '{prod_data['name']}' already exists")
            continue
        
        product = ProductModel(**prod_data, created_at=datetime.utcnow())
        db.session.add(product)
        created += 1
    
    db.session.commit()
    print(f"  ✅ Created {created} products")


def main():
    """Main seed function"""
    print("=" * 60)
    print("🌱 SEEDING DATABASE")
    print("=" * 60)
    
    # Create app context
    app = create_app('development')
    bcrypt = Bcrypt(app)
    
    with app.app_context():
        # Seed data
        seed_admin_user(bcrypt)
        seed_customers(bcrypt)
        seed_categories()
        seed_brands()
        seed_products()
        
        print("\n" + "=" * 60)
        print("✅ DATABASE SEEDED SUCCESSFULLY!")
        print("=" * 60)
        print("\n📋 Default Accounts:")
        print("  Admin:")
        print("    Username: admin")
        print("    Password: admin123")
        print("    Email: admin@camerashop.com")
        print("\n  Customers:")
        print("    Username: john_doe / Password: password123")
        print("    Username: jane_smith / Password: password123")
        print("=" * 60)


if __name__ == '__main__':
    main()
