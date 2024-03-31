import settings

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from db.models import Model

db_engine = create_async_engine(
	f'postgresql+asyncpg://{settings.DATABASE_NAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_DBNAME}',
	future=True,
	echo=True
)

new_session = async_sessionmaker(db_engine, expire_on_commit=False)

async def create_tables():
	async with db_engine.begin() as conn:
		await conn.run_sync(Model.metadata.create_all)

async def delete_tables():
	async with db_engine.begin() as conn:
		await conn.run_sync(Model.metadata.drop_all)