// Login Page JavaScript

function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleBtn = document.querySelector('.password-toggle');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleBtn.textContent = 'Ẩn';
    } else {
        passwordInput.type = 'password';
        toggleBtn.textContent = 'Hiện';
    }
}

function setLoading(loading) {
    const loginBtn = document.getElementById('loginBtn');
    const form = document.getElementById('loginForm');
    
    if (loading) {
        loginBtn.disabled = true;
        loginBtn.textContent = 'Đang đăng nhập...';
        form.querySelectorAll('input, button').forEach(el => el.disabled = true);
    } else {
        loginBtn.disabled = false;
        loginBtn.textContent = 'Đăng nhập';
        form.querySelectorAll('input, button').forEach(el => el.disabled = false);
    }
}

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const rememberMe = document.getElementById('rememberMe').checked;

    if (!email || !password) {
        showAlert('Vui lòng điền đầy đủ thông tin', 'error');
        return;
    }

    setLoading(true);

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: email,  // API accepts username (can be email or username)
                password: password
            })
        });

        const data = await response.json();

        if (data.success && data.user) {
            // API response structure: {success: true, user: {id, username, role, full_name, email}}
            sessionStorage.setItem('userId', data.user.id);
            sessionStorage.setItem('email', data.user.email);
            sessionStorage.setItem('username', data.user.username);
            sessionStorage.setItem('role', data.user.role);
            sessionStorage.setItem('fullName', data.user.full_name);

            if (rememberMe) {
                localStorage.setItem('userId', data.user.id);
                localStorage.setItem('email', data.user.email);
                localStorage.setItem('username', data.user.username);
            }

            console.log('✅ Đăng nhập thành công');
            console.log('Role từ API:', data.user.role);
            console.log('Role lưu trong sessionStorage:', sessionStorage.getItem('role'));

            showAlert('Đăng nhập thành công! Đang chuyển hướng...', 'success');

            // Chuyển hướng dựa trên vai trò
            const role = data.user.role ? String(data.user.role).trim().toUpperCase() : '';
            console.log('Role đã format:', role);
            
            const isAdmin = role.includes('ADMIN') || 
                           role.includes('QUẢN TRỊ') ||
                           role.includes('ADMIN_ROLE') ||
                           role.includes('ROLE_ADMIN');
            const redirectUrl = isAdmin ? '/admin' : '/products';
            
            console.log('Is Admin?', isAdmin);
            console.log('Chuyển hướng đến:', redirectUrl);

            setTimeout(() => {
                window.location.href = redirectUrl;
            }, 1500);
        } else {
            showAlert(data.error || data.errorMessage || 'Đăng nhập thất bại', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showAlert('Lỗi kết nối đến server', 'error');
    } finally {
        setLoading(false);
    }
});

window.onload = function() {
    const savedEmail = localStorage.getItem('email');
    if (savedEmail) {
        document.getElementById('email').value = savedEmail;
        document.getElementById('rememberMe').checked = true;
    }
};
