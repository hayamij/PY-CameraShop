# 🎉 PHASE 2 COMPLETE - Domain Layer & Repository Interfaces

## ✅ Achievements

### 1. Value Objects (Immutable Domain Concepts)

#### 💰 Money Value Object
- **Location**: `app/domain/value_objects/money.py`
- **Features**:
  - Supports VND and USD currencies
  - Immutable (cannot be modified after creation)
  - Rich arithmetic operations (add, subtract, multiply)
  - Currency validation and mismatch prevention
  - Formatted display (e.g., "1,000,000 ₫")
- **Business Rules**:
  - Amount cannot be negative
  - Can only operate on same currency
  - Prevents currency mismatch errors

```python
# Example usage
price = Money(Decimal('500000'), 'VND')
quantity = Decimal('2')
total = price.multiply(quantity)  # Money(1000000, 'VND')
```

#### 📧 Email Value Object
- **Location**: `app/domain/value_objects/email.py`
- **Features**:
  - Email format validation with regex
  - Automatic lowercase conversion
  - Domain extraction
  - Local part extraction
- **Business Rules**:
  - Must match valid email pattern
  - Automatically normalized (lowercase, trimmed)

```python
# Example usage
email = Email("user@example.com")
print(email.domain)  # "example.com"
```

#### 📱 PhoneNumber Value Object
- **Location**: `app/domain/value_objects/phone_number.py`
- **Features**:
  - Vietnamese phone number validation (10 digits, starts with 0)
  - Automatic formatting (0xxx-xxx-xxx)
  - Cleans input (removes spaces, dashes)
- **Business Rules**:
  - Must be 10 digits starting with 0
  - Format: 0xxxxxxxxx

```python
# Example usage
phone = PhoneNumber("0912345678")
print(phone.formatted)  # "0912-345-678"
```

---

### 2. Domain Exceptions

#### 📍 Location: `app/domain/exceptions.py`

#### Exception Hierarchy:
```
DomainException (base)
├── User Exceptions
│   ├── InvalidCredentialsException
│   ├── UserAlreadyExistsException
│   ├── UserNotFoundException
│   ├── UnauthorizedAccessException
│   └── InsufficientPermissionsException
├── Product Exceptions
│   ├── InsufficientStockException
│   ├── ProductNotFoundException
│   └── InvalidProductPriceException
├── Order Exceptions
│   ├── InvalidOrderStatusTransitionException
│   ├── EmptyOrderException
│   ├── OrderNotFoundException
│   └── OrderAlreadyShippedException
└── Cart Exceptions
    ├── CartNotFoundException
    ├── EmptyCartException
    └── InvalidQuantityException
```

#### Key Features:
- All exceptions carry `error_code` for machine-readable errors
- Human-readable messages for logging
- Factory methods for common scenarios

```python
# Example usage
raise InsufficientStockException(product_id=5, requested=10, available=3)
# Message: "Product 5: requested 10, but only 3 available"
# Code: "INSUFFICIENT_STOCK"
```

---

### 3. Domain Enums

#### 📍 Location: `app/domain/enums.py`

#### UserRole Enum
```python
class UserRole(Enum):
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"
    GUEST = "GUEST"
```
- Methods: `is_admin()`, `is_customer()`, `is_guest()`

#### OrderStatus Enum
```python
class OrderStatus(Enum):
    PENDING = "CHO_XAC_NHAN"
    SHIPPING = "DANG_GIAO"
    COMPLETED = "HOAN_THANH"
    CANCELLED = "DA_HUY"
```
- Methods: 
  - `can_transition_to(new_status)` - Validates state transitions
  - `is_terminal()` - Checks if status is final
  - `is_modifiable()` - Checks if order can be changed

**Valid Transitions**:
- PENDING → SHIPPING or CANCELLED
- SHIPPING → COMPLETED
- No transitions from COMPLETED or CANCELLED

#### PaymentMethod Enum
```python
class PaymentMethod(Enum):
    CASH = "TIEN_MAT"
    BANK_TRANSFER = "CHUYEN_KHOAN"
    CREDIT_CARD = "THE_CREDIT"
```
- Method: `requires_confirmation()` - Returns True for bank transfers

---

### 4. Domain Entities (Rich Models)

#### 👤 User Entity
**Location**: `app/domain/entities/user.py`

**Properties**:
- id, username, email (Email VO), password_hash
- full_name, phone_number (PhoneNumber VO), address
- role (UserRole enum), is_active, created_at

**Business Methods**:
```python
user.update_profile(full_name, phone_number, address)
user.change_password(new_hash)
user.deactivate() / user.activate()
user.promote_to_admin() / user.demote_to_customer()
user.ensure_admin()  # Throws exception if not admin
user.ensure_active()  # Throws exception if inactive
```

**Creation**:
```python
# New user
user = User(
    username="john_doe",
    email=Email("john@example.com"),
    password_hash=hashed_password,
    full_name="John Doe",
    role=UserRole.CUSTOMER
)

# Reconstruct from DB
user = User.reconstruct(user_id=1, username="john", ...)
```

---

#### 📦 Product Entity
**Location**: `app/domain/entities/product.py`

**Properties**:
- id, name, description, price (Money VO)
- stock_quantity, category_id, brand_id
- image_url, is_visible, created_at

**Business Methods**:
```python
product.update_details(name, description, price, ...)
product.update_price(new_price)
product.add_stock(quantity)
product.reduce_stock(quantity)  # Validates sufficient stock
product.restore_stock(quantity)  # When order cancelled
product.hide() / product.show()
product.is_in_stock()
product.has_sufficient_stock(required_quantity)
product.is_available_for_purchase()
product.calculate_total_price(quantity)
```

**Business Rules**:
- Price must be positive (enforced by Money VO)
- Stock cannot be negative
- Throws `InsufficientStockException` if reducing more than available
- Visible products with stock > 0 are available for purchase

---

#### 🛒 Cart Entity (Aggregate Root)
**Location**: `app/domain/entities/cart.py`

**Contains**: CartItem value objects

**Properties**:
- id, customer_id, items (Dict[product_id → CartItem])
- created_at, updated_at

**Business Methods**:
```python
cart.add_item(product_id, quantity)  # Adds or increases quantity
cart.remove_item(product_id)
cart.update_item_quantity(product_id, new_quantity)
cart.clear()
cart.is_empty()
cart.get_item_count()  # Number of distinct products
cart.get_total_quantity()  # Total quantity of all items
cart.has_item(product_id)
cart.ensure_not_empty()  # For checkout validation
```

**CartItem Value Object**:
```python
class CartItem:
    - product_id, quantity
    Methods:
    - update_quantity(new_quantity)
    - increase_quantity(amount)
    - decrease_quantity(amount)
```

---

#### 📋 Order Entity (Aggregate Root)
**Location**: `app/domain/entities/order.py`

**Contains**: OrderItem value objects

**Properties**:
- id, customer_id, items (List[OrderItem])
- payment_method, shipping_address
- status (OrderStatus enum), total_amount (Money VO)
- created_at, updated_at

**Business Methods**:
```python
order.ship()      # PENDING → SHIPPING
order.complete()  # SHIPPING → COMPLETED
order.cancel()    # PENDING → CANCELLED
order.is_pending() / is_shipping() / is_completed() / is_cancelled()
order.can_be_cancelled()
order.can_be_modified()
order.get_item_count()
order.get_total_quantity()
order.belongs_to_customer(customer_id)
```

**OrderItem Value Object**:
```python
class OrderItem:
    - product_id, product_name, quantity, unit_price (Money VO)
    Methods:
    - calculate_subtotal()  # Returns Money
```

**Business Rules**:
- Order must have at least one item
- Total is calculated from items (immutable after creation)
- Status transitions are strictly enforced
- Only PENDING orders can be cancelled
- Shipped orders cannot be modified

---

#### 🏷️ Category Entity
**Location**: `app/domain/entities/category.py`

**Properties**:
- id, name, description, is_active, created_at

**Business Methods**:
```python
category.update_details(name, description)
category.deactivate() / category.activate()
```

---

#### 🏢 Brand Entity
**Location**: `app/domain/entities/brand.py`

**Properties**:
- id, name, description, logo_url, is_active, created_at

**Business Methods**:
```python
brand.update_details(name, description, logo_url)
brand.deactivate() / brand.activate()
```

---

### 5. Repository Interfaces (Ports)

#### 📍 Location: `app/business/ports/`

All repository interfaces are **abstract base classes (ABC)** defining contracts. Infrastructure layer will implement them.

#### IUserRepository
```python
- save(user) → User
- find_by_id(user_id) → Optional[User]
- find_by_username(username) → Optional[User]
- find_by_email(email) → Optional[User]
- find_all(skip, limit) → List[User]
- find_by_role(role, skip, limit) → List[User]
- delete(user_id) → bool
- exists_by_username(username) → bool
- exists_by_email(email) → bool
- count() → int
```

#### IProductRepository
```python
- save(product) → Product
- find_by_id(product_id) → Optional[Product]
- find_all(skip, limit, visible_only) → List[Product]
- find_by_category(category_id, skip, limit) → List[Product]
- find_by_brand(brand_id, skip, limit) → List[Product]
- search_by_name(query, skip, limit) → List[Product]
- find_by_ids(product_ids) → List[Product]
- delete(product_id) → bool
- count(visible_only) → int
- count_by_category(category_id) → int
- count_by_brand(brand_id) → int
```

#### IOrderRepository
```python
- save(order) → Order
- find_by_id(order_id) → Optional[Order]
- find_by_customer_id(customer_id, skip, limit) → List[Order]
- find_by_status(status, skip, limit) → List[Order]
- find_all(skip, limit) → List[Order]
- find_by_date_range(start_date, end_date, skip, limit) → List[Order]
- delete(order_id) → bool
- count() → int
- count_by_status(status) → int
- count_by_customer(customer_id) → int
```

#### ICartRepository
```python
- save(cart) → Cart
- find_by_id(cart_id) → Optional[Cart]
- find_by_customer_id(customer_id) → Optional[Cart]
- delete(cart_id) → bool
- clear_cart(customer_id) → bool
```

#### ICategoryRepository
```python
- save(category) → Category
- find_by_id(category_id) → Optional[Category]
- find_by_name(name) → Optional[Category]
- find_all(active_only) → List[Category]
- delete(category_id) → bool
- exists_by_name(name) → bool
- count(active_only) → int
```

#### IBrandRepository
```python
- save(brand) → Brand
- find_by_id(brand_id) → Optional[Brand]
- find_by_name(name) → Optional[Brand]
- find_all(active_only) → List[Brand]
- delete(brand_id) → bool
- exists_by_name(name) → bool
- count(active_only) → int
```

---

## 🏗️ Clean Architecture Compliance

### ✅ Dependency Rule Respected

```
Infrastructure ──→ Adapters ──→ Business ──→ Domain
     (NO)           (NO)        (Ports)     (Pure!)
```

**Domain Layer**:
- ✅ ZERO framework imports
- ✅ ZERO database annotations
- ✅ Pure Python code only
- ✅ Rich with business logic
- ✅ Self-validating entities

**Business Layer (Ports)**:
- ✅ Defines interfaces (contracts)
- ✅ Does NOT implement them
- ✅ Depends only on Domain layer
- ✅ Framework-agnostic

**Infrastructure Layer** (Next Phase):
- Will implement repository interfaces
- Will use SQLAlchemy models
- Will handle database persistence

---

## 📊 Statistics

- **Value Objects**: 3 (Money, Email, PhoneNumber)
- **Domain Entities**: 6 (User, Product, Order, Cart, Category, Brand)
- **Domain Exceptions**: 17 custom exceptions
- **Enums**: 3 (UserRole, OrderStatus, PaymentMethod)
- **Repository Interfaces**: 6 ports
- **Total Lines of Code**: ~2,600 lines
- **Framework Dependencies in Domain**: 0 ❌ (Perfect!)

---

## 🎯 Next Steps: Phase 3

### Authentication & Authorization (Week 2)

1. **Flask-Login Integration** (Infrastructure)
   - User loader function
   - Session management
   - Remember me functionality

2. **Authentication Use Cases** (Business Layer)
   - RegisterUserUseCase
   - LoginUserUseCase
   - LogoutUserUseCase
   - ResetPasswordUseCase

3. **Password Hashing**
   - Flask-Bcrypt integration
   - Hash passwords on registration
   - Verify passwords on login

4. **Authorization Decorators**
   - @login_required
   - @admin_required
   - @customer_required

5. **Templates**
   - Login page
   - Register page
   - Password reset flow

---

## 🎓 Key Learnings

### 1. Domain-Driven Design Principles
- **Entities** have identity and lifecycle
- **Value Objects** are immutable and defined by values
- **Aggregates** enforce consistency boundaries (Order → OrderItems)
- **Business logic** lives in entities, NOT services

### 2. Separation of Concerns
- Domain entities know NOTHING about databases
- Repository interfaces live in Business layer
- Implementations will be in Infrastructure layer
- This allows easy testing and framework swapping

### 3. Type Safety
- Used Python type hints throughout
- Optional types for nullable fields
- Enums for restricted values
- Money VO prevents currency mismatch bugs

### 4. Business Rule Enforcement
- Validation in entity constructors
- State transitions via methods (not direct property access)
- Exceptions for business rule violations
- Immutable value objects prevent invalid states

---

## 📝 Code Quality Highlights

✅ **No Anemic Models**: Every entity has rich behavior  
✅ **Fail Fast**: Validation happens at creation time  
✅ **Encapsulation**: Private fields with controlled access  
✅ **Immutability**: Value objects cannot change after creation  
✅ **Type Safety**: Comprehensive type hints  
✅ **Documentation**: Every class and method documented  
✅ **Testability**: Pure functions, no hidden dependencies  
✅ **SOLID Principles**: Single responsibility, open/closed, dependency inversion  

---

**Phase 2 Status**: ✅ **COMPLETE**  
**Git Commit**: `52bf2f5` - "feat: Phase 2 - Domain layer and repository interfaces"  
**Ready for Phase 3**: 🎯 Authentication & Authorization

---

*"The heart of software is its domain logic." - Eric Evans*
