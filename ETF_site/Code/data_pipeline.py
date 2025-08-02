from sqlalchemy import create_engine
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
import urllib
from pathlib import Path
import shutil

def fetch_db_connection():
    password = os.getenv('MYSQL_PASSWORD')
    encoded_pw = urllib.parse.quote_plus(password)
    return f"mysql+pymysql://root:{encoded_pw}@localhost/etf"

def fetch_etf_data(dbconnection):
    engine = create_engine(dbconnection)
    df = pd.read_sql("SELECT * FROM etf", engine)
    return df.to_dict(orient="records")

def compute_summary(etfs):
    total_etfs       = len(etfs)
    total_categories = len({e['etf_asset_category']   for e in etfs})
    total_funds      = len({e['etf_fundhouse_name']    for e in etfs})
    return total_etfs, total_categories, total_funds

def render_template(etfs, summary):
    # ETF_site/Code
    code_dir      = Path(__file__).resolve().parent
    templates_dir = code_dir / "templates"
    env           = Environment(loader=FileSystemLoader(templates_dir))
    template      = env.get_template("index_template.html")

    total_etfs, total_categories, total_funds = summary
    html = template.render(
        etfs=etfs,
        total_etfs=total_etfs,
        total_categories=total_categories,
        total_funds=total_funds
    )

    # ETF/output/
    project_root = code_dir.parent.parent
    output_dir   = project_root / "output"
    output_dir.mkdir(exist_ok=True)

    (output_dir / "index.html").write_text(html, encoding="utf-8")
    print("Rendered → output/index.html")

def copy_assets():
    # locate:
    #   ETF_site/Code        ← this file’s folder
    #   ETF_site/static/css  ← where your custom CSS lives
    code_dir       = Path(__file__).resolve().parent #Target D:\ETF\ETF_site\Code
    static_css_src = code_dir/ "static" / "css" / "etf_site.css"
    dynamic_js_src = code_dir/ "static" / "js" / "etf_site.js"
   
    # ETF/output/css/
    project_root   = code_dir.parent.parent #Target D:\ETF\ETF_site\Code
    css_dst_dir    = project_root / "output" / "css"
    css_dst_dir.mkdir(parents=True, exist_ok=True)

    #ETF/output/js
    project_root   = code_dir.parent.parent #Target D:\ETF\ETF_site\Code
    dynamic_js_dst    = project_root / "output" 
    
    if static_css_src.exists():
        shutil.copy(static_css_src, css_dst_dir / "etf_site.css")
        print(f"Copied CSS → output/css/etf_site.css")
    else:
        print(f"WARNING: {static_css_src} not found, skipping CSS copy")

    if dynamic_js_src.exists():
        shutil.copy(dynamic_js_src, dynamic_js_dst / "etf_site.js")
        print(f"Copied js → output/etf_site.js")
    else:
        print(f"WARNING: {dynamic_js_src} not found, skipping CSS copy")

if __name__ == "__main__":
    dburl  = fetch_db_connection()
    etfs   = fetch_etf_data(dburl)
    summary= compute_summary(etfs)
    render_template(etfs, summary)
    copy_assets()
