from os.path import isfile, join

from bs4 import BeautifulSoup
import requests
import glob
import re
import os

UPLOAD_FOLDER = './static'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
DATE_PATTERN = r'\b\d{4}-\d{2}-\d{2}\b'
DICT_ATTRIBUTE = {
    'id': 'futures'
}
FX_INSTRUMENTS_TRADINGSTER = {
    "AUD": "232741",
    "GBP": "096742",
    "CAD": "090741",
    "EUR": "099741",
    "JPY": "097741",
    "CHF": "092741",
    "DXY": "098662",
    "NZD": "112741",
    "BTC": "133741",
    "SP 500": "13874%2B",
    "US 100": "209742",
    "GOLD": "088691",
    "SILVER": "084691",
    "NAT GAS": "023651",
}
FX_PERFORMANCE_GRAPHS = {
    "W1": "https://finviz.com/forex_performance.ashx?v=2",
    "M": "https://finviz.com/forex_performance.ashx?v=3",
    "Q": "https://finviz.com/forex_performance.ashx?v=4",
}
FX_CONTRACTS_AMOUNT = {
    "AUD": 100000,
    "GBP": 62500,
    "CAD": 100000,
    "EUR": 125000,
    "JPY": 12500000,
    "CHF": 125000,
    "DXY": 1000,
    "NZD": 100000,
    "BTC": 5,
}


def get_all_xlsx_files(directory):
    return glob.glob(os.path.join(directory, '*.xlsx'))


def get_latest_date_report():
    # Update the latest_date variable with the latest date
    response = get_response(f'https://www.tradingster.com/cot/legacy-futures/{FX_INSTRUMENTS_TRADINGSTER["AUD"]}')
    latest_date = None
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.find('h3', class_='report-sub-title text-center').text
        latest_date = re.search(DATE_PATTERN, text).group()
    return latest_date


def get_div(url, dict_attribute):
    response = get_response(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        div_content = soup.find('div', dict_attribute)
        return [str(div) for div in div_content]
    else:
        print(f"Failed to fetch data from url: {url}")
        return None


def get_instrument_cot_url(instrument_value: str):
    return f'https://www.tradingster.com/cot/legacy-futures/{instrument_value}'


def get_response(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    return requests.get(url, headers=headers)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def delete_images():
    images = [f for f in os.listdir(UPLOAD_FOLDER) if isfile(join(UPLOAD_FOLDER, f)) and allowed_file(f)]
    for image in images:
        os.remove(os.path.join(UPLOAD_FOLDER, image))


def get_converted_contract_amount(from_instrument, to_instrument, amount):
    if from_instrument == "DXY":
        from_instrument = "USD"
    if to_instrument == "DXY":
        to_instrument = "USD"

    print("Converting {} to {}".format(from_instrument, to_instrument))
    converting_currency_url = "https://www.xe.com/currencyconverter/convert/?Amount={}&From={}&To={}".format(amount, from_instrument, to_instrument)
    response = get_response(converting_currency_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        converted_amount = soup.find('p', class_='sc-1c293993-1 fxoXHw').text.replace(",", "").split(" ")[0]
        print("Converted amount: ", converted_amount)
        converted_amount = float(converted_amount)
        return converted_amount
    else:
        print("Failed to fetch data from url: ", converting_currency_url)
        return None


def get_rate_of_contracts(base_contracts, to_contracts):
    return base_contracts/to_contracts


def get_conversion_rate(from_instrument, to_instrument):
    base_contracts = FX_CONTRACTS_AMOUNT[from_instrument]
    to_contracts = FX_CONTRACTS_AMOUNT[to_instrument]
    converted_contract_amount = get_converted_contract_amount(from_instrument, to_instrument, base_contracts)
    return get_rate_of_contracts(converted_contract_amount, to_contracts)
