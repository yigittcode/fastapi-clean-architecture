from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories.item import ItemRepository
from ..models.item import Item
from ..models.user import User
from ..schemas.item import ItemCreate, ItemUpdate, Item as ItemSchema


class ItemsService:
    """Items business logic"""
    
    def __init__(self, item_repository: ItemRepository):
        self.item_repository = item_repository
    
    async def get_items(
        self,
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ItemSchema]:
        """Get all items with owner info"""
        return await self.item_repository.get_all_with_owners(db, skip=skip, limit=limit)
    
    async def get_items_without_owner(
        self,
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ItemSchema]:
        """Get all items without owner info - more efficient"""
        return await self.item_repository.get_all_without_owners(db, skip=skip, limit=limit)
    
    async def get_user_items(self, db: AsyncSession, current_user: User) -> List[ItemSchema]:
        """Get current user's items with owner info"""
        return await self.item_repository.get_user_items(db, current_user.id)
    
    async def get_user_items_without_owner(self, db: AsyncSession, current_user: User) -> List[ItemSchema]:
        """Get current user's items without owner info - more efficient"""
        return await self.item_repository.get_user_items(db, current_user.id)
    
    async def get_item_by_id(self, db: AsyncSession, item_id: int) -> ItemSchema:
        """Get item by ID"""
        item = await self.item_repository.get_with_owner(db, item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        return item
    
    async def create_item(
        self,
        db: AsyncSession, 
        item_data: ItemCreate, 
        current_user: User
    ) -> ItemSchema:
        """Create new item"""
        return await self.item_repository.create_item(db, item_data, current_user.id)
    
    async def update_item(
        self,
        db: AsyncSession, 
        item_id: int, 
        item_data: ItemUpdate, 
        current_user: User
    ) -> ItemSchema:
        """Update item (owner only)"""
        item = await self.item_repository.get(db, item_id)
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
        
        return await self.item_repository.update(db, item, item_data)
    
    async def delete_item(
        self,
        db: AsyncSession, 
        item_id: int, 
        current_user: User
    ) -> None:
        """Delete item (owner only)"""
        item = await self.item_repository.get(db, item_id)
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
        
        await self.item_repository.delete(db, item_id)


