import os

import pandas as pd
from flask import Flask, render_template, send_file, jsonify
from cot_report import COTReport
from utils import get_all_xlsx_files

OUTPUT_EXCEL_FILE = './cot_report_{}.xlsx'

app = Flask(__name__)
cot_report = COTReport()


# Route for home page
@app.route('/')
def home():
    report_date = cot_report.latest_date
    output_file = OUTPUT_EXCEL_FILE.format(report_date)
    xlsx_files = get_all_xlsx_files('.')
    for file in xlsx_files:
        if os.path.exists(file) and file != output_file:
            os.remove(file)
    return render_template('index.html', report_date=report_date)


# Route to download Excel file
@app.route('/download')
def download():
    last_report = OUTPUT_EXCEL_FILE.format(cot_report.latest_date)
    if not os.path.exists(last_report):
        cot_report.get_cot_report(last_report)
    return send_file(last_report, as_attachment=True)


@app.route('/get_report_data')
def get_report_data():
    last_report = OUTPUT_EXCEL_FILE.format(cot_report.latest_date)
    if not os.path.exists(last_report):
        cot_report.get_cot_report(last_report)
    df = pd.read_excel(last_report)
    df = df.fillna("")
    data_to_return = jsonify(df.to_dict(orient='records'))
    return data_to_return


@app.route('/get_performance_data')
def get_performance_data():
    return jsonify({
        "W1": cot_report.w_performance,
        "M": cot_report.m_performance,
        "Q": cot_report.q_performance
    })


if __name__ == '__main__':
    app.run(debug=True)
