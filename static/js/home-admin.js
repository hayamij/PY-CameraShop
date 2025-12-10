// Home Admin Page JavaScript

// Check admin role on page load
document.addEventListener('DOMContentLoaded', function() {
    checkAdminAccess();
    updateAdminGreeting();
    loadDashboardData();
});

// Check if user has admin role
function checkAdminAccess() {
    const role = sessionStorage.getItem('role');
    const userId = sessionStorage.getItem('userId');
    const username = sessionStorage.getItem('username');

    console.log('=== DEBUG INFO ===');
    console.log('UserId:', userId);
    console.log('Username:', username);
    console.log('Role từ sessionStorage:', role);
    console.log('Role type:', typeof role);
    console.log('==================');

    if (!userId) {
        console.log('❌ Chưa đăng nhập - Chuyển hướng đến trang login');
        window.location.href = '/login';
        return;
    }

    // Normalize role: convert to uppercase and trim
    const normalizedRole = role ? String(role).trim().toUpperCase() : '';
    console.log('Role đã normalize:', normalizedRole);

    // Check if role contains 'ADMIN' (English or Vietnamese)
    const isAdmin = normalizedRole.includes('ADMIN') || 
                    normalizedRole.includes('QUẢN TRỊ') ||
                    normalizedRole.includes('ADMIN_ROLE') ||
                    normalizedRole.includes('ROLE_ADMIN');
    console.log('Is Admin?', isAdmin);

    if (!isAdmin) {
        console.log('❌ Không phải Admin');
        showAccessDenied();
        return;
    }

    console.log('✅ Admin đã được xác nhận - Tải dashboard');
}

// Show access denied message
function showAccessDenied() {
    const container = document.querySelector('.admin-container');
    if (container) {
        container.innerHTML = `
            <div style="text-align: center; padding: 100px 20px;">
                <div style="font-size: 4em; margin-bottom: 20px;">❌</div>
                <h1>Truy cập bị từ chối</h1>
                <p style="font-size: 1.2em; color: #666; margin: 20px 0;">Bạn không có quyền truy cập trang admin.</p>
                <p style="color: #999; margin-bottom: 30px;">Chỉ người dùng có vai trò Admin mới có thể vào trang này.</p>
                <button class="btn-primary" onclick="logout()" style="padding: 12px 30px; font-size: 1em;">
                    Đăng xuất & Quay lại
                </button>
            </div>
        `;
    }
}

// Update admin greeting
function updateAdminGreeting() {
    const username = sessionStorage.getItem('username') || 'Admin';
    const adminNameEl = document.getElementById('adminName');
    if (adminNameEl) {
        adminNameEl.textContent = username;
    }
}

// Load dashboard data
async function loadDashboardData() {
    try {
        // Load statistics
        await loadStatistics();
        
        // Load products
        await loadProducts();
        
        // Load orders
        await loadOrders();
        
        // Load users
        await loadUsers();

        // Load cameras
        await loadcameras();
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Load statistics
async function loadStatistics() {
    try {
        // Load products count
        const productsRes = await fetch('/api/products');
        const productsData = await productsRes.json();
        const totalProducts = productsData.total_products || (productsData.products ? productsData.products.length : 0);
        document.getElementById('totalProducts').textContent = totalProducts;
        
        // Load orders and calculate revenue
        const ordersRes = await fetch('/api/admin/orders');
        const ordersData = await ordersRes.json();
        if (ordersData.success && ordersData.orders) {
            const orders = ordersData.orders;
            const pendingOrders = orders.filter(o => o.status === 'PENDING' || o.order_status === 'PENDING').length;
            document.getElementById('pendingOrders').textContent = pendingOrders;
            
            // Calculate total revenue from completed orders
            const totalRevenue = orders
                .filter(o => o.status === 'COMPLETED' || o.order_status === 'COMPLETED')
                .reduce((sum, o) => sum + (parseFloat(o.total_amount || o.totalAmount || 0)), 0);
            document.getElementById('totalRevenue').textContent = formatCurrency(totalRevenue);
        } else {
            document.getElementById('pendingOrders').textContent = '0';
            document.getElementById('totalRevenue').textContent = '0 ₫';
        }
        
        // Placeholder for users (would need a user list API)
        document.getElementById('totalUsers').textContent = '-';
    } catch (error) {
        console.error('Error loading statistics:', error);
        document.getElementById('totalRevenue').textContent = 'N/A';
        document.getElementById('totalProducts').textContent = 'N/A';
        document.getElementById('totalUsers').textContent = 'N/A';
        document.getElementById('pendingOrders').textContent = 'N/A';
    }
}

// Load products list
async function loadProducts() {
    try {
        const response = await fetch('/api/products');
        const data = await response.json();

        const tbody = document.getElementById('productsTableBody');
        
        if (!data.products || data.products.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 40px; color: #999;">
                        Không có sản phẩm
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = data.products.slice(0, 10).map(product => `
            <tr>
                <td>${product.id || 'N/A'}</td>
                <td><strong>${product.tenSanPham || 'N/A'}</strong></td>
                <td>${product.category || 'N/A'}</td>
                <td>${formatCurrency(product.giaBan || 0)}</td>
                <td>${product.soLuong || 0}</td>
                <td>
                    <button class="btn-secondary" onclick="editProduct(${product.id})" style="padding: 6px 12px; font-size: 0.85em; margin-right: 4px;">Sửa</button>
                    <button class="btn-secondary" onclick="deleteProduct(${product.id})" style="padding: 6px 12px; font-size: 0.85em; background: #fee2e2; color: #991b1b; border-color: #991b1b;">Xóa</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading products:', error);
        document.getElementById('productsTableBody').innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; color: #e74c3c;">Lỗi tải sản phẩm</td>
            </tr>
        `;
    }
}

// Load orders list
async function loadOrders() {
    try {
        // Use ListAllOrders use case endpoint
        const response = await fetch('/api/admin/orders');
        const data = await response.json();

        const tbody = document.getElementById('ordersTableBody');
        
        if (!data.success || !data.orders || data.orders.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 40px; color: #999;">
                        Không có đơn hàng
                    </td>
                </tr>
            `;
            return;
        }

        const orders = data.orders || [];

        tbody.innerHTML = orders.slice(0, 10).map(order => `
            <tr>
                <td><strong>#${order.orderId || 'N/A'}</strong></td>
                <td>${order.customerName || 'N/A'}</td>
                <td>
                    <span class="status-badge status-${(order.statusColor || 'GRAY').toLowerCase()}">
                        ${order.orderStatus || 'N/A'}
                    </span>
                </td>
                <td>${order.formattedTotalAmount || formatCurrency(order.totalAmount || 0)}</td>
                <td>${order.formattedOrderDate || formatDate(order.orderDate || '')}</td>
                <td>
                    <button class="btn-secondary" onclick="viewOrder(${order.orderId})" style="padding: 6px 12px; font-size: 0.85em;">Xem</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading orders:', error);
        document.getElementById('ordersTableBody').innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; color: #e74c3c;">Lỗi tải đơn hàng</td>
            </tr>
        `;
    }
}

// Load users list
async function loadUsers() {
    try {
        // Users management API not implemented yet
        return;
        const data = await response.json();

        const tbody = document.getElementById('usersTableBody');
        
        if (!data.users || data.users.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 40px; color: #999;">
                        Không có người dùng
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = data.users.slice(0, 10).map(user => `
            <tr>
                <td>${user.id || 'N/A'}</td>
                <td>${user.email || 'N/A'}</td>
                <td>${user.username || 'N/A'}</td>
                <td><span class="status-badge">${user.role || 'USER'}</span></td>
                <td><span class="status-badge status-confirmed">Hoạt động</span></td>
                <td>
                    <button class="btn-secondary" onclick="editUser(${user.id})" style="padding: 6px 12px; font-size: 0.85em;">Sửa</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading users:', error);
        document.getElementById('usersTableBody').innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; color: #e74c3c;">Lỗi tải người dùng</td>
            </tr>
        `;
    }
}

// Helper functions
function formatCurrency(value) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(value);
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN');
}

function getStatusClass(status) {
    if (!status) return 'pending';
    const lower = status.toLowerCase();
    if (lower.includes('chờ') || lower.includes('pending')) return 'pending';
    if (lower.includes('xác nhận') || lower.includes('confirmed')) return 'confirmed';
    if (lower.includes('giao') || lower.includes('delivered')) return 'delivered';
    if (lower.includes('hủy') || lower.includes('cancelled')) return 'cancelled';
    return 'pending';
}

// Action functions
function goToProductManagement() {
    alert('Chuyển hướng đến trang quản lý sản phẩm');
    // window.location.href = 'product-management.html';
}

function editProduct(productId) {
    alert(`Chỉnh sửa sản phẩm #${productId}`);
    // window.location.href = `product-edit.html?id=${productId}`;
}

function deleteProduct(productId) {
    if (confirm(`Bạn có chắc chắn muốn xóa sản phẩm #${productId}?`)) {
        alert(`Sản phẩm #${productId} đã được xóa`);
    }
}

function viewOrder(orderId) {
    if (!orderId) return;
    window.location.href = `order-detail.html?orderId=${orderId}&from=admin`;
}

function editUser(userId) {
    alert(`Chỉnh sửa người dùng #${userId}`);
    // window.location.href = `user-edit.html?id=${userId}`;
}

// Logout function
function logout() {
    sessionStorage.clear();
    localStorage.removeItem('userId');
    localStorage.removeItem('email');
    localStorage.removeItem('username');
    window.location.href = '/login';
}

// Load cameras
async function loadcameras() {
    try {
        // ✅ Dùng API đang có: /api/cameras
        // Cameras entity removed - camera shop uses products
        return;

        if (!response.ok) {
            throw new Error(`HTTP status ${response.status}`);
        }

        // ✅ Backend trả về MẢNG camera, không phải { cameras: [...] }
        const data = await response.json();

        const tbody = document.getElementById('cameraTableBody');

        // Nếu không phải mảng hoặc rỗng
        if (!Array.isArray(data) || data.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; color: #999; padding: 20px;">
                        Không có dữ liệu máy ảnh
                    </td>
                </tr>`;
            return;
        }

        // ✅ Dùng nhiều tên field khác nhau cho chắc: tenXe / tenSanPham / name,...
        tbody.innerHTML = data.slice(0, 10).map(bike => {
            const id = bike.id ?? bike.maSanPham ?? 'N/A';
            const ten =
                bike.tenXe ||
                bike.tenSanPham ||
                bike.name ||
                'N/A';
            const hang =
                bike.hangXe ||
                bike.brand ||
                'N/A';
            const dong =
                bike.dongXe ||
                bike.model ||
                'N/A';
            const dungTich =
                bike.dungTich ||
                bike.displacement ||
                'N/A';
            const giaRaw =
                bike.gia ||
                bike.price ||
                bike.giaBan ||
                0;

            return `
                <tr>
                    <td>${id}</td>
                    <td>${ten}</td>
                    <td>${hang}</td>
                    <td>${dong}</td>
                    <td>${dungTich}</td>
                    <td>${formatCurrency(giaRaw)}</td>
                </tr>
            `;
        }).join('');

    } catch (error) {
        console.error("Error loading cameras:", error);
        const tbody = document.getElementById('cameraTableBody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; color: #e74c3c; padding: 20px;">
                        Lỗi tải dữ liệu máy ảnh
                    </td>
                </tr>`;
        }
    }
}

