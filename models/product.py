from pydantic import BaseModel, field_validator, computed_field, Field
from typing import Annotated, Optional, Literal


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
