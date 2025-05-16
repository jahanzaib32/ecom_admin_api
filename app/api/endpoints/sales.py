from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import List, Optional
from datetime import date
from app.crud import crud_sales
from app.models import schemas

router = APIRouter()

@router.post("/", response_model=schemas.Sale, status_code=status.HTTP_201_CREATED)
def record_new_sale(sale_in: schemas.SaleCreate):
    try:
        sale = crud_sales.record_sale(sale_in=sale_in)
        if not sale:
            raise HTTPException(status_code=500, detail="Sale could not be recorded.")
        return sale
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Unexpected error recording sale: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while recording the sale.")


@router.get("/", response_model=List[schemas.Sale])
def get_sales_list(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    product_id: Optional[int] = None,
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = Query(default=100, le=200)
):
    sales = crud_sales.get_sales_data(
        date_from=date_from, date_to=date_to,
        product_id=product_id, category_id=category_id,
        skip=skip, limit=limit
    )
    return sales

@router.get("/revenue/analysis", response_model=schemas.RevenueReport)
def get_revenue_analysis_endpoint(
    period_type: str = Query(..., enum=["daily", "weekly", "monthly", "annual"]),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[int] = None
):
    try:
        report = crud_sales.get_revenue_analysis(
            period_type=period_type,
            start_date=start_date,
            end_date=end_date,
            category_id=category_id
        )
        return report
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in revenue analysis: {e}")
        raise HTTPException(status_code=500, detail="Error generating revenue report.")


@router.post("/revenue/comparison", response_model=schemas.RevenueComparisonResponse)
def compare_revenue_endpoint(comparison_request: schemas.RevenueComparisonRequest):
    try:
        response = crud_sales.compare_revenue(comparison_request)
        return response
    except Exception as e:
        print(f"Error in revenue comparison: {e}")
        raise HTTPException(status_code=500, detail="Error generating revenue comparison.")
