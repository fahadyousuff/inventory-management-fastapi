import pandas as pd
import sqlite3
from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator, computed_field, Field
from typing import Annotated, Optional, Literal

app = FastAPI()


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
    conn = connection()
    try:
        conn.execute("""
        INSERT INTO users (name)
        VALUES(?)
        """,
        (user.name,)
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