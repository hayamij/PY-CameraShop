# PY-CameraShop

**E-commerce Website for Camera & Accessories**
Built with Flask following Clean Architecture principles

---

## Project Overview

**PY-CameraShop** is a camera and accessories e-commerce website built with the Flask framework, strictly following **Clean Architecture** to ensure:

- **Maintainability** - Code is easy to maintain and extend
- **Testability** - Business logic is completely independent (481 tests passing)
- **Scalability** - Highly scalable architecture
- **Independence** - No dependency on specific frameworks or databases

### Project Status: PRODUCTION READY

All phases completed:
- Phase 1: Database Setup
- Phase 2: Infrastructure Layer
- Phase 3: Repository Adapters
- Phase 4: HTTP Controllers (34+ API endpoints)
- Phase 5: Frontend Interface (Full-stack UI)
- Phase 6: Testing (1105/1105 tests passing - 100% coverage)
- Phase 7: Admin Dashboard with Analytics

---

## Key Features

### For Guests (No login required)
- Browse homepage with featured products
- Advanced search and filter (category, brand, price range)
- View detailed product information with specs
- Browse by categories and brands
- Real-time price display in VND

### For Customers
- Register / Login with secure password hashing
- Shopping cart management (add, update, remove items)
- Place orders with multiple payment methods (COD, Bank Transfer, Credit Card)
- View complete order history with status tracking
- Cancel pending orders
- Profile management (update info, addresses)
- Email validation and phone number verification

### For Admins
- Rich admin dashboard with Plotly charts & real-time analytics
- Revenue tracking with daily/weekly/monthly trends
- Complete product management (Create, Read, Update, Delete)
- Order management with status updates & tracking
- User account management (Create, Update, Delete, Role changes)
- Category & Brand management
- Advanced search and filtering for all entities
- Low stock alerts & inventory management
- Sales reports & revenue analytics

---

## Architecture

The project follows **Clean Architecture** with 4 layers:

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

### Clean Architecture Layers Explained

**Layer 1: Domain (`app/domain/`)**
Pure business entities with zero dependencies on frameworks. Rich with behavior — business rules are enforced here. Self-validating entities. Examples: `User`, `Product`, `Order`, `Cart` entities.

**Layer 2: Business (`app/business/`)**
Use case orchestration (application logic). Input/Output DTOs for data transfer. Repository interfaces (ports) — the business layer defines contracts. Examples: `PlaceOrderUseCase`, `AddToCartUseCase`.

**Layer 3: Adapters (`app/adapters/`)**
REST API controllers handling HTTP requests. Repository implementations (database adapters). Presenters for output formatting. View routes for HTML rendering.

**Layer 4: Infrastructure (`app/infrastructure/`)**
Flask application factory. Database configuration (SQLAlchemy). ORM models (mapped to domain entities). Dependency injection wiring.

---

## Getting Started

### Prerequisites

- Python 3.11+ (3.10+ supported)
- pip package manager
- Virtual environment (recommended)

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
python scripts/init_db.py
python scripts/seed_data.py
```

6. **Run the application**
```bash
python app.py
```

Application will be available at: **http://localhost:5000**

### Test Accounts

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

## Tech Stack

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

## API Documentation

### Authentication Endpoints (4 endpoints)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login user | No |
| POST | `/api/auth/logout` | Logout user | Yes |
| GET | `/api/auth/me` | Get current user info | Yes |

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

### Product Endpoints (2 endpoints)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/products` | List products (with filters) | No |
| GET | `/api/products/<id>` | Get product detail | No |

**Query Parameters for /api/products:**
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 12)
- `category_id` - Filter by category
- `brand_id` - Filter by brand
- `search_query` - Text search
- `min_price`, `max_price` - Price range
- `sort_by` - Sort option (newest, oldest, price_asc, price_desc)

### Catalog Endpoints (2 endpoints)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/catalog/categories` | List all categories | No |
| GET | `/api/catalog/brands` | List all brands | No |

### Cart Endpoints (4 endpoints)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/cart` | View cart | Yes |
| POST | `/api/cart/add` | Add item to cart | Yes |
| PUT | `/api/cart/items/<item_id>` | Update cart item quantity | Yes |
| DELETE | `/api/cart/items/<item_id>` | Remove item from cart | Yes |

**Example: Add to Cart**
```json
POST /api/cart/add
{
  "product_id": 5,
  "quantity": 2
}
```

### Order Endpoints (4 endpoints)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/orders` | Place new order | Yes |
| GET | `/api/orders/my-orders` | Get user's orders | Yes |
| GET | `/api/orders/<id>` | Get order detail | Yes |
| POST | `/api/orders/<id>/cancel` | Cancel order | Yes |

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

### Admin Endpoints (Requires ADMIN role) - 18 endpoints

#### User Management (6 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/users` | List all users (with filters & pagination) |
| GET | `/api/admin/users/search` | Search users by query |
| POST | `/api/admin/users` | Create new user |
| PUT | `/api/admin/users/<id>` | Update user |
| DELETE | `/api/admin/users/<id>` | Delete user (soft delete) |
| PUT | `/api/admin/users/<id>/role` | Change user role |

#### Product Management (3 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/products` | Create product |
| PUT | `/api/admin/products/<id>` | Update product |
| DELETE | `/api/admin/products/<id>` | Delete product |

#### Category Management (3 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/categories` | Create category |
| PUT | `/api/admin/categories/<id>` | Update category |
| DELETE | `/api/admin/categories/<id>` | Delete category |

#### Brand Management (3 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/brands` | Create brand |
| PUT | `/api/admin/brands/<id>` | Update brand |
| DELETE | `/api/admin/brands/<id>` | Delete brand |

#### Order Management (4 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/orders` | List all orders (with filters) |
| POST | `/api/admin/orders` | Create order (admin) |
| PUT | `/api/admin/orders/<id>/status` | Update order status |
| DELETE | `/api/admin/orders/<id>` | Delete order |

### Frontend View Routes (13 routes)

#### Public Routes
| Route | Description | Auth Required |
|-------|-------------|---------------|
| `/` | Homepage with featured products | No |
| `/products` | Product listing with filters | No |
| `/products/<id>` | Product detail page | No |
| `/login` | Login page | No |
| `/register` | Register page | No |

#### Customer Routes
| Route | Description | Auth Required |
|-------|-------------|---------------|
| `/cart` | Shopping cart | Yes |
| `/checkout` | Checkout page | Yes |
| `/orders` | My orders | Yes |
| `/orders/<id>` | Order detail | Yes |

#### Admin Routes
| Route | Description | Auth Required |
|-------|-------------|---------------|
| `/admin` | Admin dashboard with charts | ADMIN |
| `/admin/users` | User management | ADMIN |
| `/admin/products` | Product management | ADMIN |
| `/admin/orders` | Order management | ADMIN |
| `/admin/categories` | Category management | ADMIN |
| `/admin/brands` | Brand management | ADMIN |

---

## Testing

### Test Coverage: 481/481 Passing (100%)

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

### Test Examples

**Business Logic Test:**
```python
def test_place_order_success():
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
    repository = OrderRepositoryAdapter(db_session)
    saved = repository.save(sample_order)
    retrieved = repository.find_by_id(saved.id)
    assert retrieved is not None
    assert retrieved.customer_id == sample_order.customer_id
```

---

## Troubleshooting

### Common Issues

**1. Database Migration Error**
```bash
flask db stamp head
flask db upgrade
```

**2. Import Errors**
```bash
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

**3. Port Already in Use**
```bash
# Change port in run.py
app.run(host='0.0.0.0', port=8000, debug=True)
```

**4. SQLAlchemy Warning (MovedIn20Warning)**
Non-critical deprecation warning — does not affect functionality.

---

## Project Documentation

Comprehensive documentation available in the `materials/` folder:

- [Clean Architecture Implementation Summary](materials/CLEAN_ARCHITECTURE_IMPLEMENTATION_SUMMARY.md)
- [Quick Start Guide](materials/QUICK_START.md)
- [UI Design Guide](materials/UI_DESIGN_GUIDE.md)
- [Architecture Overview](materials/architecture.md)
- [Mega Prompt](materials/mega-prompt.md)

---

## Deployment

### Development
```bash
python run.py  # Runs on http://localhost:5000
```

### Production

**1. Environment Variables**
```bash
FLASK_ENV=production
SECRET_KEY=your-super-secure-random-key-here
DATABASE_URL=postgresql://user:pass@host/db
```

**2. Use Production Server (Gunicorn)**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

**3. Deploy to Cloud**

Heroku:
```bash
git push heroku main
heroku run flask db upgrade
heroku run python scripts/seed_data.py
```

Docker:
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

## Contributing

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

## Project Statistics

- **Lines of Code:** ~18,000+ (excluding tests and docs)
- **Test Coverage:** 481/481 tests passing (100% business logic coverage)
- **API Endpoints:** 34 REST API endpoints (Authentication: 4, Public APIs: 4, Customer APIs: 8, Admin APIs: 18)
- **Use Cases:** 33 business operations
- **Domain Entities:** 6 (User, Product, Order, Cart, Brand, Category)
- **Value Objects:** 3 (Money, Email, PhoneNumber)
- **Repository Interfaces:** 6 (with SQLAlchemy implementations)
- **View Routes:** 13 frontend pages
- **Database Tables:** 7 tables with relationships
- **Development Time:** 80+ hours

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author

**PY-CameraShop Team** — Built with Clean Architecture principles.

---

## Acknowledgments

- **Uncle Bob (Robert C. Martin)** - Clean Architecture pattern
- **Flask Team** - Excellent web framework
- **SQLAlchemy Team** - Powerful ORM
- All contributors and testers

---
