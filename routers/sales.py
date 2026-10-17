from fastapi import APIRouter, HTTPException, Path, Depends
from fastapi.responses import JSONResponse
from typing import Annotated
import sqlite3
import secrets

from database import connection
from dependencies import get_current_user, require_admin
from models.sales import Sales, AddSales, UpdateSales

router = APIRouter(tags=["sales"])

@router.get('/sales')
def show_sales():
    conn = connection()
    rows = conn.execute("select * from sales").fetchall()
    return [Sales(**dict(row)).model_dump() for row in rows]


@router.post('/addsales')
def create_sales(sales: AddSales, user = Depends(get_current_user)):
    conn = connection()
    try:
        product = conn.execute("select Id from product where ProductName = ?",(sales.ProductName,)).fetchone()
        if product is None:
            raise HTTPException(status_code=404, detail="Product not available in Inventory.")
        conn.execute("""
        INSERT INTO sales (UserId, ProductId, Quantity)
        VALUES (?, ?, ?)
        """,
        (user["Id"], product["Id"], sales.Quantity)
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
    return JSONResponse(status_code=200, content={'message': 'Sales Transaction has been added.'})



@router.put('/editsales/{sales_id}')
def update_sales(sales_id: int, sales: UpdateSales):
    conn = connection()
    try:
        row = conn.execute("select * from sales where Id = ?",(sales_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Sales Transaction not found.")
        update_info = sales.model_dump(exclude_unset=True)
        if not update_info:
            raise HTTPException(status_code=400, detail="Nothing to update")
        if "ProductName" in update_info:
            product = conn.execute("select * from product where ProductName=?",(update_info["ProductName"],)).fetchone()
            if product is None:
                raise HTTPException(status_code=404, detail='Invalid Product.')
            update_info["ProductId"] = product["Id"]
            del update_info["ProductName"]

        set_params = ", ".join(f"{k} = ?" for k in update_info.keys())
        values = list(update_info.values()) + [sales_id]

        conn.execute(f"UPDATE sales SET {set_params} where Id = ?",values)
        conn.commit()

    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        conn.close()

    return JSONResponse(status_code=200, content={'message': 'Sales transaction has been updated.'})
        

@router.delete('/deletesales/{sales_id}')
def delete_sales(
    sales_id: Annotated[int, Path(..., gt=0,description="Id of sales transction to delete.")],
    admin = Depends(require_admin)
    ):
    conn = connection()
    try:
        row = conn.execute("Select * from sales where Id = ?",(sales_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Sales Transaction not found.")
        conn.execute("DELETE FROM sales where Id = ?",(sales_id,))
        conn.commit()
    
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        conn.close()

    return JSONResponse(status_code=200, content={'message': 'Sales Transaction has been deleted.'})
