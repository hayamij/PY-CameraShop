"""
Application Factory
Infrastructure Layer - Flask App Creation
"""
import os
from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
# Optional extensions - commented out if not installed
# from flask_mail import Mail
# from flask_caching import Cache
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
# from flask_cors import CORS

from app.infrastructure.config.config import config
from app.infrastructure.database.db import init_db

# Initialize extensions
login_manager = LoginManager()
bcrypt = Bcrypt()
# Optional extensions - initialize later if needed
# mail = Mail()
# cache = Cache()
# limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
# cors = CORS()


def create_app(config_name='development'):
    """
    Application Factory Pattern
    Creates and configures Flask application
    """
    app = Flask(__name__, 
                template_folder='../../template',
                static_folder='../../static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    init_extensions(app)
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app


def init_extensions(app):
    """Initialize Flask extensions"""
    
    # Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.infrastructure.database.models import UserModel
        return UserModel.query.get(int(user_id))
    
    # Other extensions
    bcrypt.init_app(app)
    # Other extensions
    bcrypt.init_app(app)
    # Optional extensions - uncomment if needed
    # mail.init_app(app)
    # cache.init_app(app)
    # limiter.init_app(app)
    # cors.init_app(app)
def register_blueprints(app):
    """Register Flask blueprints"""
    
    # Main routes (Guest accessible)
    from app.adapters.api.main_routes import main_bp
    app.register_blueprint(main_bp)
    
    # Authentication routes
    from app.adapters.api.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Product routes
    from app.adapters.api.product_routes import product_bp
    app.register_blueprint(product_bp, url_prefix='/products')
    
    # Cart routes (Customer only)
    from app.adapters.api.cart_routes import cart_bp
    app.register_blueprint(cart_bp, url_prefix='/cart')
    
    # Order routes (Customer only)
    from app.adapters.api.order_routes import order_bp
    app.register_blueprint(order_bp, url_prefix='/orders')
    
    # Admin routes
    from app.adapters.api.admin.admin_routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Admin order management routes
    from app.adapters.api.admin_order_routes import admin_orders_bp
    app.register_blueprint(admin_orders_bp)
    
    # Admin dashboard routes
    from app.adapters.api.admin_dashboard_routes import admin_dashboard_bp
    app.register_blueprint(admin_dashboard_bp)
    
    # Admin product management routes
    from app.adapters.api.admin_product_routes import admin_products_bp
    app.register_blueprint(admin_products_bp)
    
    # Admin category management routes
    from app.adapters.api.admin_category_routes import admin_categories_bp
    app.register_blueprint(admin_categories_bp)
    
    # Admin brand management routes
    from app.adapters.api.admin_brand_routes import admin_brands_bp
    app.register_blueprint(admin_brands_bp)
    
    # Checkout routes
    from app.adapters.api.checkout_routes import checkout_bp
    app.register_blueprint(checkout_bp)


def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        from app.infrastructure.database.db import db
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('errors/403.html'), 403
