# E-commerce Admin API

This API provides backend services for an e-commerce admin dashboard, allowing managers to track sales, revenue, inventory, and register new products.

## Features

*   **Product Management:**
    *   Register new products with initial inventory.
    *   View and filter product listings.
    *   Update product details.
*   **Inventory Management:**
    *   View current inventory status for all products.
    *   Update inventory levels manually.
    *   Get alerts for low-stock items.
    *   (Implicitly) Inventory updated upon sales.
*   **Sales & Revenue Analysis:**
    *   Record new sales.
    *   Retrieve sales data with filters (date range, product, category).
    *   Analyze revenue on daily, weekly, monthly, and annual bases.
    *   Compare revenue across different periods and/or categories.

## API Endpoints Overview

The API provides the following main groups of endpoints, all prefixed with `/api/v1`:

*   **`/products`**:
    *   `POST /` : Register a new product along with its initial inventory.
    *   `GET /` : Retrieve a list of all products, with optional filtering by category or name.
    *   `GET /{product_id}` : Retrieve details for a specific product.
    *   `PUT /{product_id}` : Update details for an existing product.
    *   `POST /categories/` : Create a new product category.
    *   `GET /categories/` : Retrieve a list of all product categories.

*   **`/inventory`**:
    *   `GET /` : Retrieve the current inventory status for all products.
    *   `GET /low-stock` : Get a list of products that are below their low stock threshold.
    *   `GET /{product_id}` : Retrieve inventory details for a specific product.
    *   `PUT /{product_id}` : Update the inventory level (quantity, low stock threshold) for a specific product.

*   **`/sales`**:
    *   `POST /` : Record a new sale, which also updates product inventory.
    *   `GET /` : Retrieve a list of sales, filterable by date range, product, or category.
    *   `GET /revenue/analysis` : Analyze revenue on a daily, weekly, monthly, or annual basis, with optional date range and category filters.
    *   `POST /revenue/comparison` : Compare revenue totals between two different periods and/or categories.

For detailed request/response schemas and parameters, please refer to the auto-generated API documentation available at `/docs` (e.g., `http://127.0.0.1:8000/api/v1/docs`) when the server is running.

## Tech Stack

*   Programming Language & Framework: Python with FastAPI
*   API Type: RESTful
*   Database: MySQL
*   Pydantic
*   Uvicorn

## Setup Instructions

1.  **Prerequisites:**
    *   Python 3.8+
    *   MySQL Server installed and running.

2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/jahanzaib32/ecom_admin_api.git
    cd ecom_admin_api
    ```

3.  **Create and Activate Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt 
    ```

5.  **Database Setup:**
    *   Connect to your MySQL instance.
    *   Create the database and a dedicated user:
        ```sql
        CREATE DATABASE ecom_admin_db;
        CREATE USER 'ecom_user'@'localhost' IDENTIFIED BY 'your_strong_password'; -- Choose a strong password
        GRANT ALL PRIVILEGES ON ecom_admin_db.* TO 'ecom_user'@'localhost';
        FLUSH PRIVILEGES;
        ```
    *   Run the schema script to create tables:
        ```bash
        mysql -u ecom_user -p ecom_admin_db < sql/schema.sql 
        ```
    *   Populate with demo data:
        ```bash
        mysql -u ecom_user -p ecom_admin_db < sql/demo_data.sql
        ```

6.  **Environment Variables:**
    *   Copy `.env.example` to `.env`:
        ```bash
        cp .env.example .env
        ```
    *   Edit `.env` and fill in your MySQL database credentials:
        ```
        DB_HOST=localhost
        DB_USER=ecom_user
        DB_PASSWORD=your_strong_password
        DB_NAME=ecom_admin_db
        ```

7.  **Run the API Server:**
    From the project root directory (`ecom_admin_api/`):
    ```bash
    uvicorn app.main:app --reload
    ```
    The API docs will be available at `http://127.0.0.1:8000/docs`.

## Database Schema Documentation

The database `ecom_admin_db` consists of the following tables:

1.  **`categories`**
    *   Stores product categories.
    *   `id` (INT, PK, AI): Unique identifier for the category.
    *   `name` (VARCHAR(255), NOT NULL, UNIQUE): Name of the category.
    *   `created_at` (TIMESTAMP): When the category was created.

2.  **`products`**
    *   Stores information about individual products.
    *   `id` (INT, PK, AI): Unique identifier for the product.
    *   `name` (VARCHAR(255), NOT NULL): Name of the product.
    *   `description` (TEXT): Detailed description of the product.
    *   `price` (DECIMAL(10,2), NOT NULL): Current selling price of the product.
    *   `category_id` (INT, FK): Foreign key referencing `categories.id`. Can be NULL if product is uncategorized.
    *   `created_at` (TIMESTAMP): When the product was registered.
    *   `updated_at` (TIMESTAMP): When the product details were last updated.
    *   *Indexes:* `idx_product_name` (on `name`), `idx_product_category` (on `category_id`).

3.  **`inventory`**
    *   Tracks the stock levels for each product.
    *   `id` (INT, PK, AI): Unique identifier for the inventory record.
    *   `product_id` (INT, NOT NULL, UNIQUE, FK): Foreign key referencing `products.id`. Ensures one inventory record per product. `ON DELETE CASCADE`.
    *   `quantity` (INT, NOT NULL): Current number of units in stock.
    *   `low_stock_threshold` (INT, NOT NULL): Threshold below which the product is considered "low stock".
    *   `last_updated` (TIMESTAMP): When the inventory for this product was last modified.
    *   *Indexes:* `idx_inventory_product` (on `product_id`).

4.  **`sales`**
    *   Records each sale transaction.
    *   `id` (INT, PK, AI): Unique identifier for the sale record.
    *   `product_id` (INT, NOT NULL, FK): Foreign key referencing `products.id`. `ON DELETE RESTRICT` (prevents deleting product if sales exist).
    *   `quantity_sold` (INT, NOT NULL): Number of units of the product sold in this transaction.
    *   `sale_price_at_time_of_sale` (DECIMAL(10,2), NOT NULL): The price of one unit of the product at the moment the sale was made.
    *   `sale_date` (TIMESTAMP): Timestamp of when the sale occurred.
    *   `order_id` (VARCHAR(255), NULL): Optional identifier to group multiple sale items into a single customer order.
    *   *Indexes:* `idx_sales_product` (on `product_id`), `idx_sales_date` (on `sale_date`), `idx_sales_order_id` (on `order_id`).


**Relationships:**
*   A `Product` belongs to one `Category` (or none). A `Category` can have many `Products`.
*   Each `Product` has one `Inventory` record.
*   A `Product` can be part of many `Sales` records. Each `Sale` record pertains to one `Product`.
*   An `InventoryLog` entry is associated with one `Product`. A `Product` can have many `InventoryLog` entries.

---