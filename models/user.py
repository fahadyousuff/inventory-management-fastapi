from pydantic import BaseModel, field_validator, computed_field, Field
from typing import Annotated, Optional, Literal


class LoginRequest(BaseModel):
    usercode: Annotated[str, Field(..., description="example U-1, U-2")]
    password: Annotated[str, Field(...)]


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