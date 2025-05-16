from typing import List, Optional
from app.core.db import db_cursor
from app.models import schemas

def create_product(product_in: schemas.ProductCreate) -> Optional[schemas.ProductWithInventory]:
    
    product_query = """
        INSERT INTO products (name, description, price, category_id)
        VALUES (%s, %s, %s, %s)
    """
    inventory_query = """
        INSERT INTO inventory (product_id, quantity, low_stock_threshold)
        VALUES (%s, %s, %s)
    """
    
    product_id = None
    try:
        with db_cursor(commit=True) as cursor:
            # Insert product
            cursor.execute(product_query, (
                product_in.name, product_in.description, product_in.price, product_in.category_id
            ))
            product_id = cursor.lastrowid
            if not product_id:
                raise Exception("Failed to create product, no ID returned.")

            # Insert initial inventory
            cursor.execute(inventory_query, (
                product_id, product_in.initial_quantity, product_in.low_stock_threshold
            ))
        
        # Fetch the created product with its inventory details
        return get_product_by_id(product_id)

    except Exception as e:
        print(f"Error creating product and inventory: {e}")
        return None


def get_product_by_id(product_id: int) -> Optional[schemas.ProductWithInventory]:
    query = """
        SELECT p.id, p.name, p.description, p.price, p.category_id, p.created_at, p.updated_at,
               c.id as cat_id, c.name as cat_name, c.created_at as cat_created_at,
               i.quantity as inventory_quantity, i.low_stock_threshold
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN inventory i ON p.id = i.product_id
        WHERE p.id = %s
    """
    with db_cursor() as cursor:
        cursor.execute(query, (product_id,))
        row = cursor.fetchone()
        if row:
            category_data = None
            if row['cat_id']:
                category_data = schemas.Category(id=row['cat_id'], name=row['cat_name'], created_at=row['cat_created_at'])
            
            return schemas.ProductWithInventory(
                id=row['id'], name=row['name'], description=row['description'],
                price=row['price'], category_id=row['category_id'],
                created_at=row['created_at'], updated_at=row['updated_at'],
                category=category_data,
                inventory_quantity=row['inventory_quantity'],
                low_stock_threshold=row['low_stock_threshold']
            )
    return None

def get_all_products(
    skip: int = 0, limit: int = 100, 
    category_id: Optional[int] = None, 
    name_filter: Optional[str] = None
) -> List[schemas.ProductWithInventory]:
    base_query = """
        SELECT p.id, p.name, p.description, p.price, p.category_id, p.created_at, p.updated_at,
               c.id as cat_id, c.name as cat_name, c.created_at as cat_created_at,
               i.quantity as inventory_quantity, i.low_stock_threshold
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN inventory i ON p.id = i.product_id
    """
    conditions = []
    params = []

    if category_id is not None:
        conditions.append("p.category_id = %s")
        params.append(category_id)
    if name_filter:
        conditions.append("p.name LIKE %s")
        params.append(f"%{name_filter}%")

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    
    base_query += " ORDER BY p.name LIMIT %s OFFSET %s"
    params.extend([limit, skip])

    products_list = []
    with db_cursor() as cursor:
        cursor.execute(base_query, tuple(params))
        for row in cursor.fetchall():
            category_data = None
            if row['cat_id']:
                category_data = schemas.Category(id=row['cat_id'], name=row['cat_name'], created_at=row['cat_created_at'])
            
            products_list.append(
                schemas.ProductWithInventory(
                    id=row['id'], name=row['name'], description=row['description'],
                    price=row['price'], category_id=row['category_id'],
                    created_at=row['created_at'], updated_at=row['updated_at'],
                    category=category_data,
                    inventory_quantity=row['inventory_quantity'],
                    low_stock_threshold=row['low_stock_threshold']
                )
            )
    return products_list

def update_product(product_id: int, product_update: schemas.ProductUpdate) -> Optional[schemas.ProductWithInventory]:
    # Fetch current product data to only update provided fields
    current_product = get_product_by_id(product_id)
    if not current_product:
        return None

    update_fields = product_update.dict(exclude_unset=True)
    if not update_fields:
        return current_product # No changes to make

    set_clauses = []
    params = []
    for key, value in update_fields.items():
        set_clauses.append(f"{key} = %s")
        params.append(value)
    
    if not set_clauses: # Should be caught by "if not update_fields"
        return current_product

    params.append(product_id)
    query = f"UPDATE products SET {', '.join(set_clauses)} WHERE id = %s"
    
    try:
        with db_cursor(commit=True) as cursor:
            cursor.execute(query, tuple(params))
            if cursor.rowcount == 0: # No rows updated, possibly product_id not found (though checked above)
                return None
        return get_product_by_id(product_id) # Fetch updated product
    except Exception as e:
        print(f"Error updating product {product_id}: {e}")
        return None