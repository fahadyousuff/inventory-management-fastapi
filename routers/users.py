from fastapi import APIRouter, HTTPException, Path, Depends
from fastapi.responses import JSONResponse
from typing import Annotated
import sqlite3
import secrets

from database import connection
from security import verify_password
from models.user import Users, AddUser, UpdateUser, LoginRequest

router = APIRouter(tags=["users"])


@router.post("/login")
def login(payload: LoginRequest):
    code = payload.usercode.strip().upper()
    if not code.startswith("U-"):
        raise HTTPException(status_code=400, detail="Invalid User-code")
    try:
        uid = int(code[2:])
    except:
        raise HTTPException(status_code=400, detail="Invalid User-code")

    # fetching the user
    conn = connection()
    try:
        row = conn.execute("select Id, name, IsAdmin, ApiToken, PasswordHash from users where Id = ?",(uid,)).fetchone()
    finally:
        conn.close()

    if row is None or not row["PasswordHash"]:
        raise HTTPException(status_code=401, detail="Invalid usercode or password")

    if not verify_password(payload.password, row["PasswordHash"]):
        raise HTTPException(status_code=401, detail="Invalid usercode or password")

    return {
        "token": row["ApiToken"],
        "user": {
            "Id": row["Id"],
            "name": row["name"],
            "IsAdmin": bool(row["IsAdmin"]),
            "usercode": f"U-{row['Id']}",
        },
    }


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
