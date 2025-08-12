from sqlalchemy import create_engine
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
import urllib
from pathlib import Path
import shutil
from collections import defaultdict
import json


# -------------------------
# Database Connection
# -------------------------
def fetch_db_connection():
    password = os.getenv('MYSQL_PASSWORD')
    encoded_pw = urllib.parse.quote_plus(password)
    return f"mysql+pymysql://root:{encoded_pw}@localhost/etf"


# -------------------------
# ETF Base Data
# -------------------------
def fetch_etf_data(dbconnection):
    engine = create_engine(dbconnection)
    try:
        df = pd.read_sql("""
            SELECT * 
            FROM etf E
            JOIN etf_asset A 
              ON E.etf_asset_category = A.idetf_asset
        """, engine)
    finally:
        engine.dispose()
    return df.to_dict(orient="records")


def compute_summary(etfs):
    total_etfs = len(etfs)
    total_categories = len({e['etf_asset_category'] for e in etfs})
    total_funds = len({e['etf_fundhouse_name'] for e in etfs})
    return total_etfs, total_categories, total_funds


# -------------------------
# Tracking Error
# -------------------------
def fetch_latest_tracking_error(dbconnection):
    engine = create_engine(dbconnection)
    query = """
        SELECT t1.etf_id, t1.etf_trackingerror_value
        FROM etf_trackingerror t1
        INNER JOIN (
            SELECT etf_id,
                   MAX(CONCAT(
                       etf_trackingerror_year,
                       LPAD(
                           CASE etf_trackingerror_month
                               WHEN 'Jan' THEN 1
                               WHEN 'Feb' THEN 2
                               WHEN 'Mar' THEN 3
                               WHEN 'Apr' THEN 4
                               WHEN 'May' THEN 5
                               WHEN 'Jun' THEN 6
                               WHEN 'Jul' THEN 7
                               WHEN 'Aug' THEN 8
                               WHEN 'Sep' THEN 9
                               WHEN 'Oct' THEN 10
                               WHEN 'Nov' THEN 11
                               WHEN 'Dec' THEN 12
                           END,
                           2,
                           '0'
                       )
                   )) AS max_period
            FROM etf_trackingerror
            WHERE etf_trackingerror_timeperiod = 'SL'
            GROUP BY etf_id
        ) t2 ON t1.etf_id = t2.etf_id
           AND CONCAT(
               t1.etf_trackingerror_year,
               LPAD(
                   CASE t1.etf_trackingerror_month
                       WHEN 'Jan' THEN 1
                       WHEN 'Feb' THEN 2
                       WHEN 'Mar' THEN 3
                       WHEN 'Apr' THEN 4
                       WHEN 'May' THEN 5
                       WHEN 'Jun' THEN 6
                       WHEN 'Jul' THEN 7
                       WHEN 'Aug' THEN 8
                       WHEN 'Sep' THEN 9
                       WHEN 'Oct' THEN 10
                       WHEN 'Nov' THEN 11
                       WHEN 'Dec' THEN 12
                   END,
                   2,
                   '0'
               )
           ) = t2.max_period
        WHERE t1.etf_trackingerror_timeperiod = 'SL';
    """

    try:
        df = pd.read_sql(query, engine)
    finally:
        engine.dispose()
    return {row["etf_id"]: row["etf_trackingerror_value"] for _, row in df.iterrows()}


def fetch_tracking_error_history(dbconnection):
    engine = create_engine(dbconnection)
    query = """
         SELECT etf_id, etf_trackingerror_timeperiod, etf_trackingerror_value,
               etf_trackingerror_month, etf_trackingerror_year
        FROM etf_trackingerror
        ORDER BY etf_id, etf_trackingerror_timeperiod,
                 etf_trackingerror_year DESC,
                 CASE etf_trackingerror_month
                     WHEN 'Jan' THEN 1 WHEN 'Feb' THEN 2 WHEN 'Mar' THEN 3
                     WHEN 'Apr' THEN 4 WHEN 'May' THEN 5 WHEN 'Jun' THEN 6
                     WHEN 'Jul' THEN 7 WHEN 'Aug' THEN 8 WHEN 'Sep' THEN 9
                     WHEN 'Oct' THEN 10 WHEN 'Nov' THEN 11 WHEN 'Dec' THEN 12
                 END DESC
    """
    try:
        df = pd.read_sql(query, engine)
    finally:
        engine.dispose()

    grouped = defaultdict(lambda: defaultdict(list))
    for row in df.to_dict(orient="records"):
        grouped[row["etf_id"]][row["etf_trackingerror_timeperiod"]].append({
            "value": row["etf_trackingerror_value"],
            "month": row["etf_trackingerror_month"],
            "year": row["etf_trackingerror_year"]
        })
    return dict(grouped)


# -------------------------
# Expense Ratio
# -------------------------
def fetch_latest_expense_ratio(dbconnection):
    engine = create_engine(dbconnection)
    query = """
       SELECT e1.etf_id, e1.etf_expenseratio_value
        FROM etf_expenseratio e1
        INNER JOIN (
            SELECT etf_id,
                   MAX(CONCAT(
                       etf_expenseratioyear,
                       LPAD(
                           CASE etf_expenseratiomonth
                               WHEN 'Jan' THEN 1 WHEN 'Feb' THEN 2 WHEN 'Mar' THEN 3
                               WHEN 'Apr' THEN 4 WHEN 'May' THEN 5 WHEN 'Jun' THEN 6
                               WHEN 'Jul' THEN 7 WHEN 'Aug' THEN 8 WHEN 'Sep' THEN 9
                               WHEN 'Oct' THEN 10 WHEN 'Nov' THEN 11 WHEN 'Dec' THEN 12
                           END, 2, '0'
                       )
                   )) AS max_period
            FROM etf_expenseratio
            GROUP BY etf_id
        ) e2 ON e1.etf_id = e2.etf_id
           AND CONCAT(
               e1.etf_expenseratioyear,
               LPAD(
                   CASE e1.etf_expenseratiomonth
                       WHEN 'Jan' THEN 1 WHEN 'Feb' THEN 2 WHEN 'Mar' THEN 3
                       WHEN 'Apr' THEN 4 WHEN 'May' THEN 5 WHEN 'Jun' THEN 6
                       WHEN 'Jul' THEN 7 WHEN 'Aug' THEN 8 WHEN 'Sep' THEN 9
                       WHEN 'Oct' THEN 10 WHEN 'Nov' THEN 11 WHEN 'Dec' THEN 12
                   END, 2, '0'
               )
           ) = e2.max_period;
  
    """
    try:
        df = pd.read_sql(query, engine)
    finally:
        engine.dispose()
    return {row["etf_id"]: row["etf_expenseratio_value"] for _, row in df.iterrows()}


def fetch_expense_ratio_history(dbconnection):
    engine = create_engine(dbconnection)
    query = """
         SELECT etf_id, etf_expenseratio_value, etf_expenseratiomonth, etf_expenseratioyear
        FROM etf_expenseratio
        ORDER BY etf_id, etf_expenseratioyear DESC, 
                 CASE etf_expenseratiomonth
                     WHEN 'Jan' THEN 1 WHEN 'Feb' THEN 2 WHEN 'Mar' THEN 3
                     WHEN 'Apr' THEN 4 WHEN 'May' THEN 5 WHEN 'Jun' THEN 6
                     WHEN 'Jul' THEN 7 WHEN 'Aug' THEN 8 WHEN 'Sep' THEN 9
                     WHEN 'Oct' THEN 10 WHEN 'Nov' THEN 11 WHEN 'Dec' THEN 12
                 END DESC
    """
    try:
        df = pd.read_sql(query, engine)
    finally:
        engine.dispose()

    grouped = defaultdict(list)
    for row in df.to_dict(orient="records"):
        grouped[row["etf_id"]].append({
            "value": row["etf_expenseratio_value"],
            "month": row["etf_expenseratiomonth"],
            "year": row["etf_expenseratioyear"]
        })
    return dict(grouped)


# -------------------------
# AUM
# -------------------------
def fetch_latest_aum(dbconnection):
    engine = create_engine(dbconnection)
    query = """
        SELECT a1.etf_id, a1.etf_aum
        FROM etf_aum a1
        INNER JOIN (
            SELECT etf_id,
                   MAX(CONCAT(
                       etf_aum_year,
                       LPAD(
                           CASE etf_aum_month
                               WHEN 'Jan' THEN 1 WHEN 'Feb' THEN 2 WHEN 'Mar' THEN 3
                               WHEN 'Apr' THEN 4 WHEN 'May' THEN 5 WHEN 'Jun' THEN 6
                               WHEN 'Jul' THEN 7 WHEN 'Aug' THEN 8 WHEN 'Sep' THEN 9
                               WHEN 'Oct' THEN 10 WHEN 'Nov' THEN 11 WHEN 'Dec' THEN 12
                           END, 2, '0'
                       )
                   )) AS max_period
            FROM etf_aum
            GROUP BY etf_id
        ) a2 ON a1.etf_id = a2.etf_id
           AND CONCAT(
               a1.etf_aum_year,
               LPAD(
                   CASE a1.etf_aum_month
                       WHEN 'Jan' THEN 1 WHEN 'Feb' THEN 2 WHEN 'Mar' THEN 3
                       WHEN 'Apr' THEN 4 WHEN 'May' THEN 5 WHEN 'Jun' THEN 6
                       WHEN 'Jul' THEN 7 WHEN 'Aug' THEN 8 WHEN 'Sep' THEN 9
                       WHEN 'Oct' THEN 10 WHEN 'Nov' THEN 11 WHEN 'Dec' THEN 12
                   END, 2, '0'
               )
           ) = a2.max_period;
    """
    try:
        df = pd.read_sql(query, engine)
    finally:
        engine.dispose()
    return {row["etf_id"]: row["etf_aum"] for _, row in df.iterrows()}


def fetch_aum_history(dbconnection):
    engine = create_engine(dbconnection)
    query = """
        SELECT etf_id, etf_aum, etf_aum_month, etf_aum_year
        FROM etf_aum
        ORDER BY etf_id, etf_aum_year DESC, 
                 CASE etf_aum_month
                     WHEN 'Jan' THEN 1 WHEN 'Feb' THEN 2 WHEN 'Mar' THEN 3
                     WHEN 'Apr' THEN 4 WHEN 'May' THEN 5 WHEN 'Jun' THEN 6
                     WHEN 'Jul' THEN 7 WHEN 'Aug' THEN 8 WHEN 'Sep' THEN 9
                     WHEN 'Oct' THEN 10 WHEN 'Nov' THEN 11 WHEN 'Dec' THEN 12
                 END DESC
    """
    try:
        df = pd.read_sql(query, engine)
    finally:
        engine.dispose()

    grouped = defaultdict(list)
    for row in df.to_dict(orient="records"):
        grouped[row["etf_id"]].append({
            "aum": row["etf_aum"],
            "month": row["etf_aum_month"],
            "year": row["etf_aum_year"]
        })
    return dict(grouped)


# -------------------------
# Summary Builders
# -------------------------
def compute_fundhouse_summary(etfs):
    grouped = defaultdict(list)
    for etf in etfs:
        grouped[etf['etf_fundhouse_name']].append(etf)

    result = []
    for name, etf_list in grouped.items():
        count = len(etf_list)
        aum = sum(float(etf.get('etf_aum', 0) or 0) for etf in etf_list)
        perf = sum(float(etf.get('etf_return_1y', 0) or 0) for etf in etf_list) / count if count else 0
        result.append({
            "name": name,
            "count": count,
            "aum": round(aum),
            "performance": round(perf, 1)
        })
    return sorted(result, key=lambda x: x['name'])


def compute_categories_summary(etfs):
    category_counts = defaultdict(int)
    for etf in etfs:
        category_name = etf.get('asset_info', 'Unknown')
        category_counts[category_name] += 1
    return [{'name': name, 'count': count} for name, count in sorted(category_counts.items())]


# -------------------------
# Template Rendering
# -------------------------
def render_template(
    etfs,
    summary,
    categories,
    fund_houses,
    etfs_aum_latest,
    etfs_expenseratio_latest,
    etfs_trackingerror_latest,
    etfs_aum_history,
    etfs_expenseratio_history,
    etfs_trackingerror_history
):
    code_dir      = Path(__file__).resolve().parent
    templates_dir = code_dir / "templates"
    env           = Environment(loader=FileSystemLoader(templates_dir))
    template      = env.get_template("index_template.html")

    total_etfs, total_categories, total_funds = summary

    # Build a pure Python dict for history
    etf_data_history = {
        e['etf_id']: {
            "aum": etfs_aum_history.get(e['etf_id'], []),
            "expense": etfs_expenseratio_history.get(e['etf_id'], []),
            "te": etfs_trackingerror_history.get(e['etf_id'], {})
        } for e in etfs
    }

    html = template.render(
        etfs=etfs,
        total_etfs=total_etfs,
        total_categories=total_categories,
        total_funds=total_funds,
        categories=categories,
        fund_houses=fund_houses,
        etfs_aum_latest=etfs_aum_latest,
        etfs_expenseratio_latest=etfs_expenseratio_latest,
        etfs_trackingerror_latest=etfs_trackingerror_latest,
        etf_data_history=etf_data_history
    )

    # Save rendered file
    project_root = code_dir.parent.parent
    output_dir   = project_root / "output"
    output_dir.mkdir(exist_ok=True)

    (output_dir / "index.html").write_text(html, encoding="utf-8")
    print("Rendered → output/index.html")

# -------------------------
# Asset Copy
# -------------------------
def copy_assets():
    code_dir = Path(__file__).resolve().parent
    static_css_src = code_dir / "static" / "css" / "etf_site.css"
    dynamic_js_src = code_dir / "static" / "js" / "etf_site.js"

    css_dst_dir = code_dir.parent.parent / "output" / "css"
    css_dst_dir.mkdir(parents=True, exist_ok=True)
    dynamic_js_dst = code_dir.parent.parent / "output"

    if static_css_src.exists():
        shutil.copy(static_css_src, css_dst_dir / "etf_site.css")
        print(f"Copied CSS → output/css/etf_site.css")
    else:
        print(f"WARNING: {static_css_src} not found, skipping CSS copy")

    if dynamic_js_src.exists():
        shutil.copy(dynamic_js_src, dynamic_js_dst / "etf_site.js")
        print(f"Copied JS → output/etf_site.js")
    else:
        print(f"WARNING: {dynamic_js_src} not found, skipping JS copy")


# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    dburl = fetch_db_connection()
    etfs = fetch_etf_data(dburl)
    etfs_trackingerror_latest = fetch_latest_tracking_error(dburl)
    etfs_trackingerror_history = fetch_tracking_error_history(dburl)
    etfs_aum_latest = fetch_latest_aum(dburl)
    etfs_aum_history = fetch_aum_history(dburl)
    etfs_expenseratio_latest = fetch_latest_expense_ratio(dburl)
    etfs_expenseratio_history = fetch_expense_ratio_history(dburl)
    summary = compute_summary(etfs)
    fund_houses = compute_fundhouse_summary(etfs)
    categories = compute_categories_summary(etfs)
    

    render_template(
        etfs,
        summary,
        categories,
        fund_houses,
        etfs_aum_latest,
        etfs_expenseratio_latest,
        etfs_trackingerror_latest,
        etfs_aum_history,
        etfs_expenseratio_history,
        etfs_trackingerror_history
    )
    copy_assets()
