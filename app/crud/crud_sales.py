from typing import List, Optional, Tuple
from datetime import date, datetime
from app.core.db import db_cursor
from app.models import schemas
from app.crud import crud_products, crud_inventory # For getting product price and updating inventory

def record_sale(sale_in: schemas.SaleCreate) -> Optional[schemas.Sale]:
    # 1. Get current product price
    product_details = crud_products.get_product_by_id(sale_in.product_id)
    if not product_details:
        raise ValueError(f"Product with ID {sale_in.product_id} not found.")
    
    sale_price = product_details.price # Price at the time of sale

    # 2. Check if enough stock is available
    if product_details.inventory_quantity is None or product_details.inventory_quantity < sale_in.quantity_sold:
        raise ValueError(f"Not enough stock for product {product_details.name}. Available: {product_details.inventory_quantity}, Requested: {sale_in.quantity_sold}")

    sale_query = """
        INSERT INTO sales (product_id, quantity_sold, sale_price_at_time_of_sale, order_id, sale_date)
        VALUES (%s, %s, %s, %s, NOW()) 
    """
    inventory_update_query = """
        UPDATE inventory SET quantity = quantity - %s, last_updated = NOW() 
        WHERE product_id = %s
    """
    inventory_log_query = """
        INSERT INTO inventory_log (product_id, change_in_quantity, reason)
        VALUES (%s, %s, %s)
    """
    
    sale_id = None
    try:
        with db_cursor(commit=True) as cursor:
            # Record sale
            cursor.execute(sale_query, (
                sale_in.product_id, sale_in.quantity_sold, sale_price, sale_in.order_id
            ))
            sale_id = cursor.lastrowid
            if not sale_id:
                raise Exception("Failed to record sale.")

            # Update inventory quantity
            cursor.execute(inventory_update_query, (sale_in.quantity_sold, sale_in.product_id))
            if cursor.rowcount == 0:
                 raise Exception(f"Failed to update inventory for product ID {sale_in.product_id}. Product might not exist in inventory or stock update failed.")

            # Log inventory change
            reason = f"Sale (Order ID: {sale_in.order_id})" if sale_in.order_id else f"Sale (ID: {sale_id})"
            cursor.execute(inventory_log_query, (sale_in.product_id, -sale_in.quantity_sold, reason))
        
        # Fetch the created sale record
        return get_sale_by_id(sale_id)

    except ValueError as ve: # Specific value errors from checks
        print(f"Value error during sale recording: {ve}")
        raise # Re-raise to be caught by FastAPI handler
    except Exception as e:
        print(f"Error recording sale: {e}")
        raise # Re-raise for now
    

def get_sale_by_id(sale_id: int) -> Optional[schemas.Sale]:
    query = """
        SELECT s.id, s.product_id, s.quantity_sold, s.sale_price_at_time_of_sale, s.sale_date, s.order_id,
               p.id as p_id, p.name as p_name, p.description as p_description, 
               p.price as p_price_current, p.category_id as p_category_id,
               p.created_at as p_created_at, p.updated_at as p_updated_at
        FROM sales s
        JOIN products p ON s.product_id = p.id
        WHERE s.id = %s
    """
    with db_cursor() as cursor:
        cursor.execute(query, (sale_id,))
        row = cursor.fetchone()
        if row:
            product_data = schemas.Product(
                id=row['p_id'], name=row['p_name'], description=row['p_description'],
                price=row['p_price_current'], category_id=row['p_category_id'],
                created_at=row['p_created_at'], updated_at=row['p_updated_at']
            )
            return schemas.Sale(
                id=row['id'], product_id=row['product_id'], quantity_sold=row['quantity_sold'],
                sale_price_at_time_of_sale=row['sale_price_at_time_of_sale'],
                sale_date=row['sale_date'], order_id=row['order_id'],
                product=product_data
            )
    return None

def get_sales_data(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    product_id: Optional[int] = None,
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[schemas.Sale]:
    base_query = """
        SELECT s.id, s.product_id, s.quantity_sold, s.sale_price_at_time_of_sale, s.sale_date, s.order_id,
               p.id as p_id, p.name as p_name, p.description as p_description, 
               p.price as p_price_current, p.category_id as p_category_id,
               p.created_at as p_created_at, p.updated_at as p_updated_at,
               c.name as category_name
        FROM sales s
        JOIN products p ON s.product_id = p.id
        LEFT JOIN categories c ON p.category_id = c.id
    """
    conditions = []
    params = []

    if date_from:
        conditions.append("s.sale_date >= %s")
        params.append(datetime.combine(date_from, datetime.min.time()))
    if date_to:
        conditions.append("s.sale_date <= %s")
        params.append(datetime.combine(date_to, datetime.max.time()))
    if product_id:
        conditions.append("s.product_id = %s")
        params.append(product_id)
    if category_id:
        conditions.append("p.category_id = %s")
        params.append(category_id)

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    
    base_query += " ORDER BY s.sale_date DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])

    sales_list = []
    with db_cursor() as cursor:
        cursor.execute(base_query, tuple(params))
        for row in cursor.fetchall():
            product_data = schemas.Product(
                id=row['p_id'], name=row['p_name'], description=row['p_description'],
                price=row['p_price_current'], category_id=row['p_category_id'],
                created_at=row['p_created_at'], updated_at=row['p_updated_at']
                # category detail can be added if Product schema has it and it's fetched
            )
            sales_list.append(schemas.Sale(
                id=row['id'], product_id=row['product_id'], quantity_sold=row['quantity_sold'],
                sale_price_at_time_of_sale=row['sale_price_at_time_of_sale'],
                sale_date=row['sale_date'], order_id=row['order_id'],
                product=product_data
            ))
    return sales_list


def get_revenue_analysis(
    period_type: str, # "daily", "weekly", "monthly", "annual"
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[int] = None
) -> schemas.RevenueReport:
    
    if period_type not in ["daily", "weekly", "monthly", "annual"]:
        raise ValueError("Invalid period_type. Must be 'daily', 'weekly', 'monthly', or 'annual'.")

    date_format_mapping = {
        "daily": "%Y-%m-%d",    # DATE(sale_date)
        "weekly": "%Y-%u",     # YEARWEEK(sale_date, 1)
        "monthly": "%Y-%m",    # DATE_FORMAT(sale_date, '%Y-%m')
        "annual": "%Y"         # YEAR(sale_date)
    }
    group_by_expression_mapping = {
        "daily": "DATE(s.sale_date)",
        "weekly": "YEARWEEK(s.sale_date, 1)", # Mode 1: Sunday is first day, week 1 is first week with a Sunday
        "monthly": "DATE_FORMAT(s.sale_date, '%Y-%m')",
        "annual": "YEAR(s.sale_date)"
    }

    group_by_expression = group_by_expression_mapping[period_type]
    
    query = f"""
        SELECT 
            {group_by_expression} as period,
            SUM(s.quantity_sold * s.sale_price_at_time_of_sale) as total_revenue
        FROM sales s
    """
    conditions = []
    params = []

    if category_id is not None:
        # Need to join with products table if filtering by category
        query += " JOIN products p ON s.product_id = p.id "
        conditions.append("p.category_id = %s")
        params.append(category_id)
    
    if start_date:
        conditions.append("s.sale_date >= %s")
        params.append(datetime.combine(start_date, datetime.min.time()))
    if end_date:
        conditions.append("s.sale_date <= %s")
        params.append(datetime.combine(end_date, datetime.max.time()))

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += f" GROUP BY period ORDER BY period ASC"
    
    revenue_data_points = []
    total_revenue_overall = 0.0
    with db_cursor() as cursor:
        cursor.execute(query, tuple(params))
        for row in cursor.fetchall():
            # MySQL YEARWEEK returns an integer like 202301. Need to format for consistency.
            # For daily, it returns a datetime.date object.
            period_value = row['period']
            if period_type == "weekly" and isinstance(period_value, int):
                year = period_value // 100
                week = period_value % 100
                period_value = f"{year}-W{week:02d}" # e.g. 2023-W01
            elif isinstance(period_value, (date, datetime)):
                 period_value = period_value.isoformat()


            revenue_data_points.append(schemas.RevenueDataPoint(
                period=str(period_value), # Ensure period is string or date
                total_revenue=float(row['total_revenue'])
            ))
            total_revenue_overall += float(row['total_revenue'])
            
    return schemas.RevenueReport(data=revenue_data_points, total_revenue_overall=total_revenue_overall)


def get_revenue_for_period_and_category(
    start_date: date, end_date: date, category_id: Optional[int] = None
) -> Tuple[float, Optional[str]]:
    query = """
        SELECT SUM(s.quantity_sold * s.sale_price_at_time_of_sale) as total_revenue
        FROM sales s
    """
    conditions = ["s.sale_date >= %s", "s.sale_date <= %s"]
    params = [
        datetime.combine(start_date, datetime.min.time()), 
        datetime.combine(end_date, datetime.max.time())
    ]
    category_name = "All Categories"

    if category_id is not None:
        query += " JOIN products p ON s.product_id = p.id LEFT JOIN categories cat ON p.category_id = cat.id"
        conditions.append("p.category_id = %s")
        params.append(category_id)
        # Fetch category name for reporting
        cat_name_query = "SELECT name FROM categories WHERE id = %s"
        with db_cursor() as cat_cursor:
            cat_cursor.execute(cat_name_query, (category_id,))
            cat_row = cat_cursor.fetchone()
            if cat_row:
                category_name = cat_row['name']
            else:
                category_name = f"Category ID {category_id} (Not Found)"


    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    with db_cursor() as cursor:
        cursor.execute(query, tuple(params))
        result = cursor.fetchone()
        revenue = float(result['total_revenue']) if result and result['total_revenue'] is not None else 0.0
        return revenue, category_name


def compare_revenue(comparison_request: schemas.RevenueComparisonRequest) -> schemas.RevenueComparisonResponse:
    revenue_a, cat_a_name = get_revenue_for_period_and_category(
        comparison_request.period_a_start,
        comparison_request.period_a_end,
        comparison_request.category_id_a
    )
    revenue_b, cat_b_name = get_revenue_for_period_and_category(
        comparison_request.period_b_start,
        comparison_request.period_b_end,
        comparison_request.category_id_b
    )

    return schemas.RevenueComparisonResponse(comparison=[
        schemas.RevenueComparisonData(period="Period A", category_name=cat_a_name, total_revenue=revenue_a),
        schemas.RevenueComparisonData(period="Period B", category_name=cat_b_name, total_revenue=revenue_b)
    ])
