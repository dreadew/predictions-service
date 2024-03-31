from pydantic import BaseModel
from datetime import datetime


class CurrencyAdd(BaseModel):
  currency: str
  date: datetime
  rate: float

class CurrencySchema(BaseModel):
  date: datetime
  currency: str
  rate: float
  updated_at: datetime
  created_at: datetime

class GetCurrencyResponse(BaseModel):
  ok: bool = True
  items: list[CurrencySchema]