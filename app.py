import pandas as pd
import sqlite3
from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator, computed_field, Field
from typing import Annotated, Optional, Literal
import secrets

app = FastAPI()


# ===================== User Master Data Validation =================================
# Validation for overall user data
class Users(BaseModel):
    Id: Annotated[int, Field(..., description="Primary key of the user table")]
    name: Annotated[str, Field(..., description="Name of the user")]

    @computed_field
    @property
    def usercode(self) -> str:
        uc = f"U-{self.Id}"
        return uc

class AddUser(BaseModel):
    name: Annotated[str, Field(..., description="Input the name of the user")]

    @field_validator('name')
    @classmethod
    def valid_user(cls, value):
        name = value.title()
        return name

class UpdateUser(BaseModel):
    name : Annotated[Optional[str], Field(default=None)]

    @field_validator('name')
    @classmethod
    def valid_user(cls, value):
        name = value.title()
        return name


# ===================== Product Master Data Validation =================================

class Products(BaseModel):
    Id: Annotated[int, Field(..., description="Primary key of product table")]
    ProductCode: Annotated[str, Field(..., description="Unique of Products")]
    ProductName: Annotated[str, Field(..., description="Name of the Product")]
    Stock: Annotated[int, Field(..., gt=0, description="Stock of respective Product")]


class AddProduct(BaseModel):
    ProductName: Annotated[str, Field(..., description="Name of the Product")]
    Stock: Annotated[int, Field(..., gt=0, description="Stock of respective Product")]

    @field_validator('ProductName')
    @classmethod
    def valid_product(cls, value):
        valid_product = value.title()
        return valid_product

class UpdateProduct(BaseModel):
    ProductName: Annotated[Optional[str], Field(default=None)]
    Stock: Annotated[Optional[int], Field(default=None)]

    @field_validator('ProductName')
    @classmethod
    def valid_product(cls, value):
        valid_product = value.title()
        return valid_product

# ===================== User End-Points ================================================

def connection():
    conn = sqlite3.connect('inventorysystem.db')
    # for accessing the tables
    conn.row_factory = sqlite3.Row
    return conn


@app.get('/')
def home():
    return {'message':'Welcome to inventory Management System'}

@app.get('/user')
def users():
    conn = connection()
    rows = conn.execute("select * from users").fetchall()
    return [Users(**dict(row)).model_dump() for row in rows]


@app.post('/createuser')
def create_user(user: AddUser):
    token = secrets.token_hex(32)
    conn = connection()
    try:
        conn.execute("""
        INSERT INTO users (name, ApiToken)
        VALUES(?,?)
        """,
        (user.name, token)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists.")
    finally:
        conn.close()

    return JSONResponse(status_code=200, content={'message': 'User has been added.'})

@app.put('/edit/{Id}')
def update_user(user_id: int, user_update:UpdateUser):
    conn = connection()
    try:
        row = conn.execute("select * from users where Id = ?",(user_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="User not found.")
        update_info = user_update.model_dump(exclude_unset=True)
        if not update_info:
            raise HTTPException(status_code=400, detail="Update details not present.")

        set_params = ", ".join(f"{k} = ?" for k in update_info.keys())
        values = list(update_info.values()) + [user_id]

        conn.execute(f"UPDATE users SET {set_params} where Id = ?",values)
        conn.commit()
    finally:
        conn.close()

    return JSONResponse(status_code=200, content={'message': 'User has been updated.'})


@app.delete('/delete/{user_id}')
def delete_user(
                user_id: Annotated[int, Path(..., gt=0,description="Id of the user to delete.")]
                ):
    conn = connection()
    try:
        row = conn.execute("select * from users where Id = ?",(user_id,)).fetchone()
        if row is None:
            return HTTPException(status_code=404, detail="User does not exist.")
        conn.execute("DELETE from users where Id = ?",(user_id,))
        conn.commit()
    finally:
        conn.close()

    return JSONResponse(status_code=200, content={'message': 'User has been deleted.'})



# ===================== Product End-Points ================================================


@app.get('/product')
def products():
    conn = connection()
    rows = conn.execute("select * from product").fetchall()
    return [Products(**dict(row)).model_dump() for row in rows]
    

@app.post('/createproduct')
def create_product(product: AddProduct):
    conn = connection()
    try:
        conn.execute("""
        INSERT INTO product(ProductName, Stock)
        VALUES (?, ?)
        """,
        (product.ProductName, product.Stock)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Product already exists.")
    finally:
        conn.close()
    return JSONResponse(status_code=200, content={'message': "Product has been added."})


@app.put('/editproduct/{product_id}')
def update_product(product_id: int, product: UpdateProduct):
    conn = connection()
    try:
        row = conn.execute("select * from product where Id = ?",(product_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found.")
        update_info = product.model_dump(exclude_unset=True)
        if not update_info:
            raise HTTPException(status_code=400, detail="No product to update.")

        set_params = ", ".join(f"{k} = ?" for k in update_info.keys())
        values = list(update_info.values()) + [product_id]
        
        conn.execute(f"""
        UPDATE product
        set {set_params} where id = ? 
        """, (values))
        conn.commit()
    finally:
        conn.close()

    return JSONResponse(status_code=200, content={'message': 'Product has been updated.'})

@app.delete('/deleteproduct/{product_id}')
def delete_product(
    product_id: Annotated[int, Path(..., gt=0,description="Id of the product to delete.")]
):
    conn = connection()
    try:
        row = conn.execute("select * from product where Id = ? ", (product_id,))
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found.")
        conn.execute("DELETE FROM product where Id = ?", (product_id,))
        conn.commit()
    finally:
        conn.close()

    return JSONResponse(status_code=200, content={'message': 'Product has been deleted.'})