# Buying Team — Analysis Auto-Fill Tool

Upload your 3 daily source files + analysis file. Matches on ASIN and fills all missing columns instantly.

## Files in this repo
- `app.py` — main Streamlit app
- `requirements.txt` — Python dependencies

## Deploy on Streamlit Cloud (free)

1. Go to https://github.com and create a new repository (e.g. `buying-tool`)
2. Upload `app.py` and `requirements.txt` to that repo
3. Go to https://streamlit.io/cloud and sign in with GitHub
4. Click **New app** → select your repo → set main file as `app.py`
5. Click **Deploy** — your tool will be live in ~1 minute

## How to use the tool

1. Upload **FBA Inventory** file (xlsx/csv)
2. Upload **Restricted Brands** file (xlsx/csv)
3. Upload **Archive Inventory** file (xlsx/csv)
4. Upload your **Analysis file** (with blank/N/A columns)
5. Click **Match & Fill All Columns**
6. Download the filled Excel file

## What gets filled automatically

- Stock, Reserve, Inbound from FBA Inventory
- Price and totals from FBA & Archive Inventory
- All extra FBA/Archive columns appended automatically
- Restricted Brand column — flags "Yes — Restricted" if brand is in the list
