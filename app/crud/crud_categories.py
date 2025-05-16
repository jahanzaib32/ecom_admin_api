from typing import List, Optional
from app.core.db import db_cursor
from app.models.schemas import CategoryCreate, Category

def create_category(category: CategoryCreate) -> Optional[Category]:
    query = "INSERT INTO categories (name) VALUES (%s)"
    try:
        with db_cursor(commit=True) as cursor:
            cursor.execute(query, (category.name,))
            category_id = cursor.lastrowid
            # Fetch the created category to return it
            cursor.execute("SELECT id, name, created_at FROM categories WHERE id = %s", (category_id,))
            created_cat_data = cursor.fetchone()
            if created_cat_data:
                return Category(**created_cat_data)
        return None # Should not happen if insert was successful and commit True
    except Exception as e:
        print(f"Error creating category: {e}") # Log error
        return None # Or raise a custom exception

def get_category_by_id(category_id: int) -> Optional[Category]:
    query = "SELECT id, name, created_at FROM categories WHERE id = %s"
    with db_cursor() as cursor:
        cursor.execute(query, (category_id,))
        category_data = cursor.fetchone()
        return Category(**category_data) if category_data else None

def get_all_categories(skip: int = 0, limit: int = 100) -> List[Category]:
    query = "SELECT id, name, created_at FROM categories ORDER BY name LIMIT %s OFFSET %s"
    categories = []
    with db_cursor() as cursor:
        cursor.execute(query, (limit, skip))
        for row in cursor.fetchall():
            categories.append(Category(**row))
    return categories
