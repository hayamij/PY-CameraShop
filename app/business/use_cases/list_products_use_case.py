"""
List Products Use Case - Business Layer
Handles product listing with pagination, filtering, and sorting
"""
from typing import Optional, List
from dataclasses import dataclass
from ...business.ports import IProductRepository, ICategoryRepository, IBrandRepository
from ...domain.entities import Product


@dataclass
class ListProductsInputData:
    """Input data for listing products"""
    page: int = 1
    per_page: int = 12
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    search_query: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    sort_by: str = 'newest'  # newest, price_asc, price_desc, name


@dataclass
class ProductItemOutputData:
    """Single product data for output"""
    product_id: int
    name: str
    description: str
    price: float
    currency: str
    stock_quantity: int
    category_name: Optional[str]
    brand_name: Optional[str]
    image_url: Optional[str]
    is_available: bool


@dataclass
class ListProductsOutputData:
    """Output data for product listing"""
    success: bool
    products: List[ProductItemOutputData]
    total_products: int
    total_pages: int
    current_page: int
    has_next: bool
    has_prev: bool
    error_message: Optional[str] = None


class ListProductsUseCase:
    """Use case for listing products with filters and pagination"""
    
    def __init__(
        self,
        product_repository: IProductRepository,
        category_repository: ICategoryRepository,
        brand_repository: IBrandRepository
    ):
        """
        Initialize use case with repository dependencies
        
        Args:
            product_repository: Repository for product data access
            category_repository: Repository for category data access
            brand_repository: Repository for brand data access
        """
        self.product_repository = product_repository
        self.category_repository = category_repository
        self.brand_repository = brand_repository
    
    def execute(self, input_data: ListProductsInputData) -> ListProductsOutputData:
        """
        Execute use case to list products
        
        Args:
            input_data: Input parameters for listing
            
        Returns:
            ListProductsOutputData with products and pagination info
        """
        try:
            # Validate input
            if input_data.page < 1:
                input_data.page = 1
            if input_data.per_page < 1 or input_data.per_page > 100:
                input_data.per_page = 12
            
            # Get products based on filters
            if input_data.category_id:
                products = self.product_repository.find_by_category(input_data.category_id)
            elif input_data.brand_id:
                products = self.product_repository.find_by_brand(input_data.brand_id)
            elif input_data.search_query:
                products = self.product_repository.search_by_name(input_data.search_query)
            else:
                products = self.product_repository.find_all()
            
            # Filter by price range
            if input_data.min_price is not None or input_data.max_price is not None:
                products = self._filter_by_price(
                    products,
                    input_data.min_price,
                    input_data.max_price
                )
            
            # Filter only visible products
            products = [p for p in products if p.is_available_for_purchase()]
            
            # Sort products
            products = self._sort_products(products, input_data.sort_by)
            
            # Calculate pagination
            total_products = len(products)
            total_pages = (total_products + input_data.per_page - 1) // input_data.per_page
            
            # Ensure page is within bounds
            if input_data.page > total_pages and total_pages > 0:
                input_data.page = total_pages
            
            # Paginate
            start_idx = (input_data.page - 1) * input_data.per_page
            end_idx = start_idx + input_data.per_page
            paginated_products = products[start_idx:end_idx]
            
            # Convert to output format
            product_items = []
            for product in paginated_products:
                # Get category and brand names
                category_name = None
                if product.category_id:
                    category = self.category_repository.find_by_id(product.category_id)
                    if category:
                        category_name = category.name
                
                brand_name = None
                if product.brand_id:
                    brand = self.brand_repository.find_by_id(product.brand_id)
                    if brand:
                        brand_name = brand.name
                
                product_items.append(ProductItemOutputData(
                    product_id=product.product_id,
                    name=product.name,
                    description=product.description,
                    price=float(product.price.amount),
                    currency=product.price.currency,
                    stock_quantity=product.stock_quantity,
                    category_name=category_name,
                    brand_name=brand_name,
                    image_url=product.image_url,
                    is_available=product.is_available_for_purchase()
                ))
            
            return ListProductsOutputData(
                success=True,
                products=product_items,
                total_products=total_products,
                total_pages=total_pages,
                current_page=input_data.page,
                has_next=input_data.page < total_pages,
                has_prev=input_data.page > 1
            )
            
        except Exception as e:
            return ListProductsOutputData(
                success=False,
                products=[],
                total_products=0,
                total_pages=0,
                current_page=1,
                has_next=False,
                has_prev=False,
                error_message=str(e)
            )
    
    def _filter_by_price(
        self,
        products: List[Product],
        min_price: Optional[float],
        max_price: Optional[float]
    ) -> List[Product]:
        """Filter products by price range"""
        filtered = []
        for product in products:
            price = float(product.price.amount)
            if min_price is not None and price < min_price:
                continue
            if max_price is not None and price > max_price:
                continue
            filtered.append(product)
        return filtered
    
    def _sort_products(self, products: List[Product], sort_by: str) -> List[Product]:
        """Sort products based on criteria"""
        if sort_by == 'price_asc':
            return sorted(products, key=lambda p: float(p.price.amount))
        elif sort_by == 'price_desc':
            return sorted(products, key=lambda p: float(p.price.amount), reverse=True)
        elif sort_by == 'name':
            return sorted(products, key=lambda p: p.name.lower())
        elif sort_by == 'newest':
            # Assuming products with higher IDs are newer
            return sorted(products, key=lambda p: p.product_id, reverse=True)
        else:
            return products
