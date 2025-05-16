from typing import List, Optional
from app.core.db import db_cursor
from app.models import schemas

def get_inventory_by_product_id(product_id: int) -> Optional[schemas.Inventory]:
    query = """
        SELECT i.id, i.product_id, i.quantity, i.low_stock_threshold, i.last_updated,
               p.name as product_name, p.description as product_description, p.price as product_price,
               p.category_id as product_category_id
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        WHERE i.product_id = %s
    """
    with db_cursor() as cursor:
        cursor.execute(query, (product_id,))
        row = cursor.fetchone()
        if row:
            product_data = schemas.Product(
                id=row['product_id'], name=row['product_name'], description=row['product_description'],
                price=row['product_price'], category_id=row['product_category_id'],
                # Dummy values for created_at, updated_at as they are not primary in this context
                created_at=row['last_updated'], updated_at=row['last_updated'] 
            )
            return schemas.Inventory(
                id=row['id'], product_id=row['product_id'], quantity=row['quantity'],
                low_stock_threshold=row['low_stock_threshold'], last_updated=row['last_updated'],
                product=product_data
            )
    return None

def update_inventory(product_id: int, inventory_update: schemas.InventoryUpdate) -> Optional[schemas.Inventory]:
    current_inventory = get_inventory_by_product_id(product_id)
    if not current_inventory:
        return None

    update_fields = inventory_update.dict(exclude_unset=True)
    if not update_fields:
        return current_inventory

    set_clauses = []
    params = []
    for key, value in update_fields.items():
        set_clauses.append(f"{key} = %s")
        params.append(value)
    
    params.append(product_id)
    query = f"UPDATE inventory SET {', '.join(set_clauses)}, last_updated=NOW() WHERE product_id = %s"
    
    try:
        with db_cursor(commit=True) as cursor:
            cursor.execute(query, tuple(params))

        return get_inventory_by_product_id(product_id)
    except Exception as e:
        print(f"Error updating inventory for product {product_id}: {e}")
        return None

def get_all_inventory_status(skip: int = 0, limit: int = 100) -> List[schemas.Inventory]:
    query = """
        SELECT i.id, i.product_id, i.quantity, i.low_stock_threshold, i.last_updated,
               p.id as p_id, p.name as p_name, p.description as p_description, 
               p.price as p_price, p.category_id as p_category_id,
               p.created_at as p_created_at, p.updated_at as p_updated_at
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        ORDER BY p.name
        LIMIT %s OFFSET %s
    """
    inventory_list = []
    with db_cursor() as cursor:
        cursor.execute(query, (limit, skip))
        for row in cursor.fetchall():
            product_data = schemas.Product(
                id=row['p_id'], name=row['p_name'], description=row['p_description'],
                price=row['p_price'], category_id=row['p_category_id'],
                created_at=row['p_created_at'], updated_at=row['p_updated_at']
            )
            inventory_list.append(schemas.Inventory(
                id=row['id'], product_id=row['product_id'], quantity=row['quantity'],
                low_stock_threshold=row['low_stock_threshold'], last_updated=row['last_updated'],
                product=product_data
            ))
    return inventory_list


def get_low_stock_alerts() -> List[schemas.LowStockProduct]:
    query = """
        SELECT p.id as product_id, p.name as product_name, 
               i.quantity as current_quantity, i.low_stock_threshold
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        WHERE i.quantity <= i.low_stock_threshold
        ORDER BY (i.quantity - i.low_stock_threshold) ASC -- Show most critical first
    """
    low_stock_items = []
    with db_cursor() as cursor:
        cursor.execute(query)
        for row in cursor.fetchall():
            low_stock_items.append(schemas.LowStockProduct(**row))
    return low_stock_items