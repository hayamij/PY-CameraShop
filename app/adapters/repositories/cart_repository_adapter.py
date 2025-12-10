"""Cart Repository Adapter - Infrastructure implementation of cart persistence."""
from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from ...business.ports.cart_repository import ICartRepository
from ...domain.entities.cart import Cart, CartItem
from ...infrastructure.config.database import get_session
from ...infrastructure.database.models.cart_model import CartModel, CartItemModel


class CartRepositoryAdapter(ICartRepository):
    """Adapter for Cart persistence using SQLAlchemy."""
    
    def __init__(self, session=None):
        """
        Initialize cart repository adapter.
        
        Args:
            session: SQLAlchemy session (optional, for testing)
        """
        self._session = session
    
    def find_by_id(self, cart_id: int) -> Optional[Cart]:
        """
        Find cart by cart ID.
        
        Args:
            cart_id: Cart ID to find
            
        Returns:
            Cart entity if found, None otherwise
        """
        session = self._session or get_session()
        try:
            # Eagerly load cart items and their products
            cart_model = (session.query(CartModel)
                         .options(
                             joinedload(CartModel.items)
                             .joinedload(CartItemModel.product)
                         )
                         .filter(CartModel.cart_id == cart_id)
                         .first())
            
            if not cart_model:
                return None
            
            return self._to_domain_entity(cart_model)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def find_by_customer_id(self, customer_id: int) -> Optional[Cart]:
        """
        Find cart by customer ID.
        
        Args:
            customer_id: Customer ID to find cart for
            
        Returns:
            Cart entity if found, None otherwise
        """
        session = self._session or get_session()
        try:
            # Eagerly load cart items and their products
            cart_model = (session.query(CartModel)
                         .options(
                             joinedload(CartModel.items)
                             .joinedload(CartItemModel.product)
                         )
                         .filter(CartModel.user_id == customer_id)
                         .first())
            
            if not cart_model:
                return None
            
            return self._to_domain_entity(cart_model)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def find_by_user_id(self, user_id: int) -> Optional[Cart]:
        """
        Find cart by user ID (alias for find_by_customer_id).
        
        Args:
            user_id: User ID to find cart for
            
        Returns:
            Cart entity if found, None otherwise
        """
        return self.find_by_customer_id(user_id)
    
    def create_cart(self, user_id: int) -> Cart:
        """
        Create a new empty cart for a user.
        
        Args:
            user_id: User ID to create cart for
            
        Returns:
            Created cart entity
        """
        from datetime import datetime
        session = self._session or get_session()
        try:
            cart_model = CartModel(
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(cart_model)
            session.commit()
            session.refresh(cart_model)
            
            return self._to_domain_entity(cart_model)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def find_cart_item(self, cart_id: int, product_id: int) -> Optional[CartItem]:
        """
        Find a specific item in the cart.
        
        Args:
            cart_id: Cart ID
            product_id: Product ID
            
        Returns:
            CartItem if found, None otherwise
        """
        session = self._session or get_session()
        try:
            item_model = session.query(CartItemModel).filter(
                CartItemModel.cart_id == cart_id,
                CartItemModel.product_id == product_id
            ).first()
            
            if not item_model:
                return None
            
            return CartItem(
                product_id=item_model.product_id,
                quantity=item_model.quantity,
                cart_item_id=item_model.cart_item_id,
                cart_id=item_model.cart_id
            )
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def add_item_to_cart(self, cart_id: int, product_id: int, quantity: int) -> CartItem:
        """
        Add a new item to the cart.
        
        Args:
            cart_id: Cart ID
            product_id: Product ID
            quantity: Quantity to add
            
        Returns:
            Created CartItem
        """
        session = self._session or get_session()
        try:
            item_model = CartItemModel(
                cart_id=cart_id,
                product_id=product_id,
                quantity=quantity
            )
            session.add(item_model)
            session.commit()
            session.refresh(item_model)
            
            return CartItem(
                product_id=item_model.product_id,
                quantity=item_model.quantity,
                cart_item_id=item_model.cart_item_id,
                cart_id=item_model.cart_id
            )
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def update_cart_item_quantity(self, cart_item_id: int, new_quantity: int) -> CartItem:
        """
        Update quantity of a cart item.
        
        Args:
            cart_item_id: Cart item ID
            new_quantity: New quantity
            
        Returns:
            Updated CartItem
        """
        session = self._session or get_session()
        try:
            item_model = session.query(CartItemModel).filter(
                CartItemModel.cart_item_id == cart_item_id
            ).first()
            
            if not item_model:
                raise ValueError(f"Cart item {cart_item_id} not found")
            
            item_model.quantity = new_quantity
            session.commit()
            session.refresh(item_model)
            
            return CartItem(
                product_id=item_model.product_id,
                quantity=item_model.quantity,
                cart_item_id=item_model.cart_item_id,
                cart_id=item_model.cart_id
            )
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def save(self, cart: Cart) -> Cart:
        """
        Save cart (create or update).
        
        Args:
            cart: Cart entity to save
            
        Returns:
            Saved cart entity with updated ID
        """
        session = self._session or get_session()
        try:
            if cart.id is None:
                # Create new cart
                cart_model = self._to_orm_model(cart)
                session.add(cart_model)
                session.flush()  # Get the ID
                cart = self._to_domain_entity(cart_model)
            else:
                # Update existing cart
                cart_model = session.query(CartModel).filter(
                    CartModel.cart_id == cart.id
                ).first()
                
                if not cart_model:
                    raise ValueError(f"Cart with id {cart.id} not found")
                
                self._update_model_from_entity(cart_model, cart, session)
            
            session.commit()
            return cart
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def delete(self, cart_id: int) -> bool:
        """
        Delete cart by ID.
        
        Args:
            cart_id: Cart ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        session = self._session or get_session()
        try:
            cart_model = session.query(CartModel).filter(
                CartModel.cart_id == cart_id
            ).first()
            
            if not cart_model:
                return False
            
            # Delete cart items first (if not cascading)
            session.query(CartItemModel).filter(
                CartItemModel.cart_id == cart_id
            ).delete()
            
            session.delete(cart_model)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def clear_cart(self, customer_id: int) -> bool:
        """
        Clear all items from customer's cart.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            True if cleared, False if cart not found
        """
        session = self._session or get_session()
        try:
            cart_model = session.query(CartModel).filter(
                CartModel.user_id == customer_id
            ).first()
            
            if not cart_model:
                return False
            
            # Delete all cart items
            session.query(CartItemModel).filter(
                CartItemModel.cart_id == cart_model.cart_id
            ).delete()
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def _to_domain_entity(self, cart_model: CartModel) -> Cart:
        """
        Convert ORM model to domain entity.
        
        Args:
            cart_model: CartModel instance
            
        Returns:
            Cart domain entity
        """
        # Convert cart items to domain entities
        cart_items = []
        for item_model in cart_model.items:
            # CartItem constructor: (product_id, quantity, cart_item_id, cart_id)
            cart_item = CartItem(
                product_id=item_model.product_id,
                quantity=item_model.quantity,
                cart_item_id=item_model.cart_item_id,
                cart_id=item_model.cart_id
            )
            cart_items.append(cart_item)
        
        # Reconstruct cart with items
        # Cart.reconstruct(cart_id, customer_id, items, created_at, updated_at)
        return Cart.reconstruct(
            cart_id=cart_model.cart_id,
            customer_id=cart_model.user_id,
            items=cart_items,
            created_at=cart_model.created_at,
            updated_at=cart_model.updated_at
        )
    
    def _to_orm_model(self, cart: Cart) -> CartModel:
        """
        Convert domain entity to ORM model for new entities.
        
        Args:
            cart: Cart domain entity
            
        Returns:
            CartModel instance
        """
        cart_model = CartModel(
            user_id=cart.customer_id,
            created_at=cart.created_at,
            updated_at=cart.updated_at
        )
        
        # Add cart items
        for item in cart.items:
            cart_item_model = CartItemModel(
                product_id=item.product_id,
                quantity=item.quantity
            )
            cart_model.items.append(cart_item_model)
        
        return cart_model
    
    def _update_model_from_entity(self, cart_model: CartModel, cart: Cart, session) -> None:
        """
        Update existing ORM model from domain entity.
        
        Args:
            cart_model: Existing CartModel instance
            cart: Cart domain entity with updates
            session: SQLAlchemy session
        """
        cart_model.updated_at = cart.updated_at
        
        # Update cart items: remove old items and add new ones
        # This is simpler than trying to match and update existing items
        session.query(CartItemModel).filter(
            CartItemModel.cart_id == cart_model.cart_id
        ).delete()
        
        # Add current items
        for item in cart.items:
            cart_item_model = CartItemModel(
                cart_id=cart_model.cart_id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            session.add(cart_item_model)
