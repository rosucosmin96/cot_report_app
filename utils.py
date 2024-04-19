from bs4 import BeautifulSoup
import requests
import glob
import re
import os

DATE_PATTERN = r'\b\d{4}-\d{2}-\d{2}\b'
DICT_ATTRIBUTE = {
    'id': 'futures'
}
FX_INSTRUMENTS = {
    "AUD": "232741",
    "GBP": "096742",
    "CAD": "090741",
    "EUR": "099741",
    "JPY": "097741",
    "CHF": "092741",
    "DXY": "098662",
    "NZD": "112741",
}
FX_PERFORMANCE_GRAPHS = {
    "W1": "https://finviz.com/forex_performance.ashx?v=2",
    "M": "https://finviz.com/forex_performance.ashx?v=3",
    "Q": "https://finviz.com/forex_performance.ashx?v=4",
}


def get_all_xlsx_files(directory):
    return glob.glob(os.path.join(directory, '*.xlsx'))


def get_latest_date_report():
    # Update the latest_date variable with the latest date
    response = requests.get(f'https://www.tradingster.com/cot/legacy-futures/{FX_INSTRUMENTS["AUD"]}')
    latest_date = None
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.find('h3', class_='report-sub-title text-center').text
        latest_date = re.search(DATE_PATTERN, text).group()
    return latest_date


def get_div(url, dict_attribute):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        div_content = soup.find('div', dict_attribute)
        return [str(div) for div in div_content]
    else:
        print(f"Failed to fetch data from url: {url}")
        return None


def get_instrument_cot_url(instrument_value: str):
    return f'https://www.tradingster.com/cot/legacy-futures/{instrument_value}'

