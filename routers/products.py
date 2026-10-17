from fastapi import APIRouter, HTTPException, Path, Depends
from fastapi.responses import JSONResponse
from typing import Annotated
import sqlite3
import secrets

from database import connection
from models.product import Products, AddProduct, UpdateProduct

router = APIRouter(tags=["products"])

@router.get('/product')
def products():
    conn = connection()
    rows = conn.execute("select * from product").fetchall()
    return [Products(**dict(row)).model_dump() for row in rows]
    

@router.post('/createproduct')
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


@router.put('/editproduct/{product_id}')
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

@router.delete('/deleteproduct/{product_id}')
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

