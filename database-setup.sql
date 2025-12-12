-- ================================================================================
-- PY-CAMERASHOP DATABASE SETUP SCRIPT (SQL Server Version)
-- Clean Architecture Implementation - Infrastructure Layer
-- Database: localhost:1433
-- Username: fuongtuan
-- Password: toilabanhmochi
-- ================================================================================

-- Create database if not exists with UTF-8 collation
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'CameraShopDB')
BEGIN
    CREATE DATABASE CameraShopDB
    COLLATE Vietnamese_CI_AS;
END
GO

USE CameraShopDB;
GO

-- Drop existing tables if they exist (in correct order due to foreign keys)
IF OBJECT_ID('order_items', 'U') IS NOT NULL DROP TABLE order_items;
IF OBJECT_ID('orders', 'U') IS NOT NULL DROP TABLE orders;
IF OBJECT_ID('cart_items', 'U') IS NOT NULL DROP TABLE cart_items;
IF OBJECT_ID('carts', 'U') IS NOT NULL DROP TABLE carts;
IF OBJECT_ID('products', 'U') IS NOT NULL DROP TABLE products;
IF OBJECT_ID('brands', 'U') IS NOT NULL DROP TABLE brands;
IF OBJECT_ID('categories', 'U') IS NOT NULL DROP TABLE categories;
IF OBJECT_ID('users', 'U') IS NOT NULL DROP TABLE users;
IF OBJECT_ID('roles', 'U') IS NOT NULL DROP TABLE roles;
GO

-- ================================================================================
-- TABLE DEFINITIONS
-- ================================================================================

-- Roles Table
CREATE TABLE roles (
    role_id INT PRIMARY KEY,
    role_name NVARCHAR(50) UNIQUE NOT NULL,
    description NVARCHAR(255)
);
GO

-- Users Table
CREATE TABLE users (
    user_id INT PRIMARY KEY IDENTITY(1,1),
    username NVARCHAR(100) UNIQUE NOT NULL,
    email NVARCHAR(255) UNIQUE NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    full_name NVARCHAR(255) NOT NULL,
    phone_number NVARCHAR(20),
    address NVARCHAR(MAX),
    role_id INT NOT NULL DEFAULT 2,
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (role_id) REFERENCES roles(role_id),
    CHECK (role_id IN (1, 2))
);
GO

-- Create indexes for Users
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role_id);
GO

-- Categories Table
CREATE TABLE categories (
    category_id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) UNIQUE NOT NULL,
    description NVARCHAR(MAX),
    created_at DATETIME2 NOT NULL DEFAULT GETDATE()
);
GO

CREATE INDEX idx_categories_name ON categories(name);
GO

-- Brands Table
CREATE TABLE brands (
    brand_id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) UNIQUE NOT NULL,
    description NVARCHAR(MAX),
    logo_url NVARCHAR(500),
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE()
);
GO

CREATE INDEX idx_brands_name ON brands(name);
GO

-- Products Table
CREATE TABLE products (
    product_id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(255) UNIQUE NOT NULL,
    description NVARCHAR(MAX),
    price DECIMAL(18,2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    category_id INT,
    brand_id INT,
    image_url NVARCHAR(500),
    warranty_period INT,
    specifications NVARCHAR(MAX),
    is_visible BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (brand_id) REFERENCES brands(brand_id),
    CHECK (price > 0),
    CHECK (stock_quantity >= 0)
);
GO

CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_brand ON products(brand_id);
CREATE INDEX idx_products_visible ON products(is_visible);
CREATE INDEX idx_products_price ON products(price);
GO

-- Carts Table
CREATE TABLE carts (
    cart_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT UNIQUE NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
GO

CREATE UNIQUE INDEX idx_carts_user ON carts(user_id);
GO

-- CartItems Table
CREATE TABLE cart_items (
    cart_item_id INT PRIMARY KEY IDENTITY(1,1),
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    FOREIGN KEY (cart_id) REFERENCES carts(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    UNIQUE(cart_id, product_id),
    CHECK (quantity > 0)
);
GO

CREATE INDEX idx_cart_items_cart ON cart_items(cart_id);
CREATE INDEX idx_cart_items_product ON cart_items(product_id);
GO

-- Orders Table
CREATE TABLE orders (
    order_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    shipping_address NVARCHAR(MAX) NOT NULL,
    phone_number NVARCHAR(20) NOT NULL,
    order_status NVARCHAR(50) NOT NULL DEFAULT 'CHO_XAC_NHAN',
    payment_method NVARCHAR(50) NOT NULL,
    notes NVARCHAR(MAX),
    total_amount DECIMAL(18,2) NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    CHECK (order_status IN ('CHO_XAC_NHAN', 'DANG_GIAO', 'HOAN_THANH', 'DA_HUY')),
    CHECK (payment_method IN ('COD', 'BANK_TRANSFER', 'CREDIT_CARD')),
    CHECK (total_amount >= 0)
);
GO

CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_orders_created ON orders(created_at);
GO

-- OrderItems Table
CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY IDENTITY(1,1),
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    product_name NVARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(18,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    CHECK (quantity > 0),
    CHECK (unit_price > 0)
);
GO

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
GO

-- ================================================================================
-- SAMPLE DATA
-- ================================================================================

-- Insert Roles
INSERT INTO roles (role_id, role_name, description) VALUES 
(1, 'ADMIN', 'Administrator with full access'),
(2, 'CUSTOMER', 'Regular customer');
GO

-- Insert Sample Users (password: "123456" hashed with bcrypt)
SET IDENTITY_INSERT users ON;
INSERT INTO users (user_id, username, email, password_hash, full_name, phone_number, address, role_id) VALUES
(1, 'admin', 'admin@gmail.com', '$2b$12$kO8OVzfycp3mcxOvwyCWZOfRiQKHxQDvmIz/TqRlIIG1FmITKUKzG', N'Admin User', '0901234567', N'123 Admin St, Hanoi', 1),
(2, 'customer1', 'customer@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5aeOKc3BO6QI6', N'John Doe', '0902345678', N'456 Customer Ave, Hanoi', 2),
(3, 'customer2', 'customer2@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5aeOKc3BO6QI6', N'Jane Smith', '0903456789', N'789 User Blvd, Hanoi', 2);
SET IDENTITY_INSERT users OFF;
GO


-- Insert Categories
SET IDENTITY_INSERT categories ON;
INSERT INTO categories (category_id, name, description) VALUES
(1, N'Máy Ảnh DSLR', N'Máy ảnh số có ống ngắm quang học'),
(2, N'Máy Ảnh Mirrorless', N'Máy ảnh không gương lật hiện đại'),
(3, N'Ống Kính', N'Các loại ống kính cho máy ảnh'),
(4, N'Phụ Kiện', N'Phụ kiện nhiếp ảnh đa dạng'),
(5, N'Đèn Flash', N'Đèn flash chuyên nghiệp'),
(6, N'Tripod', N'Chân máy và giá đỡ'),
(7, N'Túi Đựng', N'Túi và ba lô máy ảnh'),
(8, N'Thẻ Nhớ', N'Thẻ nhớ tốc độ cao'),
(9, N'Pin & Sạc', N'Pin và bộ sạc'),
(10, N'Màn Hình', N'Màn hình máy tính và monitor');
SET IDENTITY_INSERT categories OFF;
GO

-- Insert Brands
SET IDENTITY_INSERT brands ON;
INSERT INTO brands (brand_id, name, description, logo_url) VALUES
(1, 'Canon', N'Hãng máy ảnh hàng đầu thế giới', 'https://images.seeklogo.com/logo-png/2/1/canon-logo-png_seeklogo-25733.png'),
(2, 'Nikon', N'Thương hiệu nhiếp ảnh uy tín', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Nikon_Logo.svg/1200px-Nikon_Logo.svg.png'),
(3, 'Sony', N'Công nghệ hình ảnh tiên tiến', 'https://images.seeklogo.com/logo-png/12/1/sony-logo-png_seeklogo-129420.png'),
(4, 'Fujifilm', N'Chất lượng ảnh tuyệt vời', 'https://images.seeklogo.com/logo-png/5/1/fujifilm-logo-png_seeklogo-58162.png'),
(5, 'Panasonic', N'Video và ảnh chuyên nghiệp', 'https://vinadesign.vn/uploads/images/2023/06/panasonic-logo-vinadesign-06-08-56-29.jpg'),
(6, 'Olympus', N'Máy ảnh nhỏ gọn mạnh mẽ', 'https://www.olympusamerica.com/sites/default/files/styles/card/public/2021-10/logo-blue-gold.jpg?h=d595f4a7&itok=4c_HECGe'),
(7, 'Tamron', N'Ống kính chất lượng cao', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTRVg5jZjwyih3LohKKPelj0Oqvo4Vwh4dOEA&s'),
(8, 'Sigma', N'Ống kính Art series', 'https://1000logos.net/wp-content/uploads/2023/07/Sigma-logo.jpg'),
(9, 'SanDisk', N'Thẻ nhớ tốc độ cao', 'https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhErTiwLbWi2jz4TiPKP6D3I4oeADItYtT4qITI_tKDNfOY6FiabKyk1b_uAWb3Etx3dsgi4fjCLpDyxN-GuMxkeEYRY2_iut0Ez9tyLfJLYiRT6BicJ_XuxfUJ9kd7D6SvpcE3gZbzaI2w/s1600/sandisk.jpg'),
(10, 'Manfrotto', N'Chân máy chuyên nghiệp', 'https://1000logos.net/wp-content/uploads/2020/04/Manfrotto-logo.jpg');
SET IDENTITY_INSERT brands OFF;
GO

-- Insert Sample Products (30+ items)
SET IDENTITY_INSERT products ON;
INSERT INTO products (product_id, name, description, price, stock_quantity, category_id, brand_id, image_url, warranty_period, specifications) VALUES
-- Canon DSLRs
(1, 'Canon EOS 90D', N'Máy ảnh DSLR 32.5MP APS-C với khả năng quay 4K', 32990000, 15, 1, 1, 'https://mayanh24h.com/image/catalog/san-pham/may-anh-dslr/canon/canon-90d/canon-90d-1.jpg', 24, N'Cảm biến: APS-C 32.5MP, ISO: 100-25600, Video: 4K/30p'),
(2, 'Canon EOS 5D Mark IV', N'Full-frame DSLR 30.4MP chuyên nghiệp', 65990000, 8, 1, 1, 'https://www.camera2u.com.my/image/camera2u/image/cache/data/all_product_images/product-2465/26-1-500x500.jpg', 24, N'Cảm biến: Full-frame 30.4MP, ISO: 100-32000, Video: 4K/30p'),
(3, 'Canon EOS 850D', N'DSLR nhập môn 24.1MP với màn hình xoay', 21990000, 25, 1, 1, 'https://product.hstatic.net/1000234350/product/may-anh-canon-850d-600x600_f6c10734e20c4311bbbac0813d2aeec0_master.jpg', 24, N'Cảm biến: APS-C 24.1MP, ISO: 100-25600, Video: 4K/24p'),

-- Nikon DSLRs
(4, 'Nikon D850', N'Full-frame DSLR 45.7MP độ phân giải cao', 72990000, 6, 1, 2, 'https://tugia.vn/sites/default/files/styles/product_image_600x600/public/20171026111052_16504_0-600x600_0.jpg?itok=EDXI6hE-', 24, N'Cảm biến: Full-frame 45.7MP, ISO: 64-25600, Video: 4K/30p'),
(5, 'Nikon D7500', N'DX DSLR 20.9MP với khả năng quay 4K', 28990000, 18, 1, 2, 'https://photoking.vn/upload/images/M%C3%A1y%20%E1%BA%A3nh%20DSLR/Nikon/D7500%20Kit%2018-140mm/nikon-d7500-kit-18-140mm-photoking-2.jpg', 24, N'Cảm biến: APS-C 20.9MP, ISO: 100-51200, Video: 4K/30p'),
(6, 'Nikon D5600', N'DSLR nhập môn 24.2MP với màn hình cảm ứng', 18990000, 30, 1, 2, 'https://binhminhdigital.com/StoreData/Product/8863/May-anh-Nikon-D5600%20(1).jpg', 24, N'Cảm biến: APS-C 24.2MP, ISO: 100-25600, Video: 1080p/60p'),

-- Sony Mirrorless
(7, 'Sony A7 IV', N'Full-frame mirrorless 33MP đa năng', 62990000, 10, 2, 3, 'https://product.hstatic.net/1000234350/product/front_27079cc4c0504734adee6ebb71428230_master.jpg', 24, N'Cảm biến: Full-frame 33MP, ISO: 100-51200, Video: 4K/60p'),
(8, 'Sony A7R V', N'Mirrorless độ phân giải cao 61MP', 98990000, 4, 2, 3, 'https://cdn.vjshop.vn/may-anh/mirrorless/sony/sony-a7r-v/sony-a7r-v-500x500.jpg', 24, N'Cảm biến: Full-frame 61MP, ISO: 100-32000, Video: 8K/24p'),
(9, 'Sony A6400', N'APS-C mirrorless 24.2MP nhỏ gọn', 24990000, 20, 2, 3, 'https://www.sonyalpha.vn/uploads/Images/file_1589264750.jpg', 24, N'Cảm biến: APS-C 24.2MP, ISO: 100-32000, Video: 4K/30p'),
(10, 'Sony ZV-E10', N'Mirrorless cho vlog 24.2MP', 19990000, 15, 2, 3, 'https://cdn.vjshop.vn/may-anh/mirrorless/sony/sony-zv-e10/sony-zv-e10.jpg', 24, N'Cảm biến: APS-C 24.2MP, ISO: 100-32000, Video: 4K/30p'),

-- Fujifilm Mirrorless
(11, 'Fujifilm X-T5', N'Mirrorless 40.2MP với màu sắc đẹp', 48990000, 12, 2, 4, 'https://mayanh24h.com/upload/assets/2022/1115/ar/x-t5.jpg', 24, N'Cảm biến: APS-C 40.2MP, ISO: 125-12800, Video: 6.2K/30p'),
(12, 'Fujifilm X-S20', N'Mirrorless 26.1MP nhỏ gọn', 32990000, 18, 2, 4, 'https://mayanh24h.com/upload/assets/thumb/2023/0528/ar/fujifilm-x-s20-1.jpg', 24, N'Cảm biến: APS-C 26.1MP, ISO: 160-12800, Video: 6.2K/30p'),
(13, 'Fujifilm X-H2S', N'Mirrorless thể thao 26.1MP', 54990000, 8, 2, 4, 'https://cdn.vjshop.vn/may-anh/mirrorless/fujifilm/fujifilm-x-h2s/fujifilm-xh2s.jpg', 24, N'Cảm biến: APS-C 26.1MP, ISO: 160-51200, Video: 6.2K/60p'),

-- Lenses (Canon)
(14, 'Canon RF 24-70mm f/2.8L IS USM', N'Ống kính zoom chuẩn f/2.8', 52990000, 10, 3, 1, 'https://bizweb.dktcdn.net/100/369/815/products/rf2470600x600-d1b61b8d-4e36-47b9-8009-beaac6f55f3e.jpg?v=1641792077923', 12, N'Mount: RF, Khẩu độ: f/2.8, Lấy nét: USM, Chống rung: IS'),
(15, 'Canon RF 50mm f/1.8 STM', N'Ống kính fix giá tốt', 6990000, 40, 3, 1, 'https://mayanh24h.com/upload/assets/catalog/san-pham-2019/ong-kinh-moi/canon-rf/rf-50mm-f-1-8-stm/canon-rf-50mm-f-1-8-stm.jpeg', 12, N'Mount: RF, Khẩu độ: f/1.8, Lấy nét: STM'),
(16, 'Canon EF 70-200mm f/2.8L IS III', N'Telephoto zoom chuyên nghiệp', 48990000, 7, 3, 1, 'https://binhminhdigital.com/storedata/images/product/canon-ef-70200mm-f28l-is-iii.jpg', 12, N'Mount: EF, Khẩu độ: f/2.8, Lấy nét: USM, Chống rung: IS'),

-- Lenses (Nikon)
(17, 'Nikon Z 24-70mm f/2.8 S', N'Ống kính zoom chuẩn Z-mount', 54990000, 9, 3, 2, 'https://product.hstatic.net/1000234350/product/24-70f2.8z_1_afd956127eb64220acb83cc2877f0a04.jpg', 12, N'Mount: Z, Khẩu độ: f/2.8, Lấy nét: AF, Chống rung: VR'),
(18, 'Nikon Z 50mm f/1.8 S', N'Ống kính fix cao cấp', 15990000, 25, 3, 2, 'https://mayanh24h.com/upload/assets/catalog/san-pham/ong-kinh-may-anh/nikon/nikon-z-50-f-1-8-s/nikon-z-50-1-8-s.jpg', 12, N'Mount: Z, Khẩu độ: f/1.8, Lấy nét: AF'),

-- Lenses (Sony)
(19, 'Sony FE 24-70mm f/2.8 GM II', N'Ống kính zoom GM thế hệ 2', 58990000, 8, 3, 3, 'https://cdn.vjshop.vn/ong-kinh/mirrorless/sony/ong-kinh-sony-fe-24-70mm-f28-gm-ii/fe-24-70-mm-f28-gm-ii-00-1500x1500.jpg', 12, N'Mount: E, Khẩu độ: f/2.8, Lấy nét: AF, Series: G Master'),
(20, 'Sony FE 85mm f/1.4 GM', N'Ống kính chân dung G Master', 45990000, 6, 3, 3, 'https://product.hstatic.net/1000234350/product/131346228_0dc95c1904264b0db46eab03c7d9cd19_master.jpg', 12, N'Mount: E, Khẩu độ: f/1.4, Lấy nét: AF, Series: G Master'),

-- Third-party Lenses
(21, 'Tamron 28-75mm f/2.8 Di III VXD G2', N'Ống kính zoom E-mount giá tốt', 22990000, 15, 3, 7, 'https://product.hstatic.net/1000234350/product/tamron-28-75mm-2-8-di-iii-vxd-g2_1ad33431a08b4778a9dea90a2916fd8c_master.jpg', 12, N'Mount: E, Khẩu độ: f/2.8, Lấy nét: VXD, Chống rung: VC'),
(22, 'Sigma 35mm f/1.4 DG HSM Art', N'Ống kính fix Art series', 24990000, 12, 3, 8, 'https://zshop.vn/images/detailed/52/sigma_35mm_f_1_4_dg_hsm_1393492.jpg', 12, N'Mount: Universal, Khẩu độ: f/1.4, Lấy nét: HSM'),

-- Accessories
(23, 'Manfrotto MT055XPRO3', N'Chân máy nhôm chuyên nghiệp', 5990000, 20, 6, 10, 'https://product.hstatic.net/1000340975/product/3594_mt055xpro3_bf5065453e474cf79b91bfa3427d89aa_master.jpg', 12, N'Chiều cao: 170cm, Tải trọng: 9kg, Chất liệu: Nhôm'),
(24, 'SanDisk Extreme PRO 128GB', N'Thẻ nhớ CFexpress Type B', 7990000, 50, 8, 9, 'https://bizweb.dktcdn.net/100/329/122/products/cfexpress-extremepro-type-b-128gb-01.jpg?v=1620267644133', 12, N'Dung lượng: 128GB, Tốc độ đọc: 1700MB/s, Tốc độ ghi: 1200MB/s'),
(25, 'Canon Speedlite 600EX II-RT', N'Đèn flash chuyên nghiệp', 12990000, 10, 5, 1, 'https://mayanh24h.com/image/catalog/san-pham-2019/flash-led/canon/canon-600ex-rt-ii/600ex-rt-ii.jpg', 12, N'GN: 60, TTL: Có, Wireless: Radio/Optical'),
(26, 'Peak Design Everyday Backpack 20L', N'Ba lô máy ảnh đa năng', 4990000, 30, 7, NULL, 'https://product.hstatic.net/200000863343/product/balo_may_anh_peak_design_everyday_backpack_v2__20l__ver_2-basic_9d9f49478a57446a816222f2678ce153.jpg', 12, N'Dung tích: 20L, Chất liệu: Chống nước, Ngăn laptop: 15"'),
(27, 'Rode VideoMic Pro+', N'Microphone cho quay video', 6990000, 15, 4, NULL, 'https://bizweb.dktcdn.net/100/107/650/products/videomic-pro-4.jpg?v=1700539889467', 12, N'Loại: Shotgun, Nguồn: Pin/Phantom, Chống rung: Có'),

-- Additional Products
(28, 'DJI Ronin-SC', N'Gimbal cho mirrorless', 8990000, 12, 4, NULL, 'https://mayanh24h.com/upload/assets/catalog/san-pham/phu-kien-quay-phim/gimbal/ronin-s-2/ronin-sc/gimbal-chong-rung-dji-sc-5.jpg', 12, N'Tải trọng: 2kg, Pin: 11h, Điều khiển: App'),
(29, 'Godox V1 Flash', N'Đèn flash tròn TTL', 5990000, 18, 5, NULL, 'https://mayanh24h.com/upload/assets/catalog/san-pham/phu-kien-may-anh/den-flash-led/godox-v1/flash-godox-v1.jpg', 12, N'GN: 92, TTL: Có, Pin: Li-ion'),
(30, 'Lowepro ProTactic BP 450 AW II', N'Ba lô nhiếp ảnh chuyên nghiệp', 6490000, 15, 7, NULL, 'https://bizweb.dktcdn.net/thumb/1024x1024/100/507/659/products/ffbd0ee5-d627-496c-95b4-fe96c703452d.jpg?v=1759546191133', 12, N'Dung tích: 25L, Chống nước: Có, Ngăn laptop: 15"');
SET IDENTITY_INSERT products OFF;
GO

-- Insert Sample Cart for customer1
SET IDENTITY_INSERT carts ON;
INSERT INTO carts (cart_id, user_id) VALUES (1, 2);
SET IDENTITY_INSERT carts OFF;
GO

-- Insert Cart Items
SET IDENTITY_INSERT cart_items ON;
INSERT INTO cart_items (cart_item_id, cart_id, product_id, quantity) VALUES
(1, 1, 1, 1),  -- Canon EOS 90D
(2, 1, 15, 1), -- Canon RF 50mm f/1.8
(3, 1, 24, 2); -- SanDisk memory card
SET IDENTITY_INSERT cart_items OFF;
GO

-- Insert Sample Orders
SET IDENTITY_INSERT orders ON;
INSERT INTO orders (order_id, user_id, shipping_address, phone_number, order_status, payment_method, notes, total_amount) VALUES
(1, 2, N'456 Customer Ave, Hanoi', '0902345678', 'HOAN_THANH', 'COD', N'Giao giờ hành chính', 47970000),
(2, 2, N'456 Customer Ave, Hanoi', '0902345678', 'DANG_GIAO', 'BANK_TRANSFER', NULL, 65990000),
(3, 3, N'789 User Blvd, Hanoi', '0903456789', 'CHO_XAC_NHAN', 'COD', N'Gọi trước khi giao', 24990000);
SET IDENTITY_INSERT orders OFF;
GO

-- Insert Order Items for Order 1 (Completed)
SET IDENTITY_INSERT order_items ON;
INSERT INTO order_items (order_item_id, order_id, product_id, product_name, quantity, unit_price) VALUES
(1, 1, 1, 'Canon EOS 90D', 1, 32990000),
(2, 1, 15, 'Canon RF 50mm f/1.8 STM', 1, 6990000),
(3, 1, 24, 'SanDisk Extreme PRO 128GB', 1, 7990000);

-- Insert Order Items for Order 2 (Shipping)
INSERT INTO order_items (order_item_id, order_id, product_id, product_name, quantity, unit_price) VALUES
(4, 2, 2, 'Canon EOS 5D Mark IV', 1, 65990000);

-- Insert Order Items for Order 3 (Pending)
INSERT INTO order_items (order_item_id, order_id, product_id, product_name, quantity, unit_price) VALUES
(5, 3, 9, 'Sony A6400', 1, 24990000);
SET IDENTITY_INSERT order_items OFF;
GO

-- ================================================================================
-- VERIFICATION QUERIES
-- ================================================================================

-- Count records in each table
SELECT 'Roles' as TableName, COUNT(*) as RecordCount FROM roles
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
SELECT 'Order Items', COUNT(*) FROM order_items;
GO

PRINT 'Database setup completed successfully!';
PRINT 'Database: CameraShopDB';
PRINT 'Server: localhost:1433';
PRINT 'Username: fuongtuan';
PRINT 'Default admin user: admin@camerashop.com (password: 123456)';
PRINT 'Default customer user: customer@gmail.com (password: 123456)';
GO
