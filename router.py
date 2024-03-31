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
		if res[i].date in dates:
			dates.remove(res[i].date)
	if len(dates) > 0:
		await start_prediction(currency, days, dates[0]) if len(dates) == days else await start_prediction(currency, len(dates), dates[0])
		res = await CurrencyRepository.get_by_params(currency, days)
	return {'ok': True, 'items': res}