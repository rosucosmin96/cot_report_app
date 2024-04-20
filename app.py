import os
import pandas as pd
from os.path import isfile, join
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, send_file, jsonify, request
from werkzeug.utils import secure_filename
from cot_report import COTReport
from utils import get_all_xlsx_files, allowed_file, UPLOAD_FOLDER, delete_images

OUTPUT_EXCEL_FILE = './cot_report_{}.xlsx'


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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


@app.route('/get_performance_images')
def get_performance_images():
    return jsonify({'images': [f for f in os.listdir(UPLOAD_FOLDER) if isfile(join(UPLOAD_FOLDER, f) ) and allowed_file(f)]})


@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    files = request.files.getlist('file')
    for file in files:
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify({'success': 'Files uploaded successfully'})


@app.route('/delete_images')
def delete_image():
    delete_images()
    return jsonify({'success': 'Images deleted successfully'})


scheduler = BackgroundScheduler()
scheduler.add_job(delete_images, 'cron', day_of_week='wed', hour=8)
scheduler.start()


if __name__ == '__main__':
    app.run(debug=True)
