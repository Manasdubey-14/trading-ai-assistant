from pydantic import BaseModel


class CloseTradeRequest(BaseModel):
    exit_price: float