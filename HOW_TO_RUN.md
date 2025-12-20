# 🎁 GỬI DỰ ÁN CHO BẠN BÈ - HƯỚNG DẪN CHI TIẾT

## 📦 Chuẩn bị gửi dự án

### Bước 1: Nén dự án thành file ZIP

1. **Mở PowerShell tại thư mục dự án**:
   ```powershell
   cd D:\VisualStudioCode\CodebaseWinter2025\CUOIKI\PY-CameraShop
   ```

2. **Tạo file ZIP** (chọn 1 trong 2 cách):
   
   **Cách 1 - Dùng PowerShell**:
   ```powershell
   Compress-Archive -Path * -DestinationPath ..\CameraShop.zip -Force
   ```
   
   **Cách 2 - Dùng Windows Explorer**:
   - Click chuột phải vào thư mục `PY-CameraShop`
   - Chọn `Send to` → `Compressed (zipped) folder`

### Bước 2: Gửi qua Discord

1. **Kéo thả file** `CameraShop.zip` vào chat Discord
2. **Hoặc** click vào biểu tượng `+` → chọn file ZIP

⚠️ **LƯU Ý**: File ZIP có thể lớn (50-100MB), Discord free có giới hạn 25MB/file. Nếu vượt quá:

#### Giải pháp thay thế:

**A. Dùng Google Drive / OneDrive**:
1. Upload file ZIP lên Google Drive hoặc OneDrive
2. Tạo link chia sẻ (Share link)
3. Gửi link cho bạn qua Discord

**B. Dùng GitHub** (Khuyên dùng - Chuyên nghiệp):
```powershell
# Tại thư mục dự án
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/camerashop.git
git push -u origin main
```
Sau đó gửi link GitHub repo cho bạn.

---

## 🚀 HƯỚNG DẪN CHO BẠN BÈ - CHẠY DỰ ÁN

### Yêu cầu hệ thống

- Windows 10/11 hoặc macOS hoặc Linux
- Docker Desktop (miễn phí)
- 4GB RAM trở lên
- 5GB dung lượng trống

---

### Bước 1: Cài đặt Docker Desktop

#### Windows:
1. Tải Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Chạy file cài đặt `Docker Desktop Installer.exe`
3. Khởi động lại máy sau khi cài đặt
4. Mở Docker Desktop và đợi nó chạy (icon Docker xuất hiện ở system tray)

#### macOS:
1. Tải Docker Desktop cho Mac (Intel hoặc Apple Silicon)
2. Kéo Docker.app vào thư mục Applications
3. Mở Docker Desktop từ Applications

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```
Đăng xuất và đăng nhập lại sau khi chạy lệnh trên.

---

### Bước 2: Giải nén và chuẩn bị dự án

1. **Giải nén file ZIP**:
   - Windows: Click chuột phải → `Extract All`
   - macOS: Double click file ZIP
   - Linux: `unzip CameraShop.zip`

2. **Mở PowerShell/Terminal tại thư mục dự án**:
   
   **Windows**:
   ```powershell
   cd C:\Users\YourName\Downloads\PY-CameraShop
   ```
   
   **macOS/Linux**:
   ```bash
   cd ~/Downloads/PY-CameraShop
   ```

---

### Bước 3: Chạy dự án bằng Docker

#### Cách 1: Chạy đơn giản (Khuyên dùng)

```bash
docker-compose up -d
```

Lệnh này sẽ:
- ✅ Tải SQL Server image (lần đầu ~700MB, lần sau không cần tải lại)
- ✅ Build ứng dụng Flask
- ✅ Khởi tạo database
- ✅ Chạy website tại http://localhost:5000

**Đợi 30-60 giây** để hệ thống khởi động lần đầu tiên.

#### Cách 2: Xem logs trong quá trình chạy

```bash
docker-compose up
```
(Không có `-d`, bạn sẽ thấy logs trực tiếp)

---

### Bước 4: Truy cập website

1. Mở trình duyệt web
2. Truy cập: **http://localhost:5000**

#### Tài khoản mặc định:

**Admin**:
- Email: `admin@gmail.com`
- Password: `admin123`

**User thường**:
- Email: `user@gmail.com`
- Password: `user123`

---

### Bước 5: Tắt dự án

```bash
# Dừng các container
docker-compose down

# Dừng và XÓA database (reset toàn bộ)
docker-compose down -v
```

---

## 🛠️ Các lệnh hữu ích

### Xem logs
```bash
# Xem logs của tất cả services
docker-compose logs

# Xem logs của web service
docker-compose logs web

# Xem logs real-time
docker-compose logs -f
```

### Khởi động lại
```bash
# Rebuild và khởi động lại
docker-compose up -d --build

# Khởi động lại 1 service
docker-compose restart web
```

### Kiểm tra trạng thái
```bash
# Xem các container đang chạy
docker-compose ps

# Xem resource usage
docker stats
```

### Reset hoàn toàn
```bash
# Xóa tất cả và bắt đầu lại từ đầu
docker-compose down -v
docker-compose up -d --build
```

---

## ❓ Xử lý lỗi thường gặp

### Lỗi 1: "Port 5000 is already in use"
```bash
# Windows: Tìm process đang dùng port 5000
netstat -ano | findstr :5000

# Dừng process (thay PID bằng số tìm được)
taskkill /PID <PID> /F

# Hoặc đổi port trong docker-compose.yml:
# ports: "8080:5000"
```

### Lỗi 2: "Docker daemon is not running"
- Mở Docker Desktop
- Đợi icon Docker xuất hiện ở system tray
- Thử lại lệnh

### Lỗi 3: Website không mở được
```bash
# Kiểm tra container có chạy không
docker-compose ps

# Xem logs để tìm lỗi
docker-compose logs web

# Khởi động lại
docker-compose restart
```

### Lỗi 4: "Cannot connect to database"
```bash
# SQL Server cần thời gian khởi động (30-60s)
# Đợi thêm 1 phút rồi thử lại

# Hoặc khởi động lại database
docker-compose restart sqlserver
docker-compose restart web
```

---

## 📝 Tùy chỉnh (Nâng cao)

### Đổi mật khẩu SQL Server

Sửa file `docker-compose.yml`:
```yaml
environment:
  - SA_PASSWORD=YourNewPassword123!
```

### Đổi port website

Sửa file `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Website sẽ chạy ở http://localhost:8080
```

---

## 🎯 Checklist để gửi cho bạn

📋 **Gửi kèm cho bạn bè**:
- ✅ File ZIP dự án
- ✅ File `HOW_TO_RUN.md` này
- ✅ Link tải Docker Desktop: https://www.docker.com/products/docker-desktop/

📝 **Tin nhắn mẫu gửi Discord**:
```
Ê, t gửi dự án Camera Shop nè! 🎥📸

File ZIP: [đính kèm hoặc link Google Drive]

Hướng dẫn chạy:
1. Cài Docker Desktop (link: https://www.docker.com/products/docker-desktop/)
2. Giải nén file ZIP
3. Mở PowerShell/Terminal tại thư mục dự án
4. Chạy lệnh: docker-compose up -d
5. Đợi 1-2 phút rồi vào http://localhost:5000

Có file HOW_TO_RUN.md chi tiết bên trong nha!
Có gì không chạy được thì inbox t! 🚀
```

---

## 🎓 Giải thích cho người không biết code

**Docker là gì?**
- Như một "máy ảo mini" chứa sẵn mọi thứ cần thiết
- Bạn không cần cài Python, SQL Server, hay các thứ phức tạp
- Chỉ cần cài Docker 1 lần, sau đó mọi dự án đều chạy được

**Docker Compose là gì?**
- Công cụ giúp chạy nhiều container cùng lúc
- File `docker-compose.yml` định nghĩa cách chạy (như công thức nấu ăn)
- 1 lệnh duy nhất: `docker-compose up -d` là mọi thứ tự động!

**Ưu điểm:**
- ✅ Không cần cài Python, SQL Server, các package
- ✅ Chạy được trên Windows, Mac, Linux
- ✅ "Works on my machine" = "Works on your machine"
- ✅ Xóa sạch chỉ cần xóa container, không ảnh hưởng máy tính

---

## 📞 Hỗ trợ

Nếu bạn bè gặp vấn đề:
1. Kiểm tra Docker Desktop có đang chạy không
2. Xem logs: `docker-compose logs`
3. Reset: `docker-compose down -v && docker-compose up -d`
4. Inbox cho bạn (người gửi dự án) 😊

---

**Chúc bạn bè chạy dự án thành công! 🎉**
