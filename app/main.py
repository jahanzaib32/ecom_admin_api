from fastapi import FastAPI, HTTPException
from app.api.api_v1 import api_router
from app.core import config # To use API_V1_STR

app = FastAPI(
    title="E-commerce Admin API",
    description="API for managing e-commerce sales, revenue, and inventory.",
    version="1.0.0"
)

@app.exception_handler(ConnectionError)
async def db_connection_exception_handler(request, exc):
    return HTTPException(
        status_code=503, # Service Unavailable
        detail="Database connection error. Please try again later."
    )


app.include_router(api_router, prefix=config.API_V1_STR)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the E-commerce Admin API. Docs at /docs"}