// Register Page JavaScript

function showValidationError(fieldId, message) {
    const errorElement = document.getElementById(fieldId + 'Error');
    if (message) {
        errorElement.textContent = message;
        errorElement.classList.add('show');
    } else {
        errorElement.classList.remove('show');
    }
}

function togglePassword(fieldId) {
    const passwordInput = document.getElementById(fieldId);
    const toggleBtn = passwordInput.nextElementSibling;
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleBtn.textContent = 'Ẩn';
    } else {
        passwordInput.type = 'password';
        toggleBtn.textContent = 'Hiện';
    }
}

function checkPasswordStrength(password) {
    const strengthBar = document.getElementById('strengthBar');
    const strengthText = document.getElementById('strengthText');
    
    if (password.length === 0) {
        strengthBar.className = 'password-strength-bar';
        strengthText.textContent = 'Nhập mật khẩu';
        return;
    }

    let strength = 0;
    if (password.length >= 6) strength++;
    if (password.length >= 10) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[@$!%*?&#]/.test(password)) strength++;

    if (strength <= 2) {
        strengthBar.className = 'password-strength-bar strength-weak';
        strengthText.textContent = 'Mật khẩu yếu';
    } else if (strength <= 3) {
        strengthBar.className = 'password-strength-bar strength-medium';
        strengthText.textContent = 'Mật khẩu trung bình';
    } else {
        strengthBar.className = 'password-strength-bar strength-strong';
        strengthText.textContent = 'Mật khẩu mạnh';
    }
}

function validateForm() {
    let isValid = true;

    const username = document.getElementById('username').value.trim();
    if (!username || username.length < 3) {
        showValidationError('username', 'Tên đăng nhập phải có ít nhất 3 ký tự');
        isValid = false;
    } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        showValidationError('username', 'Tên đăng nhập chỉ chứa chữ, số và dấu gạch dưới');
        isValid = false;
    } else {
        showValidationError('username', '');
    }

    const name = document.getElementById('name').value.trim();
    if (!name || name.length < 2) {
        showValidationError('name', 'Họ tên phải có ít nhất 2 ký tự');
        isValid = false;
    } else {
        showValidationError('name', '');
    }

    const email = document.getElementById('email').value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showValidationError('email', 'Email không hợp lệ');
        isValid = false;
    } else {
        showValidationError('email', '');
    }

    const phone = document.getElementById('phone').value.trim();
    const phoneRegex = /^[0-9]{10,11}$/;
    if (!phoneRegex.test(phone)) {
        showValidationError('phone', 'Số điện thoại phải có 10-11 chữ số');
        isValid = false;
    } else {
        showValidationError('phone', '');
    }

    const address = document.getElementById('address').value.trim();
    if (!address || address.length < 10) {
        showValidationError('address', 'Địa chỉ phải có ít nhất 10 ký tự');
        isValid = false;
    } else {
        showValidationError('address', '');
    }

    const password = document.getElementById('password').value;
    if (password.length < 6) {
        showValidationError('password', 'Mật khẩu phải có ít nhất 6 ký tự');
        isValid = false;
    } else {
        showValidationError('password', '');
    }

    const confirmPassword = document.getElementById('confirmPassword').value;
    if (password !== confirmPassword) {
        showValidationError('confirmPassword', 'Mật khẩu xác nhận không khớp');
        isValid = false;
    } else {
        showValidationError('confirmPassword', '');
    }

    const agreeTerms = document.getElementById('agreeTerms').checked;
    if (!agreeTerms) {
        showAlert('Vui lòng đồng ý với điều khoản sử dụng', 'error');
        isValid = false;
    }

    return isValid;
}

function setLoading(loading) {
    const registerBtn = document.getElementById('registerBtn');
    const form = document.getElementById('registerForm');
    
    if (loading) {
        registerBtn.disabled = true;
        registerBtn.textContent = 'Đang xử lý...';
        form.querySelectorAll('input, button').forEach(el => el.disabled = true);
    } else {
        registerBtn.disabled = false;
        registerBtn.textContent = 'Đăng ký tài khoản';
        form.querySelectorAll('input, button').forEach(el => el.disabled = false);
    }
}

document.getElementById('password').addEventListener('input', function() {
    checkPasswordStrength(this.value);
});

document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
        return;
    }

    const formData = {
        username: document.getElementById('username').value.trim(),
        full_name: document.getElementById('name').value.trim(),
        email: document.getElementById('email').value.trim(),
        phone_number: document.getElementById('phone').value.trim(),
        address: document.getElementById('address').value.trim(),
        password: document.getElementById('password').value
    };

    setLoading(true);

    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success && data.user_id) {
            // API response: {success: true, user_id: int, message: "..."}
            showAlert('Đăng ký thành công! Đang chuyển đến trang đăng nhập...', 'success');
            
            setTimeout(() => {
                window.location.href = '/login';
            }, 1500);
        } else {
            // API error response: {success: false, error: "message"}
            showAlert(data.error || data.errorMessage || 'Đăng ký thất bại', 'error');
            
            // Handle specific errors
            if (data.error && data.error.includes('username')) {
                showValidationError('username', 'Tên đăng nhập đã tồn tại');
            }
            if (data.error && data.error.includes('email')) {
                showValidationError('email', 'Email này đã được sử dụng');
            }
        }
    } catch (error) {
        console.error('Register error:', error);
        showAlert('Lỗi kết nối đến server', 'error');
    } finally {
        setLoading(false);
    }
});
