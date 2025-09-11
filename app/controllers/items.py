from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from ..models.item import Item
from ..models.user import User
from ..schemas.item import ItemCreate, ItemUpdate


class ItemsController:
    """Items business logic"""
    
    @staticmethod
    async def get_items(
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Item]:
        """Get all items with owner info"""
        return db.query(Item).options(joinedload(Item.owner)).offset(skip).limit(limit).all()
    
    @staticmethod
    async def get_items_without_owner(
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Item]:
        """Get all items without owner info - more efficient"""
        return db.query(Item).offset(skip).limit(limit).all()
    
    @staticmethod
    async def get_user_items(db: Session, current_user: User) -> List[Item]:
        """Get current user's items with owner info"""
        return db.query(Item).options(joinedload(Item.owner)).filter(Item.owner_id == current_user.id).all()
    
    @staticmethod
    async def get_user_items_without_owner(db: Session, current_user: User) -> List[Item]:
        """Get current user's items without owner info - more efficient"""
        return db.query(Item).filter(Item.owner_id == current_user.id).all()
    
    @staticmethod
    async def get_item_by_id(db: Session, item_id: int) -> Item:
        """Get item by ID"""
        item = db.query(Item).options(joinedload(Item.owner)).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        return item
    
    @staticmethod
    async def create_item(
        db: Session, 
        item_data: ItemCreate, 
        current_user: User
    ) -> Item:
        """Create new item"""
        db_item = Item(
            title=item_data.title,
            description=item_data.description,
            owner_id=current_user.id
        )
        
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        return db_item
    
    @staticmethod
    async def update_item(
        db: Session, 
        item_id: int, 
        item_data: ItemUpdate, 
        current_user: User
    ) -> Item:
        """Update item (owner only)"""
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        # Only owner or superuser can update
        if item.owner_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Update fields
        update_data = item_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        
        db.commit()
        db.refresh(item)
        
        return item
    
    @staticmethod
    async def delete_item(
        db: Session, 
        item_id: int, 
        current_user: User
    ) -> dict:
        """Delete item (owner only)"""
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        # Only owner or superuser can delete
        if item.owner_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        db.delete(item)
        db.commit()
        
        return {"message": "Item deleted successfully"}
