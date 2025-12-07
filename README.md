# 📷 Flask Camera Shop

> **E-commerce Website for Camera & Accessories**  
> Built with Flask following Clean Architecture principles

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Project Overview

Flask Camera Shop là một website bán máy ảnh & phụ kiện được xây dựng với Flask framework, tuân theo **Clean Architecture** để đảm bảo:

- ✅ **Maintainability** - Dễ bảo trì và mở rộng
- ✅ **Testability** - Logic nghiệp vụ độc lập với framework
- ✅ **Scalability** - Có khả năng mở rộng
- ✅ **Independence** - Không phụ thuộc vào framework cụ thể

### 🌟 Key Features

#### For Guests:
- 🏠 Xem trang chủ với sản phẩm nổi bật
- 🔍 Tìm kiếm và lọc sản phẩm
- 📄 Xem chi tiết sản phẩm
- 📂 Duyệt theo danh mục và thương hiệu

#### For Customers:
- 🔐 Đăng ký / Đăng nhập
- 🛒 Quản lý giỏ hàng
- 💳 Đặt hàng và thanh toán
- 📦 Xem lịch sử đơn hàng
- 👤 Quản lý thông tin cá nhân

#### For Admins:
- 📊 **Dashboard với Data Visualization** (Plotly, Chart.js)
- 📦 Quản lý sản phẩm (CRUD)
- 🛍️ Quản lý đơn hàng
- 👥 Quản lý tài khoản
- 📈 Báo cáo doanh thu & thống kê
- 📄 Export data (Excel, PDF, CSV)

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
├── app/
│   ├── domain/              # Layer 1: Pure business logic
│   │   ├── entities/        # Business entities
│   │   ├── exceptions/      # Domain exceptions
│   │   └── value_objects/   # Immutable concepts
│   ├── business/            # Layer 2: Application logic
│   │   ├── dto/             # Data Transfer Objects
│   │   ├── ports/           # Repository interfaces
│   │   └── use_cases/       # Use case implementations
│   ├── adapters/            # Layer 3: Interface adapters
│   │   ├── api/             # Flask routes/controllers
│   │   ├── presenters/      # Output formatters
│   │   └── repositories/    # Repository implementations
│   └── infrastructure/      # Layer 4: Frameworks & tools
│       ├── config/          # Configuration
│       └── database/        # Database models & setup
├── static/                  # Static files (CSS, JS, images)
├── template/                # HTML templates
├── migrations/              # Database migrations
├── tests/                   # Unit & integration tests
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── run.py                   # Application entry point
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip
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

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Setup environment variables**
```bash
# Copy example env file and edit with your configuration
cp .env.example .env
```

6. **Run the application**
```bash
python run.py
```

Application will be available at: `http://localhost:5000`

---

## 📦 Tech Stack

### Core Framework
- **Flask 3.0.0** - Web framework
- **Flask-SQLAlchemy** - ORM
- **Flask-Migrate** - Database migrations
- **Flask-Login** - User authentication
- **Flask-WTF** - Forms validation

### Data Visualization
- **Plotly** - Interactive charts
- **Pandas** - Data manipulation
- **Matplotlib** - Static plots
- **Seaborn** - Statistical visualization

### Database
- **SQLAlchemy** - ORM
- **PyMySQL** - MySQL connector
- **SQLite** - Development database

### Security
- **Flask-Bcrypt** - Password hashing
- **Flask-Limiter** - Rate limiting

### Document Processing
- **openpyxl** - Excel export
- **reportlab** - PDF generation

---

## 🙏 Acknowledgments

- Clean Architecture principles by Robert C. Martin
- Flask documentation and community
- All open-source libraries used in this project

---

**Built with ❤️ using Flask and Clean Architecture**
