from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from app.crud import crud_inventory
from app.models import schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.Inventory])
def read_all_inventory_status(skip: int = 0, limit: int = Query(default=100, le=200)):
    inventory_list = crud_inventory.get_all_inventory_status(skip=skip, limit=limit)
    return inventory_list

@router.get("/low-stock", response_model=List[schemas.LowStockProduct])
def get_low_stock_alerts_endpoint():
    low_stock_items = crud_inventory.get_low_stock_alerts()
    return low_stock_items

@router.get("/{product_id}", response_model=schemas.Inventory)
def read_inventory_for_product(product_id: int):
    inventory_item = crud_inventory.get_inventory_by_product_id(product_id=product_id)
    if inventory_item is None:
        raise HTTPException(status_code=404, detail=f"Inventory for product ID {product_id} not found")
    return inventory_item

@router.put("/{product_id}", response_model=schemas.Inventory)
def update_inventory_for_product(product_id: int, inventory_in: schemas.InventoryUpdate):
    updated_inventory = crud_inventory.update_inventory(product_id=product_id, inventory_update=inventory_in)
    if updated_inventory is None:
        raise HTTPException(status_code=404, detail=f"Inventory for product ID {product_id} not found or update failed")
    return updated_inventory
