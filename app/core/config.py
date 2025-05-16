# app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv() # Load variables from .env file

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "ecom_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_strong_password")
DB_NAME = os.getenv("DB_NAME", "ecom_admin_db")

# You can add other configurations here
API_V1_STR = "/api/v1"