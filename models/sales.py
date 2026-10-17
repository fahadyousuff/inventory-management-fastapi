from pydantic import BaseModel, field_validator, computed_field, Field
from typing import Annotated, Optional, Literal


class Sales(BaseModel):
    Id : Annotated[int, Field(..., description="Unique ID of sales transaction")]
    UserId : Annotated[int, Field(..., description="User ID of sales person in the sales transaction")]
    ProductId : Annotated[int, Field(..., description="ID of the product in the sales transaction")]
    Quantity : Annotated[int, Field(..., description="Quantity of material requested from the customer")]



class AddSales(BaseModel):
    ProductName : Annotated[str, Field(..., description="Name of the product being posting in the sales")]
    Quantity : Annotated[int, Field(..., gt=0, description="Quantity of material requested from the customer")]

    @field_validator('ProductName')
    @classmethod
    def valid_product(cls, value):
        product = value.title()
        return product


class UpdateSales(BaseModel):
    ProductName : Annotated[Optional[str], Field(default=None)]
    Quantity : Annotated[Optional[int], Field(default=None)]

    @field_validator('ProductName')
    @classmethod
    def valid_product(cls, value):
        if value is None:
            return None
        product = value.title()
        return product