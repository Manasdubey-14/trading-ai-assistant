from pydantic import BaseModel, Field


class CapitalUpdate(BaseModel):
    starting_capital: float = Field(gt=0)