from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories.item import item_repository
from ..models.item import Item
from ..models.user import User
from ..schemas.item import ItemCreate, ItemUpdate


class ItemsService:
    """Items business logic"""
    
    @staticmethod
    async def get_items(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Item]:
        """Get all items with owner info"""
        return await item_repository.get_all_with_owners(db, skip=skip, limit=limit)
    
    @staticmethod
    async def get_items_without_owner(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Item]:
        """Get all items without owner info - more efficient"""
        return await item_repository.get_all_without_owners(db, skip=skip, limit=limit)
    
    @staticmethod
    async def get_user_items(db: AsyncSession, current_user: User) -> List[Item]:
        """Get current user's items with owner info"""
        return await item_repository.get_user_items(db, current_user.id)
    
    @staticmethod
    async def get_user_items_without_owner(db: AsyncSession, current_user: User) -> List[Item]:
        """Get current user's items without owner info - more efficient"""
        return await item_repository.get_user_items(db, current_user.id)
    
    @staticmethod
    async def get_item_by_id(db: AsyncSession, item_id: int) -> Item:
        """Get item by ID"""
        item = await item_repository.get_with_owner(db, item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        return item
    
    @staticmethod
    async def create_item(
        db: AsyncSession, 
        item_data: ItemCreate, 
        current_user: User
    ) -> Item:
        """Create new item"""
        return await item_repository.create_item(db, item_data, current_user.id)
    
    @staticmethod
    async def update_item(
        db: AsyncSession, 
        item_id: int, 
        item_data: ItemUpdate, 
        current_user: User
    ) -> Item:
        """Update item (owner only)"""
        item = await item_repository.get(db, item_id)
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
        
        return await item_repository.update(db, item, item_data)
    
    @staticmethod
    async def delete_item(
        db: AsyncSession, 
        item_id: int, 
        current_user: User
    ) -> dict:
        """Delete item (owner only)"""
        item = await item_repository.get(db, item_id)
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
        
        await item_repository.delete(db, item_id)
        return {"message": "Item deleted successfully"}
