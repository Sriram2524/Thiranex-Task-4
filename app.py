from flask import Flask, render_template_string
import pandas as pd
# Assuming your function is saved in pipeline_automation.py
from pipeline_automation import clean_and_report_cafe_data 

app = Flask(__name__)

@app.route('/')
def home():
    # Automatically trigger the pipeline when visiting localhost
    clean_and_report_cafe_data("dirty_cafe_sales.csv", "cafe_automation_report.html")

    # Read and serve the generated report directly to the browser
    with open("cafe_automation_report.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return render_template_string(html_content)

if __name__ == '__main__':
    app.run(debug=True, port=5000)