from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime, date

# --- Category Schemas ---
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Product Schemas ---
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category_id: Optional[int] = None

class ProductCreate(ProductBase):
    initial_quantity: int = Field(0, ge=0)
    low_stock_threshold: Optional[int] = Field(10, ge=0)

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[Category] = None # To show category details if joined

    class Config:
        from_attributes = True

class ProductWithInventory(Product):
    inventory_quantity: Optional[int] = None
    low_stock_threshold: Optional[int] = None


# --- Inventory Schemas ---
class InventoryBase(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=0)
    low_stock_threshold: int = Field(10, ge=0)

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)

class Inventory(InventoryBase):
    id: int
    last_updated: datetime
    product: Optional[Product] = None # To show product details

    class Config:
        from_attributes = True

class LowStockProduct(BaseModel):
    product_id: int
    product_name: str
    current_quantity: int
    low_stock_threshold: int

# --- Sale Schemas ---
class SaleBase(BaseModel):
    product_id: int
    quantity_sold: int = Field(..., gt=0)
    order_id: Optional[str] = None

class SaleCreate(SaleBase):
    pass

class Sale(SaleBase):
    id: int
    sale_price_at_time_of_sale: float
    sale_date: datetime
    product: Optional[Product] = None # To show product details

    class Config:
        from_attributes = True

# --- Revenue Schemas ---
class RevenueDataPoint(BaseModel):
    period: Union[date, str]
    total_revenue: float

class RevenueReport(BaseModel):
    data: List[RevenueDataPoint]
    total_revenue_overall: float

class RevenueComparisonRequest(BaseModel):
    period_a_start: date
    period_a_end: date
    period_b_start: date
    period_b_end: date
    category_id_a: Optional[int] = None
    category_id_b: Optional[int] = None

class RevenueComparisonData(BaseModel):
    period: str # "Period A" or "Period B"
    category_name: Optional[str] = "All"
    total_revenue: float

class RevenueComparisonResponse(BaseModel):
    comparison: List[RevenueComparisonData]
