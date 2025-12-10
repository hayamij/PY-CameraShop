// Home Page JavaScript

let products = [];

function checkAuth() {
    const userId = sessionStorage.getItem('userId');
    const username = sessionStorage.getItem('username');

    if (!userId) {
        window.location.href = '/login';
        return;
    }

    document.getElementById('userName').textContent = username || 'User';
}

async function loadCartInfo() {
    const userId = sessionStorage.getItem('userId');
    if (!userId) return;

    try {
        // API: GET /api/cart - requires login
        const response = await fetch('/api/cart');
        if (!response.ok) return; // Not logged in or error
        
        const data = await response.json();

        if (data.success && data.cart) {
            const cartBadge = document.getElementById('cartItems');
            if (cartBadge) {
                cartBadge.textContent = data.cart.total_items || 0;
            }
        }
    } catch (error) {
        console.error('Error loading cart info:', error);
    }
}

async function loadProducts() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    const productsList = document.getElementById('productsList');
    
    try {
        // Show loading
        loadingIndicator?.classList.remove('hidden');
        productsList?.classList.add('hidden');
        
        // API: GET /api/products - returns {success, products: [...], total_products, ...}
        const response = await fetch('/api/products');
        const data = await response.json();
        
        if (!data.success || !data.products) {
            throw new Error(data.error || 'Failed to load products');
        }
        
        products = data.products.map(product => {
            return {
                id: product.product_id,
                name: product.name,
                description: product.description || '',
                price: product.price,
                category: product.category_name || 'Sản phẩm',
                brand: product.brand_name || '',
                stock: product.stock_quantity,
                imageUrl: product.image_url,
                categoryId: product.category_id,
                brandId: product.brand_id
            };
        });
        
        // Populate filter dropdowns
        populateFilters();
        
        renderProducts();
        
        // Hide loading, show products
        loadingIndicator?.classList.add('hidden');
        productsList?.classList.remove('hidden');
    } catch (error) {
        console.error('Error loading products:', error);
        loadingIndicator?.classList.add('hidden');
        showAlert('Không thể tải danh sách sản phẩm. Vui lòng thử lại sau.', 'error');
    }
}

function populateFilters() {
    // Get unique categories and brands
    const categories = [...new Set(products.map(p => p.category))].filter(Boolean);
    const brands = [...new Set(products.map(p => p.brand))].filter(Boolean);
    
    // Populate category filter
    const categoryFilter = document.getElementById('categoryFilter');
    if (categoryFilter) {
        categoryFilter.innerHTML = '<option value="">Tất cả danh mục</option>' +
            categories.map(cat => `<option value="${cat}">${cat}</option>`).join('');
    }
    
    // Populate brand filter
    const brandFilter = document.getElementById('brandFilter');
    if (brandFilter) {
        brandFilter.innerHTML = '<option value="">Tất cả thương hiệu</option>' +
            brands.map(brand => `<option value="${brand}">${brand}</option>`).join('');
    }
}

function filterProducts() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const sortBy = document.getElementById('sortSelect')?.value || '';
    const categoryFilter = document.getElementById('categoryFilter')?.value || '';
    const brandFilter = document.getElementById('brandFilter')?.value || '';
    
    // Filter products
    let filtered = products.filter(product => {
        const matchesSearch = !searchTerm || 
            product.name.toLowerCase().includes(searchTerm) ||
            product.description.toLowerCase().includes(searchTerm);
        const matchesCategory = !categoryFilter || product.category === categoryFilter;
        const matchesBrand = !brandFilter || product.brand === brandFilter;
        
        return matchesSearch && matchesCategory && matchesBrand;
    });
    
    // Sort products
    if (sortBy === 'name-asc') {
        filtered.sort((a, b) => a.name.localeCompare(b.name));
    } else if (sortBy === 'name-desc') {
        filtered.sort((a, b) => b.name.localeCompare(a.name));
    } else if (sortBy === 'price-asc') {
        filtered.sort((a, b) => a.price - b.price);
    } else if (sortBy === 'price-desc') {
        filtered.sort((a, b) => b.price - a.price);
    }
    
    renderProducts(filtered);
}

function renderProducts(productsToRender = products) {
    const productsList = document.getElementById('productsList');
    
    if (productsToRender.length === 0) {
        productsList.innerHTML = '<div style="text-align: center; padding: 40px; color: #7a7a7a; grid-column: 1 / -1;">Không tìm thấy sản phẩm nào</div>';
        return;
    }
    
    let html = '';
    productsToRender.forEach(product => {
        let stockClass = '';
        let stockText = `Còn ${product.stock} sản phẩm`;
        
        if (product.stock === 0) {
            stockClass = 'stock-out';
            stockText = 'Hết hàng';
        } else if (product.stock < 10) {
            stockClass = 'stock-low';
            stockText = `Chỉ còn ${product.stock} sản phẩm`;
        }

        const hasValidImage = product.imageUrl && product.imageUrl.trim() !== '' && product.imageUrl !== '/images/no-image.jpg' && product.imageUrl !== 'null';
        
        html += `
            <div class="product-card">
                <div class="product-image-container" onclick="viewProduct(${product.id})">
                    ${hasValidImage ? `<img src="${product.imageUrl}" alt="${product.name}" class="product-image">` : ''}
                    ${product.stock < 10 && product.stock > 0 ? '<div class="product-badge">Sắp hết</div>' : ''}
                    ${product.stock === 0 ? '<div class="product-badge" style="background: #f8d7da; color: #721c24;">Hết hàng</div>' : ''}
                </div>
                <div class="product-info">
                    <div class="product-category">${product.category}</div>
                    <div class="product-name" onclick="viewProduct(${product.id})" style="cursor: pointer;">${product.name}</div>
                    <div class="product-description">${product.description}</div>
                    <div class="product-footer">
                        <div>
                            <div class="product-price">${formatCurrency(product.price)}</div>
                            <div class="product-stock ${stockClass}">${stockText}</div>
                        </div>
                        <button class="btn-add-cart" onclick="addToCart(event, ${product.id})" ${product.stock === 0 ? 'disabled' : ''}>
                            ${product.stock === 0 ? 'Hết hàng' : 'Thêm'}
                        </button>
                    </div>
                </div>
            </div>
        `;
    });

    productsList.innerHTML = html;
}

function viewProduct(productId) {
    window.location.href = `/products/${productId}`;
}

async function addToCart(event, productId) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    const userId = sessionStorage.getItem('userId');
    if (!userId) {
        if (confirm('Bạn cần đăng nhập để thêm sản phẩm vào giỏ hàng. Chuyển đến trang đăng nhập?')) {
            window.location.href = '/login';
        }
        return;
    }

    const button = event ? event.target : null;
    const originalText = button ? button.innerHTML : '';
    
    if (button) {
        button.disabled = true;
        button.innerHTML = 'Đang thêm...';
    }

    try {
        // API: POST /api/cart/add - body: {product_id, quantity}
        const response = await fetch('/api/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: 1
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            if (button) {
                button.innerHTML = 'Đã thêm';
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.disabled = false;
                }, 1500);
            }
            await loadCartInfo();
            showToast('Đã thêm sản phẩm vào giỏ hàng!', 'success');
        } else {
            alert(data.errorMessage || 'Không thể thêm vào giỏ hàng');
            if (button) {
                button.innerHTML = originalText;
                button.disabled = false;
            }
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        alert('Lỗi kết nối đến server. Vui lòng thử lại.');
        if (button) {
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }
}

window.onload = function() {
    checkAuth();
    loadCartInfo();
    loadProducts();
};
