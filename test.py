import requests
from currency_converter import CurrencyConverter

# currency = CurrencyConverter()
#
# x = 25
# a = 'EUR'
# b = 'USD'

# data = currency.convert(x, a, b)
# print(data)
city_name = 'london'.lower()
api_key = 'ad319fb46026131ca79ebd383b569bd5'
response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric').json()['main']['temp']

try:
    print(response)
except KeyError:
    print('Wrong city')
