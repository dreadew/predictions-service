from repository import CurrencyRepository
from fastapi import APIRouter
from datetime import datetime, timedelta

from schemas import GetCurrencyResponse
from utils.predict import start_prediction

router = APIRouter(
	prefix='/currencies'
)

@router.get('/get-currency-rates')
async def get_currency_rates(
	currency: str = 'cny-rub',
	days: int = 1
) -> GetCurrencyResponse:
	if days > 8:
		return {'ok': False, 'items': []}
	dates = [datetime.now().date() + timedelta(i) for i in range(days)]
	res = await CurrencyRepository.get_by_params(currency, days)
	for i in range(len(res)):
		if res[len(res) - (i+1)].date in dates:
			dates.remove(res[len(res) - (i+1)].date)
	if len(dates) > 0:
		await start_prediction(currency, days, dates[0]) if len(dates) == days else await start_prediction(currency, len(dates), dates[0])
		res = await CurrencyRepository.get_by_params(currency, days)
	return {'ok': True, 'items': res}

@router.get('/get-currency-rate')
async def get_currency_rates(
	currency: str = 'cny-rub'
) -> GetCurrencyResponse:
	current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
	res = await CurrencyRepository.get_by_date(currency, current_date)
	return {'ok': True, 'items': res}