import datetime
from pydantic import BaseModel
from db.session import new_session
from db.models import Currency
from sqlalchemy import select
from schemas import CurrencyAdd, CurrencySchema

class CurrencyRepository:
	@classmethod
	async def add_one(cls, currency: CurrencyAdd) -> str:
		async with new_session() as session:
			currency_dict = currency.model_dump()
			cur = Currency(**currency_dict)
			session.add(cur)
			await session.flush()
			await session.commit()
			return cur.date
	
	@classmethod
	async def get_all(cls):
		async with new_session() as session:
			query = select(Currency)
			result = await session.execute(query)
			currency_models = result.scalars().all()
			return currency_models
		
	@classmethod
	async def get_by_params(cls, currency: str, days: int) -> list[CurrencySchema]:
		async with new_session() as session:
			query = select(Currency).where(Currency.currency == currency).order_by(Currency.date.asc()).limit(days + 1)
			result = await session.execute(query)
			currency_models = result.scalars().all()
			return currency_models