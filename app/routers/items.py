from typing import List
from fastapi import APIRouter, status, Query
from ..core.deps import DatabaseDep, ActiveUserDep, LoggerDep
from ..controllers.items import ItemsController
from ..schemas.item import Item as ItemSchema, ItemWithOwner, ItemCreate, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemSchema, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    db: DatabaseDep,
    logger: LoggerDep,
    current_user: ActiveUserDep
):
    """Create new item"""
    logger.info("Creating new item", title=item.title, user_id=current_user.id)
    return await ItemsController.create_item(db, item, current_user)


@router.get("/", response_model=List[ItemWithOwner])
async def read_items(
    db: DatabaseDep,
    logger: LoggerDep,
    skip: int = 0,
    limit: int = 100,
    include_owner: bool = Query(True, description="Include owner information")
):
    """Get all items with optional owner info"""
    logger.info("Fetching items list", skip=skip, limit=limit, include_owner=include_owner)
    
    if include_owner:
        items = await ItemsController.get_items(db, skip, limit)
        # Map to ItemWithOwner schema
        result = []
        for item in items:
            item_data = ItemWithOwner(
                id=item.id,
                title=item.title,
                description=item.description,
                is_active=item.is_active,
                owner_id=item.owner_id,
                created_at=item.created_at,
                updated_at=item.updated_at,
                owner_username=item.owner.username if item.owner else None,
                owner_email=item.owner.email if item.owner else None
            )
            result.append(item_data)
        return result
    else:
        # Return basic items without owner info
        items = await ItemsController.get_items_without_owner(db, skip, limit)
        return [ItemSchema.from_orm(item) for item in items]


@router.get("/my/", response_model=List[ItemSchema])
async def read_my_items(
    db: DatabaseDep,
    logger: LoggerDep,
    current_user: ActiveUserDep
):
    """Get current user's items - no owner info needed since it's always current user"""
    logger.info("Fetching user items", user_id=current_user.id)
    items = await ItemsController.get_user_items_without_owner(db, current_user)
    return items


@router.get("/{item_id}", response_model=ItemSchema)
async def read_item(
    item_id: int,
    db: DatabaseDep,
    logger: LoggerDep
):
    """Get item by ID"""
    logger.info("Fetching item by ID", item_id=item_id)
    return await ItemsController.get_item_by_id(db, item_id)


@router.put("/{item_id}", response_model=ItemSchema)
async def update_item(
    item_id: int,
    item_update: ItemUpdate,
    db: DatabaseDep,
    logger: LoggerDep,
    current_user: ActiveUserDep
):
    """Update item (Owner only)"""
    logger.info("Updating item", item_id=item_id, user_id=current_user.id)
    return await ItemsController.update_item(db, item_id, item_update, current_user)


@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    db: DatabaseDep,
    logger: LoggerDep,
    current_user: ActiveUserDep
):
    """Delete item (Owner only)"""
    logger.info("Deleting item", item_id=item_id, user_id=current_user.id)
    return await ItemsController.delete_item(db, item_id, current_user)