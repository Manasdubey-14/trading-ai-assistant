from pydantic import BaseModel


class ExecuteTradeRequest(BaseModel):
    quantity: int