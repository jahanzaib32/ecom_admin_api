from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import List, Optional
from app.crud import crud_products
from app.crud import crud_categories
from app.models import schemas

router = APIRouter()

@router.post("/", response_model=schemas.ProductWithInventory, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(product_in: schemas.ProductCreate):
    if product_in.category_id and not crud_categories.get_category_by_id(product_in.category_id):
        raise HTTPException(status_code=404, detail=f"Category with id {product_in.category_id} not found")
    
    product = crud_products.create_product(product_in=product_in)
    if not product:
        raise HTTPException(status_code=400, detail="Product could not be created.")
    return product

@router.get("/{product_id}", response_model=schemas.ProductWithInventory)
def read_product_endpoint(product_id: int):
    product = crud_products.get_product_by_id(product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/", response_model=List[schemas.ProductWithInventory])
def read_products_endpoint(
    skip: int = 0, 
    limit: int = Query(default=100, le=200), # Max limit 200
    category_id: Optional[int] = None,
    name: Optional[str] = None
):
    products = crud_products.get_all_products(
        skip=skip, limit=limit, category_id=category_id, name_filter=name
    )
    return products

@router.put("/{product_id}", response_model=schemas.ProductWithInventory)
def update_product_endpoint(product_id: int, product_in: schemas.ProductUpdate):
    updated_product = crud_products.update_product(product_id=product_id, product_update=product_in)
    if updated_product is None:
        raise HTTPException(status_code=404, detail="Product not found or update failed")
    return updated_product

@router.post("/categories/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED, tags=["Categories"])
def create_category_endpoint(category_in: schemas.CategoryCreate):
    category = crud_categories.create_category(category=category_in)
    if not category:
        raise HTTPException(status_code=400, detail="Category could not be created, name might exist.")
    return category

@router.get("/categories/", response_model=List[schemas.Category], tags=["Categories"])
def read_categories_endpoint(skip: int = 0, limit: int = 100):
    return crud_categories.get_all_categories(skip=skip, limit=limit)