"""
Cart Repository Adapter - Infrastructure implementation
"""
from typing import Optional
from ...business.ports import ICartRepository
from ...domain.entities import Cart, CartItem
from ...infrastructure.database.models import CartModel, CartItemModel
from ...infrastructure.database.db import db


class CartRepositoryAdapter(ICartRepository):
    """Adapter implementing cart repository using SQLAlchemy"""
    
    def save(self, cart: Cart) -> Cart:
        """Save or update cart"""
        if cart.id is None:
            # Create new cart
            db_cart = CartModel(
                customer_id=cart.customer_id,
                created_at=cart.created_at,
                updated_at=cart.updated_at
            )
            db.session.add(db_cart)
            db.session.commit()
            db.session.refresh(db_cart)
            
            # Save cart items
            for item in cart.items:
                db_item = CartItemModel(
                    cart_id=db_cart.id,
                    product_id=item.product_id,
                    quantity=item.quantity
                )
                db.session.add(db_item)
            db.session.commit()
            
            return self._to_domain(db_cart)
        else:
            # Update existing cart
            db_cart = db.session.query(CartModel).filter_by(id=cart.id).first()
            if db_cart:
                db_cart.updated_at = cart.updated_at
                
                # Clear existing items
                db.session.query(CartItemModel).filter_by(cart_id=cart.id).delete()
                
                # Add new items
                for item in cart.items:
                    db_item = CartItemModel(
                        cart_id=cart.id,
                        product_id=item.product_id,
                        quantity=item.quantity
                    )
                    db.session.add(db_item)
                
                db.session.commit()
                return self._to_domain(db_cart)
        
        return cart
    
    def find_by_id(self, cart_id: int) -> Optional[Cart]:
        """Find cart by ID"""
        db_cart = db.session.query(CartModel).filter_by(id=cart_id).first()
        return self._to_domain(db_cart) if db_cart else None
    
    def find_by_customer_id(self, customer_id: int) -> Optional[Cart]:
        """Find cart by customer ID"""
        db_cart = db.session.query(CartModel).filter_by(customer_id=customer_id).first()
        return self._to_domain(db_cart) if db_cart else None
    
    def delete(self, cart_id: int) -> bool:
        """Delete cart"""
        db_cart = db.session.query(CartModel).filter_by(id=cart_id).first()
        if db_cart:
            db.session.delete(db_cart)
            db.session.commit()
            return True
        return False
    
    def clear_cart(self, customer_id: int) -> bool:
        """Clear all items from customer's cart"""
        db_cart = db.session.query(CartModel).filter_by(customer_id=customer_id).first()
        if db_cart:
            db.session.query(CartItemModel).filter_by(cart_id=db_cart.id).delete()
            db.session.commit()
            return True
        return False
    
    def find_by_user_id(self, user_id: int) -> Optional[Cart]:
        """Find cart by user ID (alias for find_by_customer_id)"""
        return self.find_by_customer_id(user_id)
    
    def create_cart(self, user_id: int) -> Cart:
        """Create a new cart for user"""
        from datetime import datetime
        db_cart = CartModel(
            customer_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(db_cart)
        db.session.commit()
        db.session.refresh(db_cart)
        return self._to_domain(db_cart)
    
    def find_cart_item(self, cart_id: int, product_id: int) -> Optional[CartItem]:
        """Find a specific cart item"""
        db_item = db.session.query(CartItemModel).filter_by(
            cart_id=cart_id,
            product_id=product_id
        ).first()
        if db_item:
            return CartItem(
                product_id=db_item.product_id,
                quantity=db_item.quantity,
                cart_item_id=db_item.id
            )
        return None
    
    def find_cart_item_by_id(self, cart_item_id: int) -> Optional[CartItem]:
        """Find cart item by its ID"""
        db_item = db.session.query(CartItemModel).filter_by(id=cart_item_id).first()
        if db_item:
            return CartItem(
                product_id=db_item.product_id,
                quantity=db_item.quantity,
                cart_item_id=db_item.id,
                cart_id=db_item.cart_id
            )
        return None
    
    def add_item_to_cart(self, cart_id: int, product_id: int, quantity: int) -> CartItem:
        """Add a new item to cart"""
        db_item = CartItemModel(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(db_item)
        db.session.commit()
        db.session.refresh(db_item)
        return CartItem(
            product_id=db_item.product_id,
            quantity=db_item.quantity,
            cart_item_id=db_item.id
        )
    
    def update_cart_item_quantity(self, cart_item_id: int, new_quantity: int) -> CartItem:
        """Update quantity of a cart item"""
        db_item = db.session.query(CartItemModel).filter_by(id=cart_item_id).first()
        if db_item:
            db_item.quantity = new_quantity
            db.session.commit()
            return CartItem(
                product_id=db_item.product_id,
                quantity=db_item.quantity,
                cart_item_id=db_item.id
            )
        return None
    
    def remove_cart_item(self, cart_item_id: int) -> bool:
        """Remove an item from cart"""
        db_item = db.session.query(CartItemModel).filter_by(id=cart_item_id).first()
        if db_item:
            db.session.delete(db_item)
            db.session.commit()
            return True
        return False
    
    def _to_domain(self, db_cart: CartModel) -> Cart:
        """Convert database model to domain entity"""
        items = [
            CartItem(
                product_id=db_item.product_id,
                quantity=db_item.quantity,
                cart_item_id=db_item.id,
                cart_id=db_cart.id
            )
            for db_item in db_cart.items
        ]
        return Cart.reconstruct(
            cart_id=db_cart.id,
            customer_id=db_cart.customer_id,
            items=items,
            created_at=db_cart.created_at,
            updated_at=db_cart.updated_at
        )
