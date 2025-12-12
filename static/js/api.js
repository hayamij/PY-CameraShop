/**
 * API Client for Camera Shop
 * Clean Architecture - Adapters Layer Interface
 */

const API_BASE_URL = '/api';

class APIClient {
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };

        if (options.body && typeof options.body === 'object') {
            config.body = JSON.stringify(options.body);
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok && !data.success) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Authentication APIs
    auth = {
        register: (data) => this.request('/auth/register', {
            method: 'POST',
            body: data
        }),
        
        login: (data) => this.request('/auth/login', {
            method: 'POST',
            body: data
        }),
        
        logout: () => this.request('/auth/logout', {
            method: 'POST'
        }),
        
        getCurrentUser: () => this.request('/auth/me')
    };

    // Product APIs
    products = {
        list: (params = {}) => {
            const query = new URLSearchParams(params).toString();
            return this.request(`/products${query ? '?' + query : ''}`);
        },
        
        getDetail: (productId) => this.request(`/products/${productId}`)
    };

    // Catalog APIs
    catalog = {
        getCategories: () => this.request('/catalog/categories'),
        getBrands: () => this.request('/catalog/brands')
    };

    // Cart APIs
    cart = {
        view: () => this.request('/cart'),
        
        add: (productId, quantity) => this.request('/cart/add', {
            method: 'POST',
            body: { product_id: productId, quantity }
        }),
        
        update: (cartItemId, quantity) => this.request(`/cart/items/${cartItemId}`, {
            method: 'PUT',
            body: { quantity }
        }),
        
        remove: (cartItemId) => this.request(`/cart/items/${cartItemId}`, {
            method: 'DELETE'
        })
    };

    // Order APIs
    orders = {
        place: (data) => this.request('/orders', {
            method: 'POST',
            body: data
        }),
        
        getMyOrders: (status = null) => {
            const query = status ? `?status=${status}` : '';
            return this.request(`/orders/my-orders${query}`);
        },
        
        getDetail: (orderId) => this.request(`/orders/${orderId}`),
        
        cancel: (orderId) => this.request(`/orders/${orderId}/cancel`, {
            method: 'POST'
        })
    };

    // Admin User Management APIs
    admin = {
        users: {
            list: (params = {}) => {
                const query = new URLSearchParams(params).toString();
                return this.request(`/admin/users${query ? '?' + query : ''}`);
            },
            
            search: (query) => this.request(`/admin/users/search?q=${encodeURIComponent(query)}`),
            
            create: (data) => this.request('/admin/users', {
                method: 'POST',
                body: data
            }),
            
            update: (userId, data) => this.request(`/admin/users/${userId}`, {
                method: 'PUT',
                body: data
            }),
            
            delete: (userId) => this.request(`/admin/users/${userId}`, {
                method: 'DELETE'
            }),
            
            changeRole: (userId, newRole) => this.request(`/admin/users/${userId}/role`, {
                method: 'PUT',
                body: { new_role: newRole }
            })
        },
        
        // Shorthand methods for backward compatibility
        getUsers: (page = 1, perPage = 20) => {
            return this.request(`/admin/users?page=${page}&per_page=${perPage}`);
        },
        
        getOrders: (page = 1, perPage = 20) => {
            return this.request(`/admin/orders?page=${page}&per_page=${perPage}`);
        },
        
        getOrderDetail: (orderId) => {
            return this.request(`/orders/${orderId}`);
        },
        
        products: {
            create: (data) => this.request('/admin/products', {
                method: 'POST',
                body: data
            }),
            
            update: (productId, data) => this.request(`/admin/products/${productId}`, {
                method: 'PUT',
                body: data
            }),
            
            delete: (productId) => this.request(`/admin/products/${productId}`, {
                method: 'DELETE'
            })
        },
        
        categories: {
            create: (data) => this.request('/admin/categories', {
                method: 'POST',
                body: data
            }),
            
            update: (categoryId, data) => this.request(`/admin/categories/${categoryId}`, {
                method: 'PUT',
                body: data
            }),
            
            delete: (categoryId) => this.request(`/admin/categories/${categoryId}`, {
                method: 'DELETE'
            })
        },
        
        brands: {
            create: (data) => this.request('/admin/brands', {
                method: 'POST',
                body: data
            }),
            
            update: (brandId, data) => this.request(`/admin/brands/${brandId}`, {
                method: 'PUT',
                body: data
            }),
            
            delete: (brandId) => this.request(`/admin/brands/${brandId}`, {
                method: 'DELETE'
            })
        },
        
        orders: {
            list: (params = {}) => {
                const query = new URLSearchParams(params).toString();
                return this.request(`/admin/orders${query ? '?' + query : ''}`);
            },
            
            updateStatus: (orderId, newStatus) => this.request(`/admin/orders/${orderId}/status`, {
                method: 'PUT',
                body: { new_status: newStatus }
            })
        }
    };
}

// Export global API instance
const API = new APIClient();
