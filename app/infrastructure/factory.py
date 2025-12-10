"""
Infrastructure Layer - Flask Application Factory
Creates and configures Flask application with all dependencies
"""
from flask import Flask
from pathlib import Path
import os


def create_app(config_name=None):
    """
    Application factory for Flask app
    
    Args:
        config_name: Configuration name (development, testing, production)
        
    Returns:
        Configured Flask application instance
    """
    # Create Flask app
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder='../../template',
        static_folder='../../static'
    )
    
    # Load configuration
    from .config import get_config
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # CRITICAL: Import models BEFORE initializing database
    # This registers them with Base.metadata
    from .database.models import (
        UserModel, RoleModel,
        ProductModel, CategoryModel, BrandModel,
        CartModel, CartItemModel,
        OrderModel, OrderItemModel
    )
    
    # Initialize database AFTER models are imported
    from .config import init_database
    init_database(app)
    
    # Initialize use cases and register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register context processors
    register_context_processors(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'PY-CameraShop API is running'}, 200
    
    @app.route('/')
    def index():
        return {'message': 'Welcome to PY-CameraShop API', 'version': '1.0.0'}, 200
    
    return app


def register_error_handlers(app):
    """Register error handlers for common HTTP errors"""
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not Found', 'message': 'The requested resource was not found'}, 404
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad Request', 'message': 'The request could not be understood'}, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {'error': 'Unauthorized', 'message': 'Authentication is required'}, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Forbidden', 'message': 'You do not have permission to access this resource'}, 403
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}, 500


def register_blueprints(app):
    """
    Register Flask blueprints with dependency injection
    Clean Architecture: Wire use cases to controllers here
    """
    from .config.database import get_session, create_scoped_session
    
    # Import repository adapters
    from ..adapters.repositories import (
        UserRepositoryAdapter,
        ProductRepositoryAdapter,
        BrandRepositoryAdapter,
        CategoryRepositoryAdapter,
        CartRepositoryAdapter,
        OrderRepositoryAdapter
    )
    
    # Import use cases
    from ..business.use_cases.register_user_use_case import RegisterUserUseCase
    from ..business.use_cases.login_user_use_case import LoginUserUseCase
    from ..business.use_cases.get_user_use_case import GetUserUseCase
    from ..business.use_cases.list_products_use_case import ListProductsUseCase
    from ..business.use_cases.get_product_detail_use_case import GetProductDetailUseCase
    from ..business.use_cases.view_cart_use_case import ViewCartUseCase
    from ..business.use_cases.add_to_cart_use_case import AddToCartUseCase
    from ..business.use_cases.update_cart_item_use_case import UpdateCartItemUseCase
    from ..business.use_cases.remove_cart_item_use_case import RemoveCartItemUseCase
    from ..business.use_cases.place_order_use_case import PlaceOrderUseCase
    from ..business.use_cases.get_my_orders_use_case import GetMyOrdersUseCase
    from ..business.use_cases.get_order_detail_use_case import GetOrderDetailUseCase
    from ..business.use_cases.cancel_order_use_case import CancelOrderUseCase
    # Admin use cases
    from ..business.use_cases.create_product_use_case import CreateProductUseCase
    from ..business.use_cases.update_product_use_case import UpdateProductUseCase
    from ..business.use_cases.delete_product_use_case import DeleteProductUseCase
    from ..business.use_cases.create_category_use_case import CreateCategoryUseCase
    from ..business.use_cases.update_category_use_case import UpdateCategoryUseCase
    from ..business.use_cases.delete_category_use_case import DeleteCategoryUseCase
    from ..business.use_cases.create_brand_use_case import CreateBrandUseCase
    from ..business.use_cases.update_brand_use_case import UpdateBrandUseCase
    from ..business.use_cases.delete_brand_use_case import DeleteBrandUseCase
    from ..business.use_cases.list_orders_use_case import ListOrdersUseCase
    from ..business.use_cases.update_order_status_use_case import UpdateOrderStatusUseCase
    
    # Create scoped session for request lifecycle
    session = create_scoped_session()
    
    # Instantiate repositories with scoped session
    user_repository = UserRepositoryAdapter(session)
    product_repository = ProductRepositoryAdapter(session)
    brand_repository = BrandRepositoryAdapter(session)
    category_repository = CategoryRepositoryAdapter(session)
    cart_repository = CartRepositoryAdapter()
    order_repository = OrderRepositoryAdapter()
    
    # Instantiate use cases with dependencies
    register_user_use_case = RegisterUserUseCase(user_repository)
    login_user_use_case = LoginUserUseCase(user_repository)
    get_user_use_case = GetUserUseCase(user_repository)
    list_products_use_case = ListProductsUseCase(
        product_repository=product_repository,
        category_repository=category_repository,
        brand_repository=brand_repository
    )
    get_product_detail_use_case = GetProductDetailUseCase(
        product_repository=product_repository,
        category_repository=category_repository,
        brand_repository=brand_repository
    )
    view_cart_use_case = ViewCartUseCase(
        cart_repository=cart_repository,
        product_repository=product_repository
    )
    add_to_cart_use_case = AddToCartUseCase(
        cart_repository=cart_repository,
        product_repository=product_repository
    )
    update_cart_item_use_case = UpdateCartItemUseCase(
        cart_repository=cart_repository,
        product_repository=product_repository
    )
    remove_cart_item_use_case = RemoveCartItemUseCase(
        cart_repository=cart_repository
    )
    place_order_use_case = PlaceOrderUseCase(
        order_repository=order_repository,
        cart_repository=cart_repository,
        product_repository=product_repository
    )
    get_my_orders_use_case = GetMyOrdersUseCase(
        order_repository=order_repository
    )
    get_order_detail_use_case = GetOrderDetailUseCase(
        order_repository=order_repository,
        user_repository=user_repository,
        product_repository=product_repository
    )
    cancel_order_use_case = CancelOrderUseCase(
        order_repository=order_repository,
        product_repository=product_repository
    )
    # Admin use cases
    create_product_use_case = CreateProductUseCase(
        product_repository=product_repository,
        category_repository=category_repository,
        brand_repository=brand_repository
    )
    update_product_use_case = UpdateProductUseCase(
        product_repository=product_repository,
        category_repository=category_repository,
        brand_repository=brand_repository
    )
    delete_product_use_case = DeleteProductUseCase(product_repository)
    create_category_use_case = CreateCategoryUseCase(category_repository)
    update_category_use_case = UpdateCategoryUseCase(category_repository)
    delete_category_use_case = DeleteCategoryUseCase(
        category_repository=category_repository,
        product_repository=product_repository
    )
    create_brand_use_case = CreateBrandUseCase(brand_repository)
    update_brand_use_case = UpdateBrandUseCase(brand_repository)
    delete_brand_use_case = DeleteBrandUseCase(
        brand_repository=brand_repository,
        product_repository=product_repository
    )
    list_orders_use_case = ListOrdersUseCase(
        order_repository=order_repository,
        user_repository=user_repository
    )
    update_order_status_use_case = UpdateOrderStatusUseCase(order_repository)
    
    # Import and initialize blueprints
    from ..adapters.api import auth_bp, init_auth_routes
    from ..adapters.api.product_routes import create_product_routes
    from ..adapters.api.cart_routes import create_cart_routes
    from ..adapters.api.order_routes import create_order_routes
    from ..adapters.api.admin_routes import create_admin_routes
    from ..adapters.api.catalog_routes import create_catalog_routes
    from ..adapters.views import view_bp
    
    # Initialize auth routes with use cases and repository (for password verification)
    init_auth_routes(
        register_uc=register_user_use_case,
        login_uc=login_user_use_case,
        get_user_uc=get_user_use_case,
        user_repo=user_repository
    )
    
    # Create product routes blueprint
    product_bp = create_product_routes(
        list_products_use_case=list_products_use_case,
        get_product_detail_use_case=get_product_detail_use_case
    )
    
    # Create cart routes blueprint
    cart_bp = create_cart_routes(
        view_cart_use_case=view_cart_use_case,
        add_to_cart_use_case=add_to_cart_use_case,
        update_cart_item_use_case=update_cart_item_use_case,
        remove_cart_item_use_case=remove_cart_item_use_case
    )
    
    # Create order routes blueprint
    order_bp = create_order_routes(
        place_order_use_case=place_order_use_case,
        get_my_orders_use_case=get_my_orders_use_case,
        get_order_detail_use_case=get_order_detail_use_case,
        cancel_order_use_case=cancel_order_use_case
    )
    
    # Create admin routes blueprint
    admin_bp = create_admin_routes(
        create_product_use_case=create_product_use_case,
        update_product_use_case=update_product_use_case,
        delete_product_use_case=delete_product_use_case,
        create_category_use_case=create_category_use_case,
        update_category_use_case=update_category_use_case,
        delete_category_use_case=delete_category_use_case,
        create_brand_use_case=create_brand_use_case,
        update_brand_use_case=update_brand_use_case,
        delete_brand_use_case=delete_brand_use_case,
        list_orders_use_case=list_orders_use_case,
        update_order_status_use_case=update_order_status_use_case
    )
    
    # Create catalog routes blueprint
    catalog_bp = create_catalog_routes(
        category_repository=category_repository,
        brand_repository=brand_repository
    )
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(admin_bp)    # Admin API routes
    app.register_blueprint(catalog_bp)  # Catalog (categories/brands)
    app.register_blueprint(view_bp)     # Frontend views


def register_context_processors(app):
    """Register context processors for templates"""
    
    @app.context_processor
    def inject_app_info():
        return {
            'app_name': 'PY-CameraShop',
            'app_version': '1.0.0'
        }
