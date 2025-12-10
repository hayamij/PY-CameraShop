// Extract orderId from URL path: /orders/123
const pathParts = window.location.pathname.split('/');
const orderId = pathParts[pathParts.length - 1];

const params = new URLSearchParams(window.location.search);
const from = params.get('from') || 'user';

const userNameEl = document.getElementById('userName');
const backLink = document.getElementById('backLink');
const statusPill = document.getElementById('statusPill');
const orderIdHeading = document.getElementById('orderIdHeading');
const orderDateEl = document.getElementById('orderDate');
const receiverNameEl = document.getElementById('receiverName');
const phoneNumberEl = document.getElementById('phoneNumber');
const shippingAddressEl = document.getElementById('shippingAddress');
const totalAmountEl = document.getElementById('totalAmount');
const totalItemsEl = document.getElementById('totalItems');
const totalQuantityEl = document.getElementById('totalQuantity');
const orderNoteEl = document.getElementById('orderNote');
const orderNoteSection = document.getElementById('orderNoteSection');
const itemsBody = document.getElementById('itemsBody');
const errorBox = document.getElementById('errorBox');
const orderActionsSection = document.getElementById('orderActionsSection');
const cancelOrderBtn = document.getElementById('cancelOrderBtn');

const STATUS_COLORS = {
    "ORANGE": "#fef3c7",
    "BLUE": "#dbeafe",
    "PURPLE": "#e9d5ff",
    "GREEN": "#d1fae5",
    "RED": "#fee2e2",
    "GRAY": "#e5e7eb"
};

const STATUS_TEXT_COLORS = {
    "ORANGE": "#92400e",
    "BLUE": "#1e3a8a",
    "PURPLE": "#6b21a8",
    "GREEN": "#065f46",
    "RED": "#7f1d1d",
    "GRAY": "#374151"
};

document.addEventListener('DOMContentLoaded', () => {
    if (!orderId) {
        showError('Thiếu mã đơn hàng.');
        return;
    }
    setupNav();
    loadOrderDetail();
});

function setupNav() {
    const username = sessionStorage.getItem('username') || 'User';
    if (userNameEl) userNameEl.textContent = username;

    const userId = sessionStorage.getItem('userId');
    const role = (sessionStorage.getItem('role') || '').toUpperCase();
    const isAdmin = role.includes('ADMIN') || role.includes('QUẢN TRỊ');

    if (from === 'admin' || isAdmin) {
        backLink.href = '/admin/orders';
    } else {
        backLink.href = '/orders';
    }

    if (!userId) {
        window.location.href = '/login';
    }
}

async function loadOrderDetail() {
    clearError();
    setLoading(true);
    try {
        const res = await fetch(`/api/orders/${orderId}`);
        const data = await res.json();

        if (!data.success) {
            showError(data.error || data.message || 'Không tải được chi tiết đơn hàng');
            return;
        }

        renderOrder(data.order);
    } catch (err) {
        console.error(err);
        showError('Lỗi khi tải chi tiết đơn hàng');
    } finally {
        setLoading(false);
    }
}

function renderOrder(order) {
    // API response: {order_id, order_date, status, customer_name, customer_email, customer_phone, shipping_address, payment_method, items, subtotal, tax, shipping_fee, total_amount}
    // Status mapping
    const statusMap = {
        'CHO_XAC_NHAN': {label: 'Chờ xác nhận', color: '#fef3c7', textColor: '#92400e'},
        'DANG_GIAO': {label: 'Đang giao hàng', color: '#dbeafe', textColor: '#1e3a8a'},
        'HOAN_THANH': {label: 'Hoàn thành', color: '#d1fae5', textColor: '#065f46'},
        'DA_HUY': {label: 'Đã hủy', color: '#fee2e2', textColor: '#7f1d1d'}
    };
    
    const statusInfo = statusMap[order.status] || {label: order.status, color: '#e5e7eb', textColor: '#374151'};
    
    orderIdHeading.textContent = `Đơn hàng #${order.order_id}`;
    orderDateEl.textContent = new Date(order.order_date).toLocaleString('vi-VN');
    statusPill.textContent = statusInfo.label;
    statusPill.style.backgroundColor = statusInfo.color;
    statusPill.style.color = statusInfo.textColor;

    receiverNameEl.textContent = order.customer_name || '--';
    phoneNumberEl.textContent = order.customer_phone || '--';
    shippingAddressEl.textContent = order.shipping_address || '--';
    totalAmountEl.textContent = formatCurrency(order.total_amount);
    totalItemsEl.textContent = order.items?.length ?? 0;
    
    const totalQuantity = order.items?.reduce((sum, item) => sum + item.quantity, 0) ?? 0;
    totalQuantityEl.textContent = totalQuantity;

    if (orderNoteSection && orderNoteEl) {
        orderNoteSection.classList.add('hidden');
    }

    // Show cancel button only for CHO_XAC_NHAN status
    const role = (sessionStorage.getItem('role') || '').toUpperCase();
    const isAdmin = role.includes('ADMIN') || role.includes('QUẢN TRỊ') || from === 'admin';
    const canCancel = !isAdmin && order.status === 'CHO_XAC_NHAN';
    
    if (canCancel) {
        orderActionsSection.style.display = 'block';
        cancelOrderBtn.onclick = () => cancelOrder(order.order_id);
    } else {
        orderActionsSection.style.display = 'none';
    }

    if (!order.items || order.items.length === 0) {
        itemsBody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:20px; color:#999;">Không có sản phẩm</td></tr>';
        return;
    }

    itemsBody.innerHTML = order.items.map(item => `
        <tr>
            <td>${item.product_id}</td>
            <td>${item.product_name}</td>
            <td>${formatCurrency(item.unit_price)}</td>
            <td>${item.quantity}</td>
            <td>${formatCurrency(item.subtotal)}</td>
        </tr>
    `).join('');
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
}

function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove('hidden');
    itemsBody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:20px; color:#999;">Không có dữ liệu</td></tr>';
}

function clearError() {
    errorBox.textContent = '';
    errorBox.classList.add('hidden');
}

function setLoading(isLoading) {
    if (isLoading) {
        itemsBody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:20px; color:#999;">Đang tải...</td></tr>';
    }
}

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
            showError('Không thể hủy đơn hàng. Vui lòng thử lại!');
            return;
        }

        const data = await response.json();

        if (data.success) {
            // Redirect to orders list
            window.location.href = '/orders?cancelSuccess=1';
        } else {
            showError('Không thể hủy đơn hàng: ' + (data.error || data.message || 'Lỗi không xác định'));
        }
    } catch (error) {
        console.error('Error cancelling order:', error);
        showError('Lỗi khi hủy đơn hàng. Vui lòng thử lại!');
    }
}

// Custom confirm modal (styling aligned with project)
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

function logout() {
    sessionStorage.clear();
    localStorage.removeItem('userId');
    localStorage.removeItem('email');
    localStorage.removeItem('username');
    window.location.href = '/login';
}
