from fastapi import APIRouter, HTTPException, Path, Depends
from fastapi.responses import JSONResponse
from typing import Annotated
import sqlite3
import secrets

from database import connection
from models.user import Users, AddUser, UpdateUser, LoginRequest

router = APIRouter(tags=["users"])

@router.get('/user')
def users():
    conn = connection()
    rows = conn.execute("select * from users").fetchall()
    return [Users(**dict(row)).model_dump() for row in rows]


@router.post('/createuser')
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

@router.put('/edit/{Id}')
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


@router.delete('/delete/{user_id}')
def delete_user(
                user_id: Annotated[int, Path(..., gt=0,description="Id of the user to delete.")]
                ):
    conn = connection()
    try:
        row = conn.execute("select * from users where Id = ?",(user_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="User does not exist.")
        conn.execute("DELETE from users where Id = ?",(user_id,))
        conn.commit()
    finally:
        conn.close()

    return JSONResponse(status_code=200, content={'message': 'User has been deleted.'})
