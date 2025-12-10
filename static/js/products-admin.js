// products-admin.js
// Admin product management - uses /api/products endpoint with admin privileges

async function searchProducts() {
    const keyword = document.getElementById("keyword")?.value.trim();
    const category_id = document.getElementById("categoryFilter")?.value;
    const brand_id = document.getElementById("brandFilter")?.value;

    // If all empty -> load full list
    if (!keyword && !category_id && !brand_id) {
        loadProducts();
        return;
    }

    const tbody = document.getElementById("productTableBody");
    tbody.innerHTML = `
        <tr><td colspan="9" style="padding:25px;text-align:center;color:#666;">Đang tìm kiếm...</td></tr>
    `;

    const params = new URLSearchParams();
    if (keyword) params.append("search_query", keyword);
    if (category_id) params.append("category_id", category_id);
    if (brand_id) params.append("brand_id", brand_id);
    params.append("per_page", "100"); // Show more for admin

    try {
        const res = await fetch(`/api/products?` + params.toString());
        const data = await res.json();

        if (!data.success || !data.products || data.products.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" style="padding:25px; text-align:center; color:#999;">
                        Không tìm thấy sản phẩm nào
                    </td>
                </tr>
            `;
            return;
        }

        renderProductTable(data.products);

    } catch (err) {
        console.error(err);
        tbody.innerHTML = `
            <tr>
                <td colspan="9" style="padding:25px; text-align:center; color:red;">
                    Lỗi khi tìm kiếm
                </td>
            </tr>
        `;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    updateAdminName();
    loadProducts();
    loadFilters();
});

function updateAdminName() {
    const username = sessionStorage.getItem("username") || "Admin";
    const adminNameEl = document.getElementById("adminName");
    if (adminNameEl) adminNameEl.textContent = username;
}

function formatCurrency(value) {
    return new Intl.NumberFormat("vi-VN", {
        style: "currency",
        currency: "VND"
    }).format(value || 0);
}

async function loadFilters() {
    try {
        const [categoriesRes, brandsRes] = await Promise.all([
            fetch('/api/catalog/categories'),
            fetch('/api/catalog/brands')
        ]);
        
        const categoriesData = await categoriesRes.json();
        const brandsData = await brandsRes.json();
        
        if (categoriesData.success && categoriesData.categories) {
            const categorySelect = document.getElementById("categoryFilter");
            if (categorySelect) {
                categorySelect.innerHTML = '<option value="">Tất cả danh mục</option>' +
                    categoriesData.categories.map(cat => 
                        `<option value="${cat.category_id}">${cat.name}</option>`
                    ).join('');
            }
        }
        
        if (brandsData.success && brandsData.brands) {
            const brandSelect = document.getElementById("brandFilter");
            if (brandSelect) {
                brandSelect.innerHTML = '<option value="">Tất cả thương hiệu</option>' +
                    brandsData.brands.map(brand => 
                        `<option value="${brand.brand_id}">${brand.name}</option>`
                    ).join('');
            }
        }
    } catch (err) {
        console.error("Error loading filters:", err);
    }
}

async function loadProducts() {
    const tbody = document.getElementById("productTableBody");
    if (!tbody) return;

    try {
        const res = await fetch('/api/products?per_page=100');
        const data = await res.json();

        if (!data.success || !data.products || data.products.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" style="text-align:center; padding: 30px; color:#999;">
                        Không có sản phẩm nào
                    </td>
                </tr>`;
            return;
        }

        renderProductTable(data.products);

    } catch (err) {
        console.error("Error loading products:", err);
        tbody.innerHTML = `
            <tr>
                <td colspan="9" style="text-align:center; padding: 30px; color:#e74c3c;">
                    Lỗi khi tải dữ liệu
                </td>
            </tr>`;
    }
}

function renderProductTable(products) {
    const tbody = document.getElementById("productTableBody");
    if (!tbody) return;
    
    tbody.innerHTML = products.map(product => `
        <tr>
            <td>${product.product_id}</td>
            <td><img src="${product.image_url || '/static/images/no-image.jpg'}" class="product-img" style="width:60px;height:60px;object-fit:cover;"></td>
            <td><strong>${product.name}</strong></td>
            <td>${product.category_name || '-'}</td>
            <td>${product.brand_name || '-'}</td>
            <td>${product.stock_quantity}</td>
            <td>${formatCurrency(product.price)}</td>
            <td><span class="badge ${product.is_available ? 'badge-success' : 'badge-danger'}">${product.is_available ? 'Có sẵn' : 'Hết hàng'}</span></td>
            <td class="actions">
                <button class="btn-edit" onclick="editProduct(${product.product_id})">✏️ Sửa</button>
                <button class="btn-delete" onclick="deleteProduct(${product.product_id})">🗑 Xóa</button>
            </td>
        </tr>
    `).join("");
}

function editProduct(id) {
    window.location.href = `/admin/products/edit/${id}`;
}

async function deleteProduct(id) {
    if (!confirm("Bạn có chắc chắn muốn xóa sản phẩm này?")) {
        return;
    }

    try {
        const res = await fetch(`/api/admin/products/${id}`, {
            method: "DELETE"
        });

        const data = await res.json();
        
        if (!data.success) {
            alert("❌ " + (data.error || "Lỗi khi xóa"));
            return;
        }

        alert("✔ Xóa thành công!");
        loadProducts();

    } catch (err) {
        console.error(err);
        alert("⚠ Không thể kết nối server!");
    }
}

function addNewProduct() {
    window.location.href = '/admin/products/add';
}

function logout() {
    sessionStorage.clear();
    window.location.href = '/login';
}
