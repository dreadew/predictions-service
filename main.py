from fastapi import FastAPI
from router import router as currencies_router
from contextlib import asynccontextmanager
from db.session import create_tables, delete_tables
from fastapi.middleware.cors import CORSMiddleware
from utils.predict import predict_previous

@asynccontextmanager
async def lifespan(app: FastAPI):
	#await delete_tables()
	#print('База данных очищена')
	await create_tables()
	print('База данных готова к работе')
	await predict_previous()
	print('Прошлые записи созданы')
	yield
	print('Выключение...')

app = FastAPI(lifespan=lifespan)
origins = 'http://localhost:3000'
app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=['GET'],
	allow_headers=['*']
)
app.include_router(currencies_router)