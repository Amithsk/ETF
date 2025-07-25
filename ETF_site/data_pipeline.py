from sqlalchemy import create_engine
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
import urllib
from pathlib import Path

def fetch_db_connection():
    password = os.getenv('MYSQL_PASSWORD')
    encoded_pw = urllib.parse.quote_plus(password)  # Properly escape special characters
    DB_URL = f"mysql+pymysql://root:{encoded_pw}@localhost/etf"
    return DB_URL

# Step 1: Load ETF data from MySQL using SQLAlchemy
def fetch_etf_data(dbconnection):
    engine = create_engine(dbconnection)
    query = "SELECT * FROM etf"  
    df = pd.read_sql(query, engine)
    return df.to_dict(orient="records")

# Step 2: Compute summary stats
def compute_summary(etfs):
    total_etfs = len(etfs)  # Count of ETF entries
    total_categories = len(set(etf['etf_asset_category'] for etf in etfs))
    total_funds = len(set(etf['etf_fundhouse_name'] for etf in etfs))
    return total_etfs, total_categories, total_funds

# Step 3: Render Jinja2 HTML template
def render_template(etfs, summary):
    # This gets the full path to the current script (ETF_site/)
    base_path = Path(__file__).resolve().parent
    templates_path = base_path / "templates"
    env = Environment(loader=FileSystemLoader(templates_path))
    print("The templates path",templates_path)
    print("The path",env)
    template = env.get_template("index_template.html")

    total_etfs, total_categories, total_funds = summary

    output_html = template.render(
        etfs=etfs,
        total_etfs=total_etfs,
        total_categories=total_categories,
        total_funds=total_funds
    )

    os.makedirs("output", exist_ok=True)
    with open("output/index.html", "w", encoding="utf-8") as f:
        f.write(output_html)

    print("output/index.html generated")

# Main function
if __name__ == "__main__":
    dbconnection = fetch_db_connection()
    etfs = fetch_etf_data(dbconnection)
    summary = compute_summary(etfs)
    render_template(etfs, summary)
