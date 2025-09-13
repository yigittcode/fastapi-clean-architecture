from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload, joinedload

from .base import BaseRepository
from ..models.item import Item
from ..schemas.item import ItemCreate, ItemUpdate


class ItemRepository(BaseRepository[Item, ItemCreate, ItemUpdate]):
    """Item repository with specialized queries"""
    
    def __init__(self):
        super().__init__(Item)
    
    async def get_with_owner(self, db: AsyncSession, item_id: int) -> Optional[Item]:
        """Get item with owner information"""
        result = await db.execute(
            select(Item)
            .options(joinedload(Item.owner))
            .where(Item.id == item_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_with_owners(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Item]:
        """Get all items with owner information"""
        result = await db.execute(
            select(Item)
            .options(joinedload(Item.owner))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().unique().all()
    
    async def get_all_without_owners(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Item]:
        """Get all items without owner information (more efficient)"""
        result = await db.execute(
            select(Item)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_user_items(
        self, 
        db: AsyncSession, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Item]:
        """Get items belonging to a specific user"""
        result = await db.execute(
            select(Item)
            .where(Item.owner_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_active_items(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Item]:
        """Get all active items"""
        result = await db.execute(
            select(Item)
            .where(Item.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search_items(
        self, 
        db: AsyncSession, 
        query: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Item]:
        """Search items by title or description"""
        search_filter = f"%{query}%"
        result = await db.execute(
            select(Item)
            .where(
                and_(
                    Item.is_active == True,
                    (Item.title.ilike(search_filter) | Item.description.ilike(search_filter))
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create_item(self, db: AsyncSession, item_data: ItemCreate, owner_id: int) -> Item:
        """Create item with owner"""
        item_dict = item_data.dict()
        item_dict["owner_id"] = owner_id
        
        db_item = Item(**item_dict)
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item
    
    async def get_user_item_count(self, db: AsyncSession, user_id: int) -> int:
        """Get count of items for a specific user"""
        from sqlalchemy import func
        result = await db.execute(
            select(func.count(Item.id)).where(Item.owner_id == user_id)
        )
        return result.scalar()


# Singleton instance removed - now using dependency injection through deps.py
