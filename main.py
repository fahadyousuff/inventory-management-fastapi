from fastapi import FastAPI
from routers import users, products, sales

app = FastAPI()
app.include_router(users.router)
app.include_router(products.router)
app.include_router(sales.router)

@app.get('/')
def home():
    return {'message': 'Welcome to Inventory Management System'}