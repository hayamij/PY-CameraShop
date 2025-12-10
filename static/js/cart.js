// Cart Page JavaScript

let currentCart = null;

async function loadCart() {
    const userId = sessionStorage.getItem('userId');
    
    if (!userId) {
        showAlert('Vui lòng đăng nhập để xem giỏ hàng', 'warning');
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
        return;
    }

    showLoading(true);

    try {
        // API: GET /api/cart - returns {success, cart: {cart_id, items: [...], total_items, total, ...}}
        const response = await fetch('/api/cart');
        const data = await response.json();

        if (data.success && data.cart) {
            currentCart = data.cart;
            renderCart(data.cart);
        } else {
            showAlert(data.error || 'Không thể tải giỏ hàng', 'error');
            renderEmptyCart();
        }
    } catch (error) {
        console.error('Error loading cart:', error);
        showAlert('Lỗi kết nối đến server', 'error');
        renderEmptyCart();
    } finally {
        showLoading(false);
    }
}

function renderCart(cart) {
    const cartItemsList = document.getElementById('cartItemsList');
    const cartContainer = document.getElementById('cartContainer');

    if (!cart.items || cart.items.length === 0) {
        renderEmptyCart();
        return;
    }

    let html = '<div class="cart-items">';

    cart.items.forEach(item => {
        // Check stock availability: item.is_available and item.stock_available
        const hasStockIssue = !item.is_available || item.quantity > item.stock_available;
        const stockClass = hasStockIssue ? 'stock-warning' : '';

        const hasImage = item.product_image && item.product_image.trim() !== '' && item.product_image !== '/images/no-image.jpg' && item.product_image !== 'null';
        const imageUrl = hasImage ? item.product_image : '';
        
        html += `
            <div class="cart-item ${stockClass}">
                <div class="product-image">
                    ${hasImage ? `<img src="${imageUrl}" alt="${item.productName}">` : ''}
                </div>
                
                <div class="product-info">
                    <div class="product-name">${item.productName}</div>
                    <div class="product-price">${formatCurrency(item.price)} / sản phẩm</div>
                    <div class="product-stock">
                        Còn lại: ${item.availableStock} sản phẩm
                        ${hasStockIssue ? '<span class="stock-badge badge-warning">Vượt tồn kho</span>' : ''}
                    </div>
                </div>
                
                <div class="quantity-controls">
                    <button class="quantity-btn" onclick="decreaseQuantity(${item.productId}, ${item.quantity})">−</button>
                    <input type="number" class="quantity-input" id="qty-${item.productId}" value="${item.quantity}" min="0" onchange="applyQuantityChange(${item.productId})">
                    <button class="quantity-btn" onclick="increaseQuantity(${item.productId}, ${item.quantity})">+</button>
                </div>
                
                <div class="item-actions">
                    <div class="item-subtotal">${formatCurrency(item.subtotal)}</div>
                    <button class="btn-remove" onclick="removeItem(${item.productId})">Xóa</button>
                </div>
            </div>
        `;
    });

    html += '</div>';
    cartItemsList.innerHTML = html;

    document.getElementById('summaryTotalItems').textContent = cart.total_items || cart.items.length;
    document.getElementById('summaryTotalQuantity').textContent = cart.total_items || 0;
    document.getElementById('summaryTotalAmount').textContent = formatCurrency(cart.total || cart.subtotal || 0);

    cartContainer.classList.remove('hidden');
}

function renderEmptyCart() {
    const cartContainer = document.getElementById('cartContainer');
    cartContainer.innerHTML = `
        <div class="cart-items-section">
            <div class="cart-empty">
                <h2>Giỏ hàng trống</h2>
                <p>Bạn chưa có sản phẩm nào trong giỏ hàng</p>
                <button class="btn-checkout" onclick="window.location.href='/products'">
                    Bắt đầu mua sắm
                </button>
            </div>
        </div>
    `;
    cartContainer.classList.remove('hidden');
}

async function increaseQuantity(cartItemId, currentQuantity) {
    const newQuantity = currentQuantity + 1;
    await updateQuantity(cartItemId, newQuantity);
}

async function decreaseQuantity(cartItemId, currentQuantity) {
    const newQuantity = currentQuantity - 1;
    await updateQuantity(cartItemId, newQuantity);
}

async function applyQuantityChange(cartItemId) {
    const input = document.getElementById(`qty-${cartItemId}`);
    if (!input) return;

    const newQuantity = parseInt(input.value);
    await updateQuantity(cartItemId, newQuantity);
}

async function updateQuantity(cartItemId, newQuantity) {
    if (!currentCart) {
        showAlert('Không tìm thấy thông tin giỏ hàng', 'error');
        return;
    }

    try {
        // API: PUT /api/cart/items/:cart_item_id - body: {quantity}
        const response = await fetch(`/api/cart/items/${cartItemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                quantity: newQuantity
            })
        });

        const data = await response.json();

        if (data.success) {
            showAlert(data.message || 'Đã cập nhật', 'success');
            loadCart();
        } else {
            showAlert(data.error || 'Không thể cập nhật', 'error');
        }
    } catch (error) {
        console.error('Error updating quantity:', error);
        showAlert('Lỗi kết nối đến server', 'error');
    }
}

async function removeItem(cartItemId) {
    if (!confirm('Bạn có chắc muốn xóa sản phẩm này khỏi giỏ hàng?')) {
        return;
    }

    try {
        // API: DELETE /api/cart/items/:cart_item_id
        const response = await fetch(`/api/cart/items/${cartItemId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showAlert(data.message || 'Đã xóa', 'success');
            loadCart();
        } else {
            showAlert(data.error || 'Không thể xóa', 'error');
        }
    } catch (error) {
        console.error('Error removing item:', error);
        showAlert('Lỗi kết nối đến server', 'error');
    }
}

async function checkout() {
    window.location.href = '/checkout';
}

window.onload = function() {
    loadCart();
};
