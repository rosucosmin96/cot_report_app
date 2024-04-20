from bs4 import BeautifulSoup
import pandas as pd
import requests

from utils import get_latest_date_report, get_instrument_cot_url, get_div, DICT_ATTRIBUTE, FX_PERFORMANCE_GRAPHS, \
    FX_INSTRUMENTS, get_response


class COTReport:
    def __init__(self):
        self.latest_date = get_latest_date_report()
        self.w_performance = None
        self.m_performance = None
        self.q_performance = None

    def get_cot_report(self, output_file):
        df = pd.DataFrame(columns=['Instrument', 'Long', 'Short'])
        for key, value in FX_INSTRUMENTS.items():
            response = get_response(get_instrument_cot_url(value))
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                instrument_data = soup.find('table', class_='table table-striped table-bordered').find(
                    'tbody').find_all('tr')

                # Get non-commercial long and short contracts
                instrument_contracts = instrument_data[1]
                noncommercial_long_contracts = instrument_contracts.contents[1].text
                noncommercial_short_contracts = instrument_contracts.contents[3].text
                data = {"Instrument": key, "Long": noncommercial_long_contracts, "Short": noncommercial_short_contracts}
                df.loc[len(df)] = data

                # Get non-commercial long and short changes
                instrument_changes = instrument_data[3]
                noncommercial_long_changes = int(instrument_changes.contents[1].text.replace(",", ""))
                noncommercial_short_changes = int(instrument_changes.contents[3].text.replace(",", ""))
                data = {"Instrument": "", "Long": noncommercial_long_changes, "Short": noncommercial_short_changes}
                df.loc[len(df)] = data
            else:
                print("Failed to fetch data for instrument: ", key)

        writer = pd.ExcelWriter(output_file, engine='xlsxwriter')

        # Define a function that colors cells based on their values
        def color_cells(val):
            color = 'white'
            try:
                value = int(val)
                color = 'red' if value < 0 else 'lightgreen'
                return 'background-color: %s' % color
            except ValueError:
                return 'background-color: %s' % color

        # Apply the color_cells function to the DataFrame
        styled_df = df.style.map(color_cells)

        # Write the styled DataFrame to an Excel file
        styled_df.to_excel(writer, index=False)

        # Close the Pandas Excel writer and output the Excel file.
        writer.book.close()
        # df.to_excel(output_file, index=False)
