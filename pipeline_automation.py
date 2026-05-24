import os
import numpy as np
import pandas as pd
import plotly.express as px


def clean_and_report_cafe_data(input_csv, output_html):
    print("🚀 Initializing Cafe Sales Automation Pipeline...")

    # 1. Validation check for the input Kaggle dataset
    if not os.path.exists(input_csv):
        raise FileNotFoundError(
            f"Could not find '{input_csv}'. Please place the extracted Kaggle CSV in this directory."
        )

    # Load data
    df = pd.read_csv(input_csv)
    initial_rows = len(df)

    # --- PHASE 1: REUSABLE DATA CLEANING ---

    # Step A: Drop pure duplicate records
    df.drop_duplicates(inplace=True)
    duplicates_removed = initial_rows - len(df)

    # Step B: Sanitize specific placeholders often found in dirty data ('ERROR', 'UNKNOWN', 'NONE')
    invalid_placeholders = ["ERROR", "UNKNOWN", "NONE", "NAN", "NULL"]
    for col in df.columns:
        # Convert column values to string temporarily to identify placeholder text anomalies safely
        df[col] = df[col].apply(
            lambda x: (
                np.nan
                if str(x).strip().upper() in invalid_placeholders
                else x
            )
        )

    # Step C: Standardize text features (e.g., matching 'Coffee' vs 'coffee ')
    text_cols = ["Item", "Payment Method", "Location"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str).str.strip().str.title()

    # Step D: Correct Data Types & handle missing numbers safely via Column Medians
    numeric_cols = ["Quantity", "Price Per Unit", "Total Spent"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)

    # Step E: Mathematical Re-validation (Recalculating Total Spent to fix data anomalies)
    if "Quantity" in df.columns and "Price Per Unit" in df.columns:
        df["Total Spent"] = df["Quantity"] * df["Price Per Unit"]

    print("✔️ Cleaning and parsing tasks successfully executed.")

    # --- PHASE 2: AUTOMATED HTML REPORT GENERATION ---

    # Metric KPI Calculations
    total_clean_records = len(df)
    calculated_revenue = (
        df["Total Spent"].sum() if "Total Spent" in df.columns else 0.0
    )

    # Visual Component: Grouped Aggregation for Top Items sold
    item_summary = (
        df.groupby("Item")["Quantity"]
        .sum()
        .reset_index()
        .sort_values(by="Quantity", ascending=False)
    )

    fig_items = px.bar(
        item_summary,
        x="Item",
        y="Quantity",
        title="Total Quantity Sold by Product Item (Cleaned Distribution)",
        labels={"Item": "Product Name", "Quantity": "Units Sold"},
        color="Quantity",
        color_continuous_scale=px.colors.sequential.Viridis,
        template="plotly_white",
    )
    # Extract standalone HTML component string
    chart_html_div = fig_items.to_html(full_html=False, include_plotlyjs=False)

    # Build responsive HTML/CSS UI interface template layout
    html_dashboard = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Automated Performance Dashboard</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background-color: #f4f6f9; color: #333; }}
            h1 {{ color: #1e3d59; border-bottom: 3px solid #ff6e40; padding-bottom: 12px; margin-bottom: 30px; }}
            .metric-row {{ display: flex; gap: 20px; margin-bottom: 35px; }}
            .kpi-card {{ background: #ffffff; padding: 25px; border-radius: 12px; 
                         box-shadow: 0 4px 12px rgba(0,0,0,0.05); flex: 1; text-align: center; border-top: 4px solid #1e3d59; }}
            .kpi-card h3 {{ margin: 0; color: #777; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; }}
            .kpi-card p {{ margin: 12px 0 0 0; font-size: 32px; font-weight: bold; color: #1e3d59; }}
            .chart-box {{ background: #ffffff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
        </style>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body>
        <h1>☕ Automated Cafe Sales Data Cleaning & KPI Report</h1>
        
        <div class="metric-row">
            <div class="kpi-card">
                <h3>Cleaned Records Processed</h3>
                <p style="color: #2b7a78;">{total_clean_records:,}</p>
            </div>
            <div class="kpi-card">
                <h3>Row Duplicates Removed</h3>
                <p style="color: #e05038;">{duplicates_removed}</p>
            </div>
            <div class="kpi-card">
                <h3>Total Computed Revenue</h3>
                <p style="color: #ff6e40;">${calculated_revenue:,.2f}</p>
            </div>
        </div>

        <div class="chart-box">
            {chart_html_div}
        </div>
    </body>
    </html>
    """

    # Export outputs to workspace disk files
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_dashboard)

    df.to_csv("cleaned_cafe_sales.csv", index=False)

    print(f"🎉 Pipeline successfully completed output generation!")
    print(f"📁 Cleaned structured dataset saved to: 'cleaned_cafe_sales.csv'")
    print(f"🌐 Dynamic frontend dashboard generated at: '{output_html}'")


if __name__ == "__main__":
    # Point execution directly to the extracted dirty dataset file string
    try:
        clean_and_report_cafe_data(
            "dirty_cafe_sales.csv", "cafe_automation_report.html"
        )
    except FileNotFoundError as error:
        print(f"❌ Error: {error}")