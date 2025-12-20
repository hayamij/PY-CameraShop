# 📦 Quick Start Guide

## Chạy dự án bằng Docker (Đơn giản nhất)

### Bước 1: Cài Docker Desktop
- Windows/Mac: https://www.docker.com/products/docker-desktop/
- Linux: `sudo apt install docker.io docker-compose`

### Bước 2: Chạy dự án
```bash
# Di chuyển vào thư mục dự án
cd PY-CameraShop

# Khởi động tất cả (SQL Server + Flask App)
docker-compose up -d

# Đợi 30-60 giây cho SQL Server khởi động
```

### Bước 3: Truy cập
- Website: http://localhost:5000
- Admin: admin@gmail.com / admin123
- User: user@gmail.com / user123

### Dừng dự án
```bash
docker-compose down
```

---

## Chi tiết đầy đủ
Xem file [HOW_TO_RUN.md](HOW_TO_RUN.md) để biết hướng dẫn chi tiết!
