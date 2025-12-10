// My Orders Page Logic

// DOM Elements
const loadingIndicator = document.getElementById('loadingIndicator');
const ordersContainer = document.getElementById('ordersContainer');
const emptyState = document.getElementById('emptyState');
const ordersList = document.getElementById('ordersList');
const alertContainer = document.getElementById('alertContainer');

// Stats elements
const totalOrdersEl = document.getElementById('totalOrders');
const processingOrdersEl = document.getElementById('processingOrders');
const completedOrdersEl = document.getElementById('completedOrders');
const cancelledOrdersEl = document.getElementById('cancelledOrders');

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    checkAuthAndLoadOrders();
    updateUserGreeting();
});

// Check authentication and load orders
function checkAuthAndLoadOrders() {
    const userId = sessionStorage.getItem('userId');
    
    if (!userId) {
        window.location.href = '/login';
        return;
    }

    showCancelSuccessIfNeeded();

    loadMyOrders(userId);
}

// Load user's orders
async function loadMyOrders(userId) {
    showLoading();

    try {
        // API: GET /api/orders/my-orders - returns {success, orders: [...], total_orders}
        const response = await fetch('/api/orders/my-orders', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        console.log('Orders response:', data); // Debug log

        if (data.success && data.orders && data.orders.length > 0) {
            displayOrders(data.orders);
            updateStats(data.orders);
        } else {
            console.log('No orders or error:', data.error); // Debug log
            updateStats([]); // Update stats với empty array
            showEmptyState();
        }

    } catch (error) {
        console.error('Error loading orders:', error);
        showAlert('Không thể tải đơn hàng. Vui lòng thử lại!', 'error');
        updateStats([]); // Update stats với empty array
        showEmptyState();
    } finally {
        hideLoading();
    }
}

// Custom confirm modal (reuse style across site)
let confirmModalOverlay = null;

function ensureConfirmModal() {
    if (confirmModalOverlay) return confirmModalOverlay;
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `
        <div class="modal" role="dialog" aria-modal="true">
            <h3 class="modal-title">Xác nhận hủy đơn</h3>
            <p class="modal-message" id="confirmMessage">Bạn có chắc chắn?</p>
            <div class="modal-actions">
                <button type="button" class="btn-secondary" id="confirmCancelBtn">Để sau</button>
                <button type="button" class="btn-danger" id="confirmOkBtn">Hủy đơn</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
    confirmModalOverlay = overlay;
    return overlay;
}

function showConfirmModal(message) {
    return new Promise(resolve => {
        const overlay = ensureConfirmModal();
        const msgEl = overlay.querySelector('#confirmMessage');
        const okBtn = overlay.querySelector('#confirmOkBtn');
        const cancelBtn = overlay.querySelector('#confirmCancelBtn');

        msgEl.textContent = message || 'Bạn có chắc chắn?';
        overlay.classList.add('show');

        const cleanup = (result) => {
            overlay.classList.remove('show');
            document.removeEventListener('keydown', onEsc);
            resolve(result);
        };

        const onEsc = (e) => {
            if (e.key === 'Escape') {
                cleanup(false);
            }
        };

        okBtn.onclick = () => cleanup(true);
        cancelBtn.onclick = () => cleanup(false);
        document.addEventListener('keydown', onEsc);
    });
}

// Display orders list
function displayOrders(orders) {
    ordersList.innerHTML = '';

    orders.forEach(order => {
        const orderCard = createOrderCard(order);
        ordersList.appendChild(orderCard);
    });

    ordersContainer.classList.remove('hidden');
    emptyState.classList.add('hidden');
}

// Create order card element
function createOrderCard(order) {
    const card = document.createElement('div');
    card.className = 'order-card';

    // API returns: {order_id, total_amount, status, payment_method, shipping_address, phone_number, notes, created_at, item_count}
    // Status mapping: CHO_XAC_NHAN, DANG_GIAO, HOAN_THANH, DA_HUY
    const statusMap = {
        'CHO_XAC_NHAN': {label: 'Chờ xác nhận', color: 'pending'},
        'DANG_GIAO': {label: 'Đang giao hàng', color: 'shipping'},
        'HOAN_THANH': {label: 'Hoàn thành', color: 'completed'},
        'DA_HUY': {label: 'Đã hủy', color: 'cancelled'}
    };
    
    const statusInfo = statusMap[order.status] || {label: order.status, color: 'pending'};
    const canCancelOrder = order.status === 'CHO_XAC_NHAN';
    
    const cancelButtonHTML = canCancelOrder ? `
        <button class="btn-cancel" data-action="cancel-order" data-order-id="${order.order_id}">
            Hủy đơn hàng
        </button>
    ` : '';

    card.innerHTML = `
        <div class="order-header">
            <div class="order-id">Đơn hàng #${order.order_id}</div>
            <div class="order-status status-${statusInfo.color}">${statusInfo.label}</div>
        </div>

        <div class="order-body">
            <div class="order-info-item">
                <span class="info-label">Số điện thoại</span>
                <span class="info-value">${order.phone_number}</span>
            </div>

            <div class="order-info-item">
                <span class="info-label">Địa chỉ giao hàng</span>
                <span class="info-value">${order.shipping_address}</span>
            </div>

            <div class="order-info-item">
                <span class="info-label">Ngày đặt</span>
                <span class="info-value">${new Date(order.created_at).toLocaleString('vi-VN')}</span>
            </div>
            
            <div class="order-info-item">
                <span class="info-label">Thanh toán</span>
                <span class="info-value">${order.payment_method}</span>
            </div>
        </div>

        <div class="order-items-summary">
            📦 ${order.item_count || 0} sản phẩm
        </div>

        <div class="order-footer">
            <div class="order-total">${formatCurrency(order.total_amount)}</div>
            <div class="order-actions">
                ${cancelButtonHTML}
                <button class="btn-view" onclick="goToDetailPage(${order.order_id})">Xem chi tiết</button>
            </div>
        </div>
    `;

    if (canCancelOrder) {
        const cancelBtn = card.querySelector('[data-action="cancel-order"]');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                cancelOrder(order.order_id);
            });
        }
    }

    return card;
}

function goToDetailPage(orderId) {
    window.location.href = `/orders/${orderId}`;
}

// Update statistics
function updateStats(orders) {
    const stats = {
        total: orders.length,
        processing: 0,
        completed: 0,
        cancelled: 0
    };

    orders.forEach(order => {
        const status = order.status;
        
        if (status === 'CHO_XAC_NHAN' || status === 'DANG_GIAO') {
            stats.processing++;
        } else if (status === 'HOAN_THANH') {
            stats.completed++;
        } else if (status === 'DA_HUY') {
            stats.cancelled++;
        }
    });

    totalOrdersEl.textContent = stats.total;
    processingOrdersEl.textContent = stats.processing;
    completedOrdersEl.textContent = stats.completed;
    cancelledOrdersEl.textContent = stats.cancelled;
}

// Show empty state
function showEmptyState() {
    ordersContainer.classList.add('hidden');
    emptyState.classList.remove('hidden');
}

// Loading state
function showLoading() {
    loadingIndicator.classList.remove('hidden');
    ordersContainer.classList.add('hidden');
    emptyState.classList.add('hidden');
}

function hideLoading() {
    loadingIndicator.classList.add('hidden');
}

// Alert functions
function showAlert(message, type = 'success') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} show`;
    alert.textContent = message;
    
    alertContainer.appendChild(alert);
    
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 300);
    }, 3000);
}

// Hiển thị thông báo hủy thành công khi quay lại từ trang chi tiết
function showCancelSuccessIfNeeded() {
    const params = new URLSearchParams(window.location.search);
    if (params.get('cancelSuccess') === '1') {
        showAlert('Đơn hàng đã được hủy thành công!', 'success');
        // Xóa query để tránh hiện lại khi refresh
        params.delete('cancelSuccess');
        const newUrl = `${window.location.pathname}${params.toString() ? '?' + params.toString() : ''}`;
        window.history.replaceState({}, '', newUrl);
    }
}

// Cancel order function
async function cancelOrder(orderId) {
    const confirmed = await showConfirmModal(`Bạn có chắc chắn muốn hủy đơn hàng #${orderId}?`);
    if (!confirmed) return;

    try {
        const response = await fetch(`/api/orders/${orderId}/cancel`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Cancel error response:', errorText);
            showAlert('Không thể hủy đơn hàng. Vui lòng thử lại!', 'error');
            return;
        }

        const data = await response.json();
        console.log('Cancel response:', data);

        if (data.success) {
            showAlert('Đơn hàng đã được hủy thành công!', 'success');
            // Reload orders after successful cancellation
            setTimeout(() => {
                loadMyOrders();
            }, 1500);
        } else {
            showAlert('Không thể hủy đơn hàng: ' + (data.error || data.message || 'Lỗi không xác định'), 'error');
        }
    } catch (error) {
        console.error('Error cancelling order:', error);
        showAlert('Lỗi khi hủy đơn hàng. Vui lòng thử lại!', 'error');
    }
}

// Update user greeting
function updateUserGreeting() {
    const username = sessionStorage.getItem('username');
    const userNameEl = document.getElementById('userName');
    if (userNameEl) {
        userNameEl.textContent = username || 'User';
    }
}

// Logout function
function logout() {
    sessionStorage.clear();
    window.location.href = '/login';
}
