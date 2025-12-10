# 📷 PY-CameraShop

> **E-commerce Website for Camera & Accessories**  
> Built with Flask following Clean Architecture principles

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-481%20passed-brightgreen.svg)](tests/)

---

## 🎯 Project Overview

**PY-CameraShop** là website bán máy ảnh & phụ kiện được xây dựng với Flask framework, tuân theo **Clean Architecture** nghiêm ngặt để đảm bảo:

- ✅ **Maintainability** - Code dễ bảo trì và mở rộng
- ✅ **Testability** - Logic nghiệp vụ hoàn toàn độc lập (481 tests passing)
- ✅ **Scalability** - Kiến trúc có khả năng mở rộng cao
- ✅ **Independence** - Không phụ thuộc vào framework hay database cụ thể

### 🎉 **Project Status: PRODUCTION READY**

✅ **ALL PHASES COMPLETED:**
- Phase 1: Database Setup ✅
- Phase 2: Infrastructure Layer ✅
- Phase 3: Repository Adapters ✅  
- Phase 4: HTTP Controllers (14 endpoints) ✅
- Phase 5: Frontend Interface ✅
- Phase 6: Testing (481/481 tests passing) ✅

---

### 🌟 Key Features

#### 🔓 For Guests:
- 🏠 Browse homepage with featured products
- 🔍 Search and filter products (category, brand, price)
- 📄 View detailed product information
- 📂 Browse by categories and brands

#### 👤 For Customers:
- 🔐 Register / Login with secure authentication
- 🛒 Shopping cart management (add, update, remove)
- 💳 Place orders with multiple payment methods
- 📦 View order history and track status
- ❌ Cancel pending orders
- 👤 Profile management

#### 👨‍💼 For Admins:
- 📊 Admin dashboard with statistics
- 📦 Product management (CRUD operations)
- 🛍️ Order management & status updates
- 👥 User account management
- 📂 Category & Brand management
- 📈 Sales reports & analytics

---

## 🏗️ Architecture

Dự án tuân theo **Clean Architecture** với 4 layers:

```
┌─────────────────────────────────────────────┐
│         INFRASTRUCTURE LAYER                │
│   (Flask, SQLAlchemy, Config)               │
└──────────────┬──────────────────────────────┘
               │ implements
               ↓
┌─────────────────────────────────────────────┐
│          ADAPTERS LAYER                     │
│   (Controllers, Presenters, Repos)          │
└──────────────┬──────────────────────────────┘
               │ uses
               ↓
┌─────────────────────────────────────────────┐
│         BUSINESS LAYER                      │
│   (Use Cases, DTOs, Interfaces)             │
└──────────────┬──────────────────────────────┘
               │ uses
               ↓
┌─────────────────────────────────────────────┐
│          DOMAIN LAYER                       │
│   (Entities, Value Objects, Rules)          │
└─────────────────────────────────────────────┘
```

### 📁 Project Structure

```
PY-CameraShop/
├── 📄 app.py                    # 🚀 Main entry point (RUN THIS)
├── 📄 database-setup.sql        # 📊 Database schema definition
├── 📄 requirements.txt          # 📦 Python dependencies
├── 📄 README.md                 # 📖 Project documentation (this file)
├── 📄 LICENSE                   # ⚖️ License information
├── 🔒 .env                      # 🔐 Environment variables (not in git)
├── 📋 .env.example              # 📋 Example environment config
├── 🚫 .gitignore                # 🚫 Git ignore rules
│
├── 📁 app/                      # 🏛️ Main application (Clean Architecture)
│   ├── domain/                  # Layer 1: Domain entities & business rules
│   │   ├── entities/           # Pure business entities (User, Product, Order, Cart)
│   │   ├── exceptions/         # Domain exceptions
│   │   ├── value_objects/      # Immutable concepts (Email, Money, Address)
│   │   └── enums.py            # Domain enumerations
│   ├── business/                # Layer 2: Use cases & business logic
│   │   ├── dto/                # Data Transfer Objects (Input/Output)
│   │   ├── ports/              # Repository interfaces (contracts)
│   │   └── use_cases/          # Use case implementations
│   ├── adapters/                # Layer 3: Controllers, repositories, presenters
│   │   ├── api/                # REST API controllers
│   │   ├── views/              # Frontend view routes
│   │   ├── presenters/         # Output formatters
│   │   └── repositories/       # Repository implementations
│   └── infrastructure/          # Layer 4: Frameworks & tools
│       ├── config/             # Configuration & database setup
│       ├── database/           # SQLAlchemy models
│       └── factory.py          # Application factory (DI container)
│
├── 📁 scripts/                  # 🔧 Utility scripts
│   ├── init_db.py              # Initialize database
│   ├── seed_data.py            # Seed sample data
│   ├── simple_seed.py          # Simple data seeding
│   └── setup_database.py       # Database setup utility
│
├── 📁 static/                   # 🎨 Frontend assets
│   ├── css/                    # Stylesheets (common.css, admin-layout.css, etc.)
│   ├── js/                     # JavaScript files (home.js, cart.js, etc.)
│   └── images/                 # Image assets
│
├── 📁 template/                 # 🖼️ Jinja2 HTML templates
│   ├── base.html               # User base template
│   ├── admin_base.html         # Admin base template
│   ├── index.html              # Homepage
│   ├── auth/                   # Authentication pages (login, register)
│   ├── products/               # Product pages (list, detail, search)
│   ├── cart/                   # Cart pages (view, checkout)
│   ├── orders/                 # Order pages (my_orders, detail)
│   ├── errors/                 # Error pages (404, 500)
│   └── admin/                  # Admin pages (dashboard, products, orders, etc.)
│       ├── dashboard/          # Admin dashboard
│       ├── products/           # Product management
│       ├── orders/             # Order management
│       ├── brands/             # Brand management
│       └── categories/         # Category management
│
├── 📁 tests/                    # 🧪 Unit & integration tests (481 tests)
│   ├── business/               # Business logic tests
│   └── integration/            # Integration tests
│
├── 📁 migrations/               # 🔄 Database migrations (Alembic)
│   └── versions/               # Migration version files
│
├── 📁 instance/                 # 💾 Instance-specific files
│   └── camerashop.db           # SQLite database (production)
│
├── 📁 materials/                # 📚 Documentation & references
│   ├── mega-prompt.md          # Clean Architecture guidelines
│   ├── QUICK_START.md          # Quick start guide
│   ├── CLEANUP_SUMMARY.md      # Project cleanup summary
│   └── ...                     # Other documentation
│
└── 📁 venv/                     # 🐍 Python virtual environment (not in git)
```

#### 🏛️ Clean Architecture Layers Explained

**Layer 1: Domain (`app/domain/`)**
- Pure business entities with **zero dependencies** on frameworks
- Rich with behavior - business rules enforced here
- Self-validating entities
- Examples: `User`, `Product`, `Order`, `Cart` entities

**Layer 2: Business (`app/business/`)**
- Use case orchestration (application logic)
- Input/Output DTOs for data transfer
- Repository interfaces (ports) - business defines contracts
- Examples: `PlaceOrderUseCase`, `AddToCartUseCase`

**Layer 3: Adapters (`app/adapters/`)**
- REST API controllers handling HTTP requests
- Repository implementations (database adapters)
- Presenters for output formatting
- View routes for HTML rendering

**Layer 4: Infrastructure (`app/infrastructure/`)**
- Flask application factory
- Database configuration (SQLAlchemy)
- ORM models (mapped to domain entities)
- Dependency injection wiring

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** (3.10+ supported)
- **pip** package manager
- **Virtual environment** (recommended)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/PY-CameraShop.git
cd PY-CameraShop
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**

Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

Linux/MacOS:
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Initialize database**
```bash
# Run database setup
python scripts/init_db.py

# Seed sample data (30 products, test users)
python scripts/seed_data.py
```

6. **Run the application**
```bash
python app.py
```

Application will be available at: **http://localhost:5000**

### 🧪 Test Accounts

After seeding, use these accounts:

**Admin Account:**
- Username: `admin`
- Password: `123456`
- Access: http://localhost:5000/admin

**Customer Account:**
- Username: `user`
- Password: `123456`
- Access: http://localhost:5000/products

---

## 📦 Tech Stack

### Backend
- **Flask 3.0.0** - Web framework
- **SQLAlchemy 2.0** - ORM with type hints
- **Flask-Migrate** - Database migrations (Alembic)
- **Python 3.11+** - Core language

### Database
- **SQLite** - Development database
- **SQLAlchemy Core** - Database abstraction layer

### Authentication & Security
- **Werkzeug** - Password hashing (pbkdf2:sha256)
- **Flask Sessions** - Secure session management

### Frontend
- **Jinja2** - Server-side templating
- **JavaScript (Vanilla)** - Progressive enhancement
- **Bootstrap 5** - CSS framework (responsive design)

---

## 📚 API Documentation

### 🔐 Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | ❌ |
| POST | `/api/auth/login` | Login user | ❌ |
| POST | `/api/auth/logout` | Logout user | ✅ |
| GET | `/api/auth/me` | Get current user info | ✅ |

**Example: Register**
```json
POST /api/auth/register
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe",
  "phone_number": "+84901234567",
  "address": "123 Main St, Hanoi"
}
```

### 📦 Product Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/products` | List products (with filters) | ❌ |
| GET | `/api/products/<id>` | Get product detail | ❌ |

**Query Parameters for /api/products:**
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 12)
- `category_id` - Filter by category
- `brand_id` - Filter by brand
- `search_query` - Text search
- `min_price`, `max_price` - Price range
- `sort_by` - Sort option (newest, oldest, price_asc, price_desc)

### 🗂️ Catalog Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/catalog/categories` | List all categories | ❌ |
| GET | `/api/catalog/brands` | List all brands | ❌ |

### 🛒 Cart Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/cart` | View cart | ✅ |
| POST | `/api/cart/add` | Add item to cart | ✅ |
| PUT | `/api/cart/update/<item_id>` | Update cart item quantity | ✅ |
| DELETE | `/api/cart/remove/<item_id>` | Remove item from cart | ✅ |

**Example: Add to Cart**
```json
POST /api/cart/add
{
  "product_id": 5,
  "quantity": 2
}
```

### 📋 Order Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/orders` | Place new order | ✅ |
| GET | `/api/orders/my-orders` | Get user's orders | ✅ |
| GET | `/api/orders/<id>` | Get order detail | ✅ |
| POST | `/api/orders/<id>/cancel` | Cancel order | ✅ |

**Example: Place Order**
```json
POST /api/orders
{
  "shipping_address": "456 Nguyen Trai, Hanoi",
  "phone_number": "+84901234567",
  "payment_method": "COD",
  "notes": "Deliver morning only"
}
```

### 👨‍💼 Admin Endpoints (Requires ADMIN role)

#### Product Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/products` | Create product |
| PUT | `/api/admin/products/<id>` | Update product |
| DELETE | `/api/admin/products/<id>` | Delete product |

#### Category Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/categories` | Create category |
| PUT | `/api/admin/categories/<id>` | Update category |
| DELETE | `/api/admin/categories/<id>` | Delete category |

#### Brand Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/brands` | Create brand |
| PUT | `/api/admin/brands/<id>` | Update brand |
| DELETE | `/api/admin/brands/<id>` | Delete brand |

#### Order Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/orders` | List all orders (with filters) |
| PUT | `/api/admin/orders/<id>/status` | Update order status |
| POST | `/api/cart/add` | Add item to cart | ✅ |
| PUT | `/api/cart/update/<item_id>` | Update cart item | ✅ |
| DELETE | `/api/cart/remove/<item_id>` | Remove cart item | ✅ |

### 📋 Order Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/orders` | Place order | ✅ |
| GET | `/api/orders/my` | Get my orders | ✅ |
| GET | `/api/orders/<id>` | Get order detail | ✅ |
| POST | `/api/orders/<id>/cancel` | Cancel order | ✅ |

### 🎨 Frontend Routes

| Route | Description | Auth Required |
|-------|-------------|---------------|
| `/` | Homepage | ❌ |
| `/products` | Product listing | ❌ |
| `/products/<id>` | Product detail | ❌ |
| `/cart` | Shopping cart | ✅ |
| `/login` | Login page | ❌ |
| `/register` | Register page | ❌ |
| `/orders` | My orders | ✅ |
| `/orders/<id>` | Order detail | ✅ |
| `/admin/dashboard` | Admin dashboard | 👨‍💼 |
| `/admin/products` | Manage products | 👨‍💼 |
| `/admin/orders` | Manage orders | 👨‍💼 |
| `/admin/categories` | Manage categories | 👨‍💼 |
| `/admin/brands` | Manage brands | 👨‍💼 |

---

## 🧩 Clean Architecture Layers

### 🎯 Layer 1: Domain (Core Business Logic)

**Location:** `app/domain/`

The innermost layer containing pure business logic with **zero dependencies**.

**Components:**
- `entities/` - Business entities (User, Product, Order, etc.)
- `value_objects/` - Immutable concepts (Money, Email, Phone)
- `enums.py` - Business enumerations (OrderStatus, UserRole, PaymentMethod)
- `exceptions.py` - Domain-specific exceptions

**Rules:**
- ❌ No imports from outer layers
- ❌ No framework dependencies
- ✅ Pure Python classes
- ✅ Business validation logic only

### 🎯 Layer 2: Business (Application Logic)

**Location:** `app/business/`

Contains use cases (application business rules) and defines interfaces.

**Components:**
- `use_cases/` - Application use cases (RegisterUserUseCase, PlaceOrderUseCase, etc.)
- `ports/` - Repository interfaces (abstract classes)
- `dto/` - Data Transfer Objects

**Rules:**
- ✅ Can import from Domain layer
- ❌ Cannot import from Adapters/Infrastructure
- ✅ Defines interfaces (ports) for outer layers
- ✅ Contains orchestration logic

**Use Cases Implemented (25+):**
- **Auth:** `login_user`, `register_user`, `get_user`
- **Products:** `list_products`, `get_product_detail`, `create_product`, `update_product`, `delete_product`
- **Cart:** `add_to_cart`, `update_cart_item`, `remove_cart_item`
- **Orders:** `place_order`, `get_my_orders`, `get_order_detail`, `cancel_order`, `list_orders`, `update_order_status`
- **Admin:** `get_dashboard_stats`, `create_brand`, `update_brand`, `delete_brand`, `create_category`, `update_category`, `delete_category`

### 🎯 Layer 3: Adapters (Interface Adapters)

**Location:** `app/adapters/`

Converts data between use cases and external systems.

**Components:**
- `api/` - HTTP controllers/routes (Flask blueprints)
- `views/` - Frontend view routes
- `repositories/` - Repository implementations (implements ports)
- `presenters/` - Output formatters

**Repositories Implemented (6):**
- `UserRepository` - User CRUD operations
- `ProductRepository` - Product queries with filters
- `CategoryRepository` - Category management
- `BrandRepository` - Brand management
- `CartRepository` - Shopping cart operations
- `OrderRepository` - Order management

**API Blueprints (5):**
- `auth_bp` - Authentication routes (4 endpoints)
- `product_bp` - Product routes (2 endpoints)
- `cart_bp` - Cart routes (4 endpoints)
- `order_bp` - Order routes (4 endpoints)
- `view_bp` - Frontend view routes (13 routes)

### 🎯 Layer 4: Infrastructure (Frameworks & Tools)

**Location:** `app/infrastructure/`

Contains all framework and external tool implementations.

**Components:**
- `database/` - SQLAlchemy models (User, Product, Order, etc.)
- `config/` - Application configuration
- `factory.py` - Application factory with dependency injection

**Models (7):**
- `UserModel` - User accounts
- `ProductModel` - Products with relationships
- `CategoryModel` - Product categories
- `BrandModel` - Product brands
- `CartItemModel` - Cart items
- `OrderModel` - Orders with status tracking
- `OrderItemModel` - Order line items

---

## 🧪 Testing

### Test Coverage: **481/481 Passing (100%)**

**Test Suite Breakdown:**
- **Business Logic Tests:** 431 tests (use case unit tests)
- **Repository Integration Tests:** 50 tests (database operations)

### Run All Tests
```bash
# All tests
pytest

# Business logic tests only (431 tests)
pytest tests/business/ -v

# Repository integration tests only (50 tests)
pytest tests/integration/ -k "repository" -v

# Specific test file
pytest tests/business/use_cases/test_place_order_use_case.py -v

# With coverage report
pytest --cov=app --cov-report=html
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Test Structure
```
tests/
├── conftest.py              # Fixtures and test configuration
├── business/                # Business logic unit tests
│   └── use_cases/          # 431 use case tests
└── integration/            # Integration tests
    ├── test_user_repository.py     # 11 tests
    ├── test_product_repository.py  # 11 tests
    ├── test_cart_repository.py     # 14 tests
    └── test_order_repository.py    # 14 tests
```

### Test Examples

**Business Logic Test:**
```python
def test_place_order_success():
    """Test successful order placement"""
    use_case = PlaceOrderUseCase(
        order_repository=Mock(),
        cart_repository=Mock(),
        product_repository=Mock()
    )
    
    input_data = PlaceOrderInputData(
        user_id=1,
        shipping_address="123 Main St",
        phone_number="+84901234567",
        payment_method="COD"
    )
    
    output = use_case.execute(input_data)
    assert output.success == True
```

**Integration Test:**
```python
def test_save_and_retrieve_order(db_session, sample_order):
    """Test order persistence"""
    repository = OrderRepositoryAdapter(db_session)
    saved = repository.save(sample_order)
    retrieved = repository.find_by_id(saved.id)
    
    assert retrieved is not None
    assert retrieved.customer_id == sample_order.customer_id
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Database Migration Error**
```bash
# Reset migrations
flask db stamp head
flask db upgrade
```

**2. Import Errors**
```bash
# Verify Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

**3. Port Already in Use**
```bash
# Change port in run.py
app.run(host='0.0.0.0', port=8000, debug=True)
```

**4. SQLAlchemy Warning (MovedIn20Warning)**
```
# Non-critical deprecation warning - will be fixed in SQLAlchemy 2.0 migration
# Does not affect functionality
```

---

## 📖 Project Documentation

Comprehensive documentation available in `materials/` folder:

- [Clean Architecture Implementation Summary](materials/CLEAN_ARCHITECTURE_IMPLEMENTATION_SUMMARY.md) - Detailed architecture guide
- [Quick Start Guide](materials/QUICK_START.md) - Fast setup instructions
- [UI Design Guide](materials/UI_DESIGN_GUIDE.md) - Frontend styling guide
- [Architecture Overview](materials/architecture.md) - High-level design
- [Mega Prompt](materials/mega-prompt.md) - Complete architectural blueprint

---

## 🚀 Deployment

### Development
```bash
python run.py  # Runs on http://localhost:5000
```

### Production

**1. Environment Variables**
```bash
FLASK_ENV=production
SECRET_KEY=your-super-secure-random-key-here
DATABASE_URL=postgresql://user:pass@host/db  # For PostgreSQL
```

**2. Use Production Server (Gunicorn)**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

**3. Deploy to Cloud**

**Heroku:**
```bash
git push heroku main
heroku run flask db upgrade
heroku run python scripts/seed_data.py
```

**Docker:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### Architectural Rules
1. **Domain Layer** - Pure business logic, zero framework dependencies
2. **Business Layer** - Define use cases and interfaces (ports)
3. **Adapters Layer** - Implement interfaces, convert data formats
4. **Infrastructure Layer** - Framework-specific code only

### Development Workflow
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Implement feature following Clean Architecture
5. Ensure all tests pass (`pytest`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open Pull Request

### Code Standards
- Type hints for all function signatures
- Docstrings for public methods
- Maintain 100% test coverage for business logic
- Follow PEP 8 style guide

---

## 📊 Project Statistics

- **Lines of Code:** ~15,000+ (excluding tests)
- **Test Coverage:** 481 tests passing (100%)
- **API Endpoints:** 18+ (REST API)
- **Use Cases:** 25+ (business operations)
- **Domain Entities:** 6 (User, Product, Order, Cart, Brand, Category)
- **Value Objects:** 3 (Money, Email, PhoneNumber)
- **Repository Interfaces:** 6 (with full implementations)
- **Development Time:** 60-70 hours (estimated)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**PY-CameraShop Team**

Built with ❤️ following Clean Architecture principles.

---

## 🙏 Acknowledgments

- **Uncle Bob (Robert C. Martin)** - Clean Architecture pattern
- **Flask Team** - Excellent web framework
- **SQLAlchemy Team** - Powerful ORM
- All contributors and testers

---

**⭐ If you find this project helpful, please star it on GitHub!**

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 👨‍💻 Author

**PY-CameraShop Development Team**

---

## 🙏 Acknowledgments

- Clean Architecture by Robert C. Martin
- Flask Framework Documentation
- SQLAlchemy ORM Documentation

---
