from bs4 import BeautifulSoup
import pandas as pd

from utils import get_latest_date_report, get_instrument_cot_url, FX_INSTRUMENTS_TRADINGSTER, get_response, \
    get_conversion_rate, FX_CONTRACTS_AMOUNT


class COTReport:
    def __init__(self):
        self.latest_date = get_latest_date_report()

    def get_cot_report(self, output_file, base_currency="EUR"):
        df = pd.DataFrame(columns=['Instrument', 'Long', 'Short', 'Long [{}]'.format(base_currency), 'Short [{}]'.format(base_currency)])
        for key, value in FX_INSTRUMENTS_TRADINGSTER.items():
            isConversion = True if key in FX_CONTRACTS_AMOUNT else False
            response = get_response(get_instrument_cot_url(value))
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                instrument_data = soup.find('table', class_='table table-striped table-bordered').find(
                    'tbody').find_all('tr')

                # Get conversion rate
                contract_rate = get_conversion_rate(key, base_currency) if isConversion else 0
                print("Conversion rate: ", contract_rate)

                # Get non-commercial long and short contracts
                instrument_contracts = instrument_data[1]
                noncommercial_long_contracts = instrument_contracts.contents[1].text
                noncommercial_short_contracts = instrument_contracts.contents[3].text
                noncommercial_long_contracts_converted = int(int(noncommercial_long_contracts.replace(",", "")) * contract_rate)
                noncommercial_short_contracts_converted = int(int(noncommercial_short_contracts.replace(",", "")) * contract_rate)
                data = {"Instrument": key, "Long": noncommercial_long_contracts,
                        "Short": noncommercial_short_contracts,
                        "Long [{}]".format(base_currency): str(int(noncommercial_long_contracts_converted//1000)) + "," + str(noncommercial_long_contracts_converted%1000),
                        "Short [{}]".format(base_currency): str(int(noncommercial_short_contracts_converted/1000)) + "," + str(noncommercial_short_contracts_converted%1000)}
                df.loc[len(df)] = data

                # Get non-commercial long and short changes
                instrument_changes = instrument_data[3]
                noncommercial_long_changes = int(instrument_changes.contents[1].text.replace(",", ""))
                noncommercial_short_changes = int(instrument_changes.contents[3].text.replace(",", ""))
                noncommercial_long_changes_converted = int(noncommercial_long_changes * contract_rate)
                noncommercial_short_changes_converted = int(noncommercial_short_changes * contract_rate)
                data = {"Instrument": "",
                        "Long": noncommercial_long_changes,
                        "Short": noncommercial_short_changes,
                        "Long [{}]".format(base_currency): noncommercial_long_changes_converted,
                        "Short [{}]".format(base_currency): noncommercial_short_changes_converted}
                df.loc[len(df)] = data
            else:
                print("Failed to fetch data for instrument: ", key)

        writer = pd.ExcelWriter(output_file, engine='xlsxwriter')

        # Define a function that colors cells based on their values
        def color_cells(val):
            color = 'white'
            try:
                value = int(val)
                text_color = 'white'
                color = 'red' if value < 0 else 'green'
                return 'background-color: %s; color: %s' % (color, text_color)
            except ValueError:
                return 'background-color: %s' % color

        # Apply the color_cells function to the DataFrame
        styled_df = df.style.map(color_cells)

        # Write the styled DataFrame to an Excel file
        styled_df.to_excel(writer, index=False)

        # Close the Pandas Excel writer and output the Excel file.
        writer.book.close()
        # df.to_excel(output_file, index=False)
