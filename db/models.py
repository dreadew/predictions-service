from sqlalchemy import Column, String, Date, DateTime, Float, PrimaryKeyConstraint
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func

class Model(DeclarativeBase):
	pass

class Currency(Model):
	__tablename__ = 'currency'

	currency = Column(String, nullable=False, primary_key=True)
	date = Column(Date, nullable=False, primary_key=True)
	rate = Column(Float, nullable=False)

	created_at = Column(DateTime, default=func.now())
	updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

	__table_args__ = (
		PrimaryKeyConstraint(currency, date),
		{},
	)