import json
import joblib
import itertools
import numpy as np
import tensorflow as tf
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from repository import CurrencyRepository
from os import listdir
from os.path import isfile, join
from schemas import CurrencyAdd

def read_json_and_transform(filename, currency):
    with open(filename, 'r') as file:
        data = json.load(file)

    dates = [datetime.strptime(item['Date'], '%d.%m.%Y').date() for item in data]
    if currency == 'cny-aed':
      values = [1/float(item['Value']) for item in data]
    else:
       values = [item['Value'] for item in data]
    return dates, values


def read_xml(filename, currency):
  root = ET.parse(filename).getroot()
  trade_dates = []
  rates = []
  if currency == 'cny-rub' or currency == 'rub-cny':
    for row in root.findall('.//rows/row'):
      trade_date = datetime.strptime(row.attrib['tradedate'], '%Y-%m-%d')
      rate = row.attrib['rate'] if currency == 'cny-rub' else 1/float(row.attrib['rate'])
      if trade_date not in trade_dates:
        trade_dates.append(trade_date.date())
        rates.append(rate)
  elif currency == 'aed-rub' or currency == 'rub-aed':
    for row in root.findall('.//Record'):
      trade_date = datetime.strptime(row.attrib['Date'], '%d.%m.%Y')
      rate = row.find('Value').text.replace(',', '.') if currency == 'aed-rub' else 1/float(row.find('Value').text.replace(',', '.'))
      if trade_date not in trade_dates:
        trade_dates.append(trade_date.date())
        rates.append(rate)
  return trade_dates, rates

def prepare_data(dates, values):
    start_date = min(dates)
    days_since_start = np.array([(date - start_date).days for date in dates]).reshape(-1, 1)

    scaler_dates = MinMaxScaler()
    scaler_values = MinMaxScaler()

    dates_normalized = scaler_dates.fit_transform(days_since_start)
    values = np.array(values).reshape(-1, 1)
    values_normalized = scaler_values.fit_transform(values)

    return dates_normalized, values_normalized, scaler_dates, scaler_values

def create_and_train_model(dates_normalized, values_normalized):
    model = tf.keras.Sequential([
        tf.keras.Input(shape=(1,)),
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dense(1, activation="linear")
    ])
    model.compile(loss='mean_squared_error', optimizer='adam')

    model.fit(dates_normalized, values_normalized, epochs=20000)
    return model

async def predict(model_name, scaler_dates, scaler_values, dates, input_date, days, currency):
    model = tf.keras.models.load_model(f'./utils/nn_models/{model_name}')

    future_dates: list[datetime] = [input_date + timedelta(i) for i in range(days)]
    days_since_start = np.array([(date - min(dates)).days for date in future_dates]).reshape(-1, 1)
    input_dates_norm = scaler_dates.transform(days_since_start)

    predictions_norm = model.predict(input_dates_norm)
    predicted_values = scaler_values.inverse_transform(predictions_norm).flatten()

    future_dates_formatted = [date for date in future_dates]

    for idx, date in enumerate(future_dates_formatted):
       ca = CurrencyAdd(currency=currency, date=date, rate=predicted_values[idx])
       await CurrencyRepository.add_one(ca)

    return future_dates_formatted, predicted_values

async def start_prediction(currency: str, days: int, start_date: datetime = datetime.now().date()):
  is_model_exist = False
  model_name = f'{currency}.keras'
  for file in listdir('./utils/nn_models/'):
     if isfile(join('./utils/nn_models/', file)):
        if file == model_name:
           is_model_exist = True
           break
  
  splitted_currency = currency.split('-')
  inverted_currency = splitted_currency[1] + '-' + splitted_currency[0]
  filename = f'./utils/datasets/{currency}' if (splitted_currency[0] in ['cny', 'aed'] and splitted_currency[1] == 'rub') or (splitted_currency[0] == 'aed' and splitted_currency[1] == 'cny') else f'./utils/datasets/{inverted_currency}'
  print(filename, splitted_currency)
  if currency == 'aed-cny' or currency == 'cny-aed':
    dates, rates = read_json_and_transform(filename + '.json', currency)
  else:
    dates, rates = read_xml(filename + '.xml', currency)
  dates_normalized, values_normalized, scaler_dates, scaler_values = prepare_data(dates, rates)
  joblib.dump(scaler_dates, './utils/scaler/scaler_dates.joblib')
  joblib.dump(scaler_values, './utils/scaler/scaler_values.joblib')

  if not is_model_exist:
     model = create_and_train_model(dates_normalized, values_normalized)
     model.save(f'./utils/nn_models/{currency}.keras')
     
  future_dates, predicted_rates = await predict(model_name, scaler_dates, scaler_values, dates, start_date, days, currency)
  return future_dates, predicted_rates

async def predict_previous():
  res = await CurrencyRepository.get_by_date('cny-rub', datetime.strptime('19.01.2023', '%d.%m.%Y'))
  if (len(res) > 0):
    return
  currencies = ['rub', 'aed', 'cny']
  permutations = list(itertools.permutations(currencies, 2))
  start_date = datetime.strptime('19.01.2023', '%d.%m.%Y').date()
  days =  (datetime.now().date() - timedelta(1)) - start_date
  for p in permutations:
    await start_prediction('-'.join(p), days.days, start_date)