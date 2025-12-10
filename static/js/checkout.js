// Checkout Page JavaScript

let currentCart = null;
let currentUser = null;

function showValidationError(fieldId, message) {
    const errorElement = document.getElementById(fieldId + 'Error');
    if (message) {
        errorElement.textContent = message;
        errorElement.classList.add('show');
    } else {
        errorElement.classList.remove('show');
    }
}

async function loadCartForCheckout() {
    const userId = sessionStorage.getItem('userId');
    const userEmail = sessionStorage.getItem('email');
    const username = sessionStorage.getItem('username');
    
    if (!userId) {
        showAlert('Vui lòng đăng nhập để thanh toán', 'warning');
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
        return;
    }

    currentUser = {
        userId: userId,
        email: userEmail,
        username: username
    };

    document.getElementById('userEmailDisplay').textContent = userEmail || username || 'User';

    showLoading(true);

    try {
        // API: GET /api/cart - returns {success, cart: {cart_id, items: [...], total_items, total, ...}}
        const response = await fetch('/api/cart');
        const data = await response.json();

        if (data.success && data.cart) {
            if (!data.cart.items || data.cart.items.length === 0) {
                showAlert('Giỏ hàng trống. Vui lòng thêm sản phẩm trước khi thanh toán', 'warning');
                setTimeout(() => {
                    window.location.href = '/products';
                }, 2000);
                return;
            }

            currentCart = data.cart;
            renderOrderSummary(data.cart);
        } else {
            showAlert(data.error || 'Không thể tải giỏ hàng', 'error');
            setTimeout(() => {
                window.location.href = '/cart';
            }, 2000);
        }
    } catch (error) {
        console.error('Error loading cart:', error);
        showAlert('Lỗi kết nối đến server', 'error');
        setTimeout(() => {
            window.location.href = '/cart';
        }, 2000);
    } finally {
        showLoading(false);
    }
}

function renderOrderSummary(cart) {
    const orderItemsList = document.getElementById('orderItemsList');
    
    let html = '';
    cart.items.forEach(item => {
        const hasImage = item.product_image && item.product_image.trim() !== '' && item.product_image !== '/images/no-image.jpg' && item.product_image !== 'null';
        const imageHtml = hasImage 
            ? `<img src="${item.product_image}" alt="${item.product_name}">`
            : '';

        html += `
            <div class="order-item">
                <div class="item-image">${imageHtml}</div>
                <div class="item-details">
                    <div class="item-name">${item.product_name}</div>
                    <div class="item-quantity">Số lượng: ${item.quantity}</div>
                </div>
                <div class="item-price">${formatCurrency(item.subtotal)}</div>
            </div>
        `;
    });
    
    orderItemsList.innerHTML = html;
    
    document.getElementById('summaryTotalItems').textContent = cart.total_items || cart.items.length;
    document.getElementById('summaryTotalQuantity').textContent = cart.total_items || 0;
    document.getElementById('summaryTotalAmount').textContent = formatCurrency(cart.total || cart.subtotal || 0);
}

function validateForm() {
    let isValid = true;

    const receiverName = document.getElementById('receiverName').value.trim();
    if (!receiverName || receiverName.length < 2) {
        showValidationError('receiverName', 'Tên người nhận phải có ít nhất 2 ký tự');
        isValid = false;
    } else {
        showValidationError('receiverName', '');
    }

    const phoneNumber = document.getElementById('phoneNumber').value.trim();
    const phoneRegex = /^[0-9]{10,11}$/;
    if (!phoneRegex.test(phoneNumber)) {
        showValidationError('phoneNumber', 'Số điện thoại phải có 10-11 chữ số');
        isValid = false;
    } else {
        showValidationError('phoneNumber', '');
    }

    const shippingAddress = document.getElementById('shippingAddress').value.trim();
    if (!shippingAddress || shippingAddress.length < 10) {
        showValidationError('shippingAddress', 'Địa chỉ phải có ít nhất 10 ký tự');
        isValid = false;
    } else {
        showValidationError('shippingAddress', '');
    }

    return isValid;
}

async function placeOrder() {
    if (!validateForm()) {
        showAlert('Vui lòng điền đầy đủ thông tin giao hàng', 'warning');
        return;
    }

    if (!currentUser || !currentUser.userId) {
        showAlert('Không tìm thấy thông tin người dùng', 'error');
        return;
    }

    if (!currentCart || !currentCart.items || currentCart.items.length === 0) {
        showAlert('Giỏ hàng trống', 'error');
        return;
    }

    // API: POST /api/orders - body: {shipping_address, phone_number, payment_method, notes}
    const paymentMethod = document.querySelector('input[name="payment-method"]:checked')?.value || 'COD';
    
    const formData = {
        shipping_address: document.getElementById('shippingAddress').value.trim(),
        phone_number: document.getElementById('phoneNumber').value.trim(),
        payment_method: paymentMethod,
        notes: document.getElementById('note').value.trim() || ''
    };

    const placeOrderBtn = document.querySelector('.btn-place-order');
    placeOrderBtn.disabled = true;
    placeOrderBtn.textContent = 'Đang xử lý...';

    try {
        const response = await fetch('/api/orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            showAlert(data.message || 'Đặt hàng thành công!', 'success');
            
            setTimeout(() => {
                alert(`Đơn hàng đã được đặt thành công!\n\n` +
                      `Mã đơn hàng: #${data.order_id}\n` +
                      `Tổng tiền: ${formatCurrency(data.total_amount)}\n\n` +
                      `Cảm ơn bạn đã mua hàng!`);
                
                window.location.href = '/orders';
            }, 1000);
        } else {
            showAlert(data.error || 'Không thể đặt hàng', 'error');
            placeOrderBtn.disabled = false;
            placeOrderBtn.textContent = 'Đặt hàng';
        }
    } catch (error) {
        console.error('Error placing order:', error);
        showAlert('Lỗi kết nối đến server', 'error');
        placeOrderBtn.disabled = false;
        placeOrderBtn.textContent = 'Đặt hàng';
    }
}

window.onload = function() {
    loadCartForCheckout();
};
