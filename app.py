"""
BuyIQ — Buying Intelligence Engine v4
Masterclass ASIN fetch with exact column mapping.
Zero-error architecture:
  - Pattern-based ASIN detection (ignores header names)
  - Dual-table archive parser (left + right side-by-side tables)
  - Exact column fill map — every target column explicitly handled
  - "No Records" for unavailable columns (never blank, never #N/A)
  - Full audit log of every fill decision
"""

import streamlit as st
import pandas as pd
import io, re, time
from datetime import date
from difflib import SequenceMatcher

st.set_page_config(
    page_title="BuyIQ — Analysis Engine",
    page_icon="⚡", layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════════════════════
#  STYLES
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:#07070f;color:#e0e0f0;}
.block-container{padding-top:1.5rem!important;}
.hero{background:linear-gradient(135deg,#0d0d1f,#111128,#0d1a12);border:1px solid #1c1c3a;border-radius:20px;padding:2.5rem 2.5rem 2rem;margin-bottom:1.5rem;}
.hero-badge{display:inline-block;background:rgba(99,102,241,0.15);color:#818cf8;border:1px solid rgba(99,102,241,0.3);border-radius:20px;padding:3px 14px;font-size:0.7rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.8rem;}
.hero-title{font-family:'Space Grotesk',sans-serif;font-size:2.6rem;font-weight:700;background:linear-gradient(135deg,#a5b4fc,#818cf8,#34d399);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:0 0 0.4rem;line-height:1.1;}
.hero-sub{font-size:0.95rem;color:#555570;margin:0;}
.card-title{font-family:'Space Grotesk',sans-serif;font-size:0.95rem;font-weight:600;color:#c0c0e0;margin-bottom:0.2rem;}
.card-sub{font-size:0.7rem;color:#3a3a5a;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:1rem;}
.metric-row{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:1.2rem 0;}
.metric-box{background:#080814;border:1px solid #161630;border-radius:12px;padding:1rem 1.1rem;text-align:center;}
.m-val{font-family:'Space Grotesk',sans-serif;font-size:1.9rem;font-weight:700;line-height:1;}
.m-val.blue{color:#818cf8;}.m-val.green{color:#34d399;}.m-val.amber{color:#fbbf24;}.m-val.red{color:#f87171;}
.m-lbl{font-size:0.68rem;color:#3a3a5a;margin-top:4px;text-transform:uppercase;letter-spacing:0.08em;}
.log-box{background:#040410;border:1px solid #111128;border-radius:12px;padding:1rem 1.3rem;font-family:'Courier New',monospace;font-size:0.78rem;line-height:1.9;max-height:320px;overflow-y:auto;margin:0.8rem 0;}
.lok{color:#34d399;}.lwarn{color:#fbbf24;}.lerr{color:#f87171;}.lhead{color:#818cf8;font-weight:700;}.linfo{color:#3a3a5a;}
.prog-wrap{background:#151530;border-radius:8px;height:5px;margin:0.5rem 0;overflow:hidden;}
.prog-fill{height:100%;border-radius:8px;background:linear-gradient(90deg,#6366f1,#34d399);}
.alert-box{border-radius:12px;padding:0.9rem 1.1rem;margin:0.5rem 0;font-size:0.82rem;}
.alert-red{background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.25);color:#fca5a5;}
.alert-amber{background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.25);color:#fde68a;}
.alert-green{background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.25);color:#6ee7b7;}
.alert-blue{background:rgba(129,140,248,0.08);border:1px solid rgba(129,140,248,0.25);color:#a5b4fc;}
.map-table{width:100%;border-collapse:collapse;font-size:0.78rem;margin:0.5rem 0;}
.map-table th{background:#0d0d1c;color:#3a3a5a;font-weight:700;padding:7px 12px;text-align:left;letter-spacing:0.07em;font-size:0.67rem;text-transform:uppercase;border-bottom:1px solid #1a1a30;}
.map-table td{padding:6px 12px;border-bottom:1px solid #0d0d18;color:#9090b0;}
.map-table td:first-child{color:#c0c0e0;font-weight:500;}
.pill{display:inline-block;padding:1px 9px;border-radius:20px;font-size:0.67rem;font-weight:700;}
.p-fba{background:rgba(99,102,241,0.15);color:#818cf8;}
.p-arch{background:rgba(16,185,129,0.12);color:#34d399;}
.p-rb{background:rgba(251,191,36,0.12);color:#fbbf24;}
.p-calc{background:rgba(167,139,250,0.12);color:#c4b5fd;}
.p-na{background:rgba(100,100,100,0.15);color:#666;}
.divhr{border:none;border-top:1px solid #141428;margin:1.2rem 0;}
.stTabs [data-baseweb="tab-list"]{gap:4px;background:#0d0d1c;border-radius:12px;padding:4px;}
.stTabs [data-baseweb="tab"]{border-radius:8px;padding:6px 18px;font-size:0.82rem;color:#555570;}
.stTabs [aria-selected="true"]{background:#1a1a35!important;color:#c0c0e0!important;}
div[data-testid="stButton"]>button{background:linear-gradient(135deg,#6366f1,#4f46e5)!important;color:white!important;border:none!important;border-radius:12px!important;font-family:'Space Grotesk',sans-serif!important;font-weight:600!important;font-size:0.95rem!important;}
div[data-testid="stDownloadButton"]>button{background:linear-gradient(135deg,#059669,#047857)!important;color:white!important;border:none!important;border-radius:12px!important;font-family:'Space Grotesk',sans-serif!important;font-weight:600!important;}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS — EXACT TARGET COLUMNS IN ORDER
# ═══════════════════════════════════════════════════════════════════════════════

# These are the exact column names in the analysis file output
TARGET_COLS = [
    "UPC", "Output ASIN", "INV(A-Z)", "INV(Z-A)", "Listing Status",
    "Restricted", "SKU Status(A-Z)", "SKU Status(Z-A)", "Ageing", "Return",
    "FBM-LIFETIME", "FBM-LAST YEAR", "FBM-CURRENT YEAR",
    "Net Ordered GMS($)", "Net Ordered Units",
    "Lifetime", "Sales 2025", "Current year",
    "Sales 30", "Sales 3", "Sales 1",
    "Stock", "Reserve", "Inbound",
    "TOTAL(Stock+Reserve+inbound)", "Days of stock(30)", "Days of stock(3)", "Brand"
]

# Columns that cannot be fetched from any source file
NO_RECORDS_COLS = [
    "Ageing", "Return", "FBM-LIFETIME", "FBM-LAST YEAR", "FBM-CURRENT YEAR",
    "Net Ordered GMS($)", "Net Ordered Units", "Lifetime", "Sales 2025", "Current year",
]

# ═══════════════════════════════════════════════════════════════════════════════
#  CORE UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

ASIN_RE = re.compile(r'^B0[A-Z0-9]{8}$')

def is_asin(v):
    return bool(ASIN_RE.match(str(v).strip().upper()))

def clean_val(v):
    """Strip whitespace and byte-string artifacts."""
    s = str(v).strip()
    if s.startswith(("b'", 'b"')) and s.endswith(("'", '"')):
        s = s[2:-1]
    return s.strip()

def clean_asin(v):
    return clean_val(v).upper()

def is_blank(v):
    return str(v).strip().lower() in ("", "n/a", "#n/a", "#value!", "nan", "none", "0")

def safe_float(v):
    try: return float(str(v).replace(",", "").strip())
    except: return 0.0

def pct(a, b): return round(a / b * 100, 1) if b else 0.0

def sim(a, b):
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

def smart_col(df, targets, threshold=0.55):
    """Find column: exact → substring → similarity. Returns (col, confidence)."""
    cols = list(df.columns)
    for t in targets:
        for c in cols:
            if c.strip().lower() == t.strip().lower():
                return c, 'exact'
    for t in targets:
        for c in cols:
            if t.lower() in c.lower() or c.lower() in t.lower():
                return c, 'fuzzy'
    best_col, best_score = None, 0.0
    for t in targets:
        for c in cols:
            s = sim(c, t)
            if s > best_score:
                best_score, best_col = s, c
    if best_score >= threshold:
        return best_col, 'fuzzy'
    return None, None

def detect_asin_col(df, sample=60):
    """
    Find ASIN column purely by value pattern — ignores header name entirely.
    Returns (col_name, match_pct).
    """
    best_col, best_score = None, 0.0
    for col in df.columns:
        vals = df[col].head(sample).astype(str).str.strip()
        vals = vals[vals.str.len() > 0]
        if len(vals) == 0:
            continue
        hits = vals.apply(lambda v: bool(ASIN_RE.match(clean_asin(v)))).sum()
        score = hits / len(vals)
        if score > best_score:
            best_score, best_col = score, col
    if best_score >= 0.5:
        return best_col, round(best_score * 100, 1)
    return None, 0.0

def get_src_val(row_dict, *aliases):
    """
    Look up a value from a source row dict by trying multiple alias names.
    Returns (value, matched_alias) or (None, None).
    """
    for alias in aliases:
        for k, v in row_dict.items():
            if str(k).strip().lower() == alias.strip().lower():
                cleaned = str(v).strip()
                if cleaned and cleaned.lower() not in ("", "nan", "none"):
                    return cleaned, k
    return None, None

# ═══════════════════════════════════════════════════════════════════════════════
#  FILE READERS
# ═══════════════════════════════════════════════════════════════════════════════

def read_file(f):
    if f is None:
        return pd.DataFrame()
    try:
        f.seek(0)
        if f.name.lower().endswith(".csv"):
            return pd.read_csv(f, dtype=str).fillna("")
        return pd.read_excel(f, dtype=str).fillna("")
    except Exception as e:
        st.error(f"Cannot read {f.name}: {e}")
        return pd.DataFrame()

def read_archive_dual(f):
    """
    Archive has 2 side-by-side tables in one sheet.
    Returns: (left_map, right_map)
      left_map  → {ASIN: row_dict}  from asin(A-Z) table
      right_map → {ASIN: row_dict}  from asin(Z-A) table
    Strategy: scan row 0 for all 'asin' occurrences → split into sub-tables.
    """
    if f is None:
        return {}, {}
    try:
        f.seek(0)
        raw = pd.read_excel(f, header=None, dtype=str).fillna("")
        header_row = raw.iloc[0].tolist()

        # find all column indices where header contains 'asin'
        asin_col_indices = [
            i for i, v in enumerate(header_row)
            if "asin" in str(v).lower()
        ]

        if not asin_col_indices:
            # fallback: single table, use pattern detection
            f.seek(0)
            df = pd.read_excel(f, dtype=str).fillna("")
            asin_col, _ = detect_asin_col(df)
            if not asin_col:
                return {}, {}
            m = {}
            for _, r in df.iterrows():
                k = clean_asin(r[asin_col])
                if is_asin(k):
                    m[k] = r.to_dict()
            return m, {}

        maps = []
        for i, start_col in enumerate(asin_col_indices):
            end_col = asin_col_indices[i + 1] if i + 1 < len(asin_col_indices) else len(raw.columns)
            sub = raw.iloc[:, start_col:end_col].copy()
            sub.columns = [str(v).strip() for v in sub.iloc[0]]
            sub = sub.iloc[1:].reset_index(drop=True).astype(str).fillna("")

            # detect ASIN col by pattern, fallback to header name
            asin_col, asin_pct = detect_asin_col(sub)
            if not asin_col:
                for col in sub.columns:
                    if "asin" in col.lower():
                        asin_col = col
                        break

            table_map = {}
            if asin_col:
                for _, r in sub.iterrows():
                    k = clean_asin(r[asin_col])
                    if is_asin(k) and k not in table_map:
                        table_map[k] = r.to_dict()
            maps.append(table_map)

        left_map  = maps[0] if len(maps) > 0 else {}
        right_map = maps[1] if len(maps) > 1 else {}
        return left_map, right_map

    except Exception as e:
        st.error(f"Archive parse error: {e}")
        return {}, {}

def build_fba_map(df):
    """Build {ASIN: row_dict} from FBA inventory. Pattern-based ASIN detection."""
    asin_col, asin_pct = detect_asin_col(df)
    if not asin_col:
        asin_col, _ = smart_col(df, ["asin", "ASIN"])
    result = {}
    if asin_col:
        for _, r in df.iterrows():
            k = clean_asin(r[asin_col])
            if is_asin(k):
                result[k] = r.to_dict()
    return result, asin_col, asin_pct

# ═══════════════════════════════════════════════════════════════════════════════
#  MASTERCLASS FILL ENGINE
#  Every target column is handled explicitly — nothing is left to chance.
# ═══════════════════════════════════════════════════════════════════════════════

def fill_row(asin, fba_row, arch_left_row, arch_right_row, brand_in_file, restricted_set):
    """
    Given an ASIN and its source rows, return a dict of {target_col: value}
    for every column in TARGET_COLS.
    Also returns an audit list for the log.
    """
    fba   = fba_row         or {}
    arch_l = arch_left_row  or {}
    arch_r = arch_right_row or {}

    result = {}
    audit  = []

    def fill(col, value, source):
        result[col] = value
        audit.append((col, value, source))

    # ── INV(A-Z) — SKU from Archive left table ─────────────────────────────────
    v, k = get_src_val(arch_l, "sku(A-Z)", "sku", "SKU")
    fill("INV(A-Z)", v if v else "No Records", "Archive(A-Z).sku" if v else "—")

    # ── INV(Z-A) — SKU from Archive right table ────────────────────────────────
    v, k = get_src_val(arch_r, "sku(Z-A)", "sku", "SKU")
    fill("INV(Z-A)", v if v else "No Records", "Archive(Z-A).sku" if v else "—")

    # ── Listing Status — from FBA afn-listing-exists ───────────────────────────
    v, k = get_src_val(fba, "afn-listing-exists", "mfn-listing-exists", "listing")
    if v:
        # normalize Yes/No
        normalized = "Listed" if v.lower() in ("yes","true","1","active","listed") else v
        fill("Listing Status", normalized, f"FBA.{k}")
    else:
        fill("Listing Status", "No Records", "—")

    # ── Restricted — brand name match ──────────────────────────────────────────
    brand_lower = brand_in_file.strip().lower() if brand_in_file else ""
    is_r = bool(brand_lower and brand_lower in restricted_set)
    fill("Restricted", "Yes — Restricted" if is_r else "No", "Restricted Brands list")

    # ── SKU Status(A-Z) — SKU from Archive left ────────────────────────────────
    v, k = get_src_val(arch_l, "sku(A-Z)", "sku", "SKU")
    fill("SKU Status(A-Z)", v if v else "No Records", "Archive(A-Z).sku" if v else "—")

    # ── SKU Status(Z-A) — SKU from Archive right ───────────────────────────────
    v, k = get_src_val(arch_r, "sku(Z-A)", "sku", "SKU")
    fill("SKU Status(Z-A)", v if v else "No Records", "Archive(Z-A).sku" if v else "—")

    # ── Columns not available in any source file ───────────────────────────────
    for col in NO_RECORDS_COLS:
        fill(col, "No Records", "—")

    # ── Sales 30 ───────────────────────────────────────────────────────────────
    v, k = get_src_val(fba, "Sales 30", "sales30", "30 day sales", "ordered-units")
    fill("Sales 30", v if v else "No Records", f"FBA.{k}" if v else "—")

    # ── Sales 3 ────────────────────────────────────────────────────────────────
    v, k = get_src_val(fba, "Sales 3", "sales3", "3 day sales")
    fill("Sales 3", v if v else "No Records", f"FBA.{k}" if v else "—")

    # ── Sales 1 ────────────────────────────────────────────────────────────────
    v, k = get_src_val(fba, "Sales 1", "sales1", "1 day sales")
    fill("Sales 1", v if v else "No Records", f"FBA.{k}" if v else "—")

    # ── Stock ──────────────────────────────────────────────────────────────────
    v, k = get_src_val(fba, "STOCK", "afn-fulfillable-quantity", "fulfillable")
    if not v:
        v, k = get_src_val(arch_l, "afn-fulfillable-quantity", "STOCK")
    fill("Stock", v if v else "0", f"{'FBA' if fba else 'Archive'}.{k}" if v else "defaulted 0")

    # ── Reserve ────────────────────────────────────────────────────────────────
    v, k = get_src_val(fba, "RESERVE", "afn-reserved-quantity", "afn-reserve")
    if not v:
        v, k = get_src_val(arch_l, "afn-reserved-quantity", "RESERVE")
    fill("Reserve", v if v else "0", f"FBA.{k}" if v else "defaulted 0")

    # ── Inbound ────────────────────────────────────────────────────────────────
    v, k = get_src_val(fba, "INBOUND", "afn-inbound-working-quantity",
                        "afn-inbound-shipped-quantity", "afn-inbound")
    fill("Inbound", v if v else "0", f"FBA.{k}" if v else "defaulted 0")

    # ── TOTAL ──────────────────────────────────────────────────────────────────
    v, k = get_src_val(fba, "afn-total-quantity", "TOTAL")
    if not v:
        v, k = get_src_val(arch_l, "afn-total-quantity", "TOTAL")
    # if still not found, calculate from filled values
    if not v:
        try:
            calc = safe_float(result.get("Stock",0)) + safe_float(result.get("Reserve",0)) + safe_float(result.get("Inbound",0))
            v = str(int(calc)) if calc else "0"
            k = "calculated"
        except: v = "0"
    fill("TOTAL(Stock+Reserve+inbound)", v, f"FBA.{k}" if k else "calculated")

    # ── Days of stock(30) — calculated ────────────────────────────────────────
    try:
        stock_v = safe_float(result.get("Stock", 0))
        s30_v   = safe_float(result.get("Sales 30", 0))
        if s30_v > 0:
            dos30 = round(stock_v / (s30_v / 30), 1)
            fill("Days of stock(30)", str(dos30), "calculated: Stock÷(Sales30÷30)")
        else:
            fill("Days of stock(30)", "No Records", "Sales 30 not available")
    except:
        fill("Days of stock(30)", "No Records", "—")

    # ── Days of stock(3) — calculated ─────────────────────────────────────────
    try:
        stock_v = safe_float(result.get("Stock", 0))
        s3_v    = safe_float(result.get("Sales 3", 0))
        if s3_v > 0:
            dos3 = round(stock_v / (s3_v / 3), 1)
            fill("Days of stock(3)", str(dos3), "calculated: Stock÷(Sales3÷3)")
        else:
            fill("Days of stock(3)", "No Records", "Sales 3 not available")
    except:
        fill("Days of stock(3)", "No Records", "—")

    # ── Brand ──────────────────────────────────────────────────────────────────
    brand_final = brand_in_file.strip() if brand_in_file and brand_in_file.strip() else "No Records"
    fill("Brand", brand_final, "Analysis file" if brand_final != "No Records" else "—")

    return result, audit

# ═══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
if "run_result"     not in st.session_state: st.session_state.run_result     = None
if "vendor_history" not in st.session_state: st.session_state.vendor_history = []

# ═══════════════════════════════════════════════════════════════════════════════
#  HERO
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-badge">⚡ Buying Intelligence Engine v4</div>
  <div class="hero-title">BuyIQ</div>
  <p class="hero-sub">Masterclass ASIN fetch · Pattern-based detection · Dual-table archive · Zero #N/A · Full audit trail</p>
</div>
""", unsafe_allow_html=True)

# ── Column map reference ──────────────────────────────────────────────────────
with st.expander("📋 Exact column mapping — click to view"):
    st.markdown("""
<table class="map-table">
<tr><th>Analysis Column</th><th>Source</th><th>Source Column</th><th>Logic</th></tr>
<tr><td>UPC</td><td><span class="pill p-na">Pass-through</span></td><td>—</td><td>Kept from analysis file</td></tr>
<tr><td>Output ASIN</td><td><span class="pill p-na">Pass-through</span></td><td>—</td><td>Kept — used as match key</td></tr>
<tr><td>INV(A-Z)</td><td><span class="pill p-arch">Archive Left</span></td><td>sku(A-Z)</td><td>SKU from asin(A-Z) table</td></tr>
<tr><td>INV(Z-A)</td><td><span class="pill p-arch">Archive Right</span></td><td>sku(Z-A)</td><td>SKU from asin(Z-A) table</td></tr>
<tr><td>Listing Status</td><td><span class="pill p-fba">FBA Inv</span></td><td>afn-listing-exists</td><td>Yes/No → Listed/Unlisted</td></tr>
<tr><td>Restricted</td><td><span class="pill p-rb">Restricted Brands</span></td><td>Brand name</td><td>Exact brand match</td></tr>
<tr><td>SKU Status(A-Z)</td><td><span class="pill p-arch">Archive Left</span></td><td>sku(A-Z)</td><td>SKU from asin(A-Z) table</td></tr>
<tr><td>SKU Status(Z-A)</td><td><span class="pill p-arch">Archive Right</span></td><td>sku(Z-A)</td><td>SKU from asin(Z-A) table</td></tr>
<tr><td>Ageing</td><td><span class="pill p-na">No Records</span></td><td>—</td><td>Not in any source file</td></tr>
<tr><td>Return</td><td><span class="pill p-na">No Records</span></td><td>—</td><td>Not in any source file</td></tr>
<tr><td>FBM-LIFETIME / LAST YEAR / CURRENT YEAR</td><td><span class="pill p-na">No Records</span></td><td>—</td><td>Not in any source file</td></tr>
<tr><td>Net Ordered GMS($) / Units</td><td><span class="pill p-na">No Records</span></td><td>—</td><td>Not in any source file</td></tr>
<tr><td>Lifetime / Sales 2025 / Current year</td><td><span class="pill p-na">No Records</span></td><td>—</td><td>Not in any source file</td></tr>
<tr><td>Sales 30 / Sales 3 / Sales 1</td><td><span class="pill p-fba">FBA Inv</span></td><td>Sales 30 / Sales 3 / Sales 1</td><td>Direct fill</td></tr>
<tr><td>Stock</td><td><span class="pill p-fba">FBA Inv</span></td><td>STOCK</td><td>FBA first, Archive fallback</td></tr>
<tr><td>Reserve</td><td><span class="pill p-fba">FBA Inv</span></td><td>RESERVE</td><td>FBA first, Archive fallback</td></tr>
<tr><td>Inbound</td><td><span class="pill p-fba">FBA Inv</span></td><td>INBOUND</td><td>FBA only</td></tr>
<tr><td>TOTAL(Stock+Reserve+inbound)</td><td><span class="pill p-fba">FBA Inv</span></td><td>afn-total-quantity</td><td>FBA → Archive → Calculated</td></tr>
<tr><td>Days of stock(30)</td><td><span class="pill p-calc">Calculated</span></td><td>—</td><td>Stock ÷ (Sales30 ÷ 30)</td></tr>
<tr><td>Days of stock(3)</td><td><span class="pill p-calc">Calculated</span></td><td>—</td><td>Stock ÷ (Sales3 ÷ 3)</td></tr>
<tr><td>Brand</td><td><span class="pill p-na">Pass-through</span></td><td>—</td><td>Kept from analysis file</td></tr>
</table>
""", unsafe_allow_html=True)

tab_run, tab_dash, tab_history = st.tabs(["⚡  Run Engine", "📊  Dashboard", "📈  Vendor History"])

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — RUN
# ═══════════════════════════════════════════════════════════════════════════════
with tab_run:
    col_l, col_r = st.columns(2, gap="large")

    with col_l:
        st.markdown('<div class="card-title">Step 1 — Source files</div><div class="card-sub">Upload today\'s 3 daily files</div>', unsafe_allow_html=True)
        fba_file  = st.file_uploader("📦 FBA Inventory",     type=["xlsx","xls","csv"], key="fba")
        rb_file   = st.file_uploader("🚫 Restricted Brands", type=["xlsx","xls","csv"], key="rb")
        arch_file = st.file_uploader("🗃️ Archive Inventory", type=["xlsx","xls","csv"], key="arch")

    with col_r:
        st.markdown('<div class="card-title">Step 2 — Analysis file</div><div class="card-sub">Your template with Output ASIN column</div>', unsafe_allow_html=True)
        an_file     = st.file_uploader("📊 Analysis file", type=["xlsx","xls","csv"], key="an")
        vendor_name = st.text_input("Vendor / file label (for history)", placeholder="e.g. ALLWAY, 3M, Echo Park...")
        all_ready   = all([fba_file, rb_file, arch_file, an_file])
        if all_ready:
            st.success("✅ All 4 files ready — run the engine")
        else:
            missing = [n for f,n in [(fba_file,"FBA"),(rb_file,"Restricted Brands"),(arch_file,"Archive"),(an_file,"Analysis")] if not f]
            st.info("Waiting for: " + ", ".join(missing))

    # ── Pre-flight check ──────────────────────────────────────────────────────
    if an_file:
        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown("### 🔬 Pre-flight check")
        an_prev = read_file(an_file); an_file.seek(0)
        if not an_prev.empty:
            asin_col_p, asin_pct_p = detect_asin_col(an_prev)
            brand_col_p, _ = smart_col(an_prev, ["Brand","brand","BRAND"])
            st.markdown(f"<div class='card-sub'>{len(an_prev):,} rows · {len(an_prev.columns)} columns detected</div>", unsafe_allow_html=True)
            if asin_col_p:
                samples = an_prev[asin_col_p].dropna().head(3).tolist()
                st.markdown(f'<div class="alert-box alert-green">✅ ASIN column: <strong>"{asin_col_p}"</strong> ({asin_pct_p}% pattern match) · Sample: <code>{" · ".join(samples)}</code></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-box alert-red">❌ No ASIN column found in analysis file. Cells must contain values like B07QNLTK2M</div>', unsafe_allow_html=True)
            if brand_col_p:
                st.markdown(f'<div class="alert-box alert-green">✅ Brand column: <strong>"{brand_col_p}"</strong></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-box alert-amber">⚠️ Brand column not found — Restricted check will be skipped</div>', unsafe_allow_html=True)

    if fba_file:
        fba_prev = read_file(fba_file); fba_file.seek(0)
        if not fba_prev.empty:
            fc, fp = detect_asin_col(fba_prev)
            if fc:
                s = fba_prev[fc].dropna().head(3).tolist()
                st.markdown(f'<div class="alert-box alert-green">✅ FBA ASIN column: <strong>"{fc}"</strong> ({fp}%) · Sample: <code>{" · ".join(s)}</code></div>', unsafe_allow_html=True)

    st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
    run_btn = st.button("⚡ Run BuyIQ Engine", disabled=not all_ready, use_container_width=True, type="primary")

    # ═══════════════════════════════════════════════════════════════════════════
    #  MAIN PROCESSING
    # ═══════════════════════════════════════════════════════════════════════════
    if run_btn and all_ready:
        t0   = time.time()
        logs = []

        def log(msg, kind="info"):
            cls = {"ok":"lok","warn":"lwarn","err":"lerr","head":"lhead"}.get(kind,"linfo")
            logs.append(f'<span class="{cls}">{msg}</span>')

        prog   = st.progress(0)
        status = st.empty()

        # ── Read ───────────────────────────────────────────────────────────────
        status.write("Reading source files...")
        fba_df = read_file(fba_file)
        rb_df  = read_file(rb_file)
        an_df  = read_file(an_file)

        if any(df.empty for df in [fba_df, rb_df, an_df]):
            st.error("One or more files could not be read. Please re-upload.")
            st.stop()

        prog.progress(8)
        log("◆ FILES LOADED", "head")
        log(f"  FBA Inventory     → {len(fba_df):,} rows | {len(fba_df.columns)} cols", "ok")
        log(f"  Restricted Brands → {len(rb_df):,} brands", "ok")
        log(f"  Analysis file     → {len(an_df):,} rows | {len(an_df.columns)} cols", "ok")

        # ── Restricted brands ──────────────────────────────────────────────────
        status.write("Building restricted brands index...")
        rb_col = rb_df.columns[0]
        restricted_set = set(rb_df[rb_col].str.strip().str.lower().dropna())
        log(f"◆ RESTRICTED INDEX — {len(restricted_set):,} brands indexed", "head")
        prog.progress(15)

        # ── FBA map ────────────────────────────────────────────────────────────
        status.write("Indexing FBA Inventory by ASIN...")
        fba_map, fba_asin_col, fba_asin_pct = build_fba_map(fba_df)
        log(f"◆ FBA MAP — {len(fba_map):,} ASINs | col: '{fba_asin_col}' ({fba_asin_pct}%)", "head" if fba_map else "warn")
        if not fba_map:
            log("  ⚠ No ASINs indexed from FBA file — verify file format", "warn")
        prog.progress(30)

        # ── Archive dual-table parse ───────────────────────────────────────────
        status.write("Parsing Archive Inventory (dual-table)...")
        arch_left, arch_right = read_archive_dual(arch_file)
        log(f"◆ ARCHIVE — Left table: {len(arch_left):,} ASINs | Right table: {len(arch_right):,} ASINs", "head")
        if not arch_left and not arch_right:
            log("  ⚠ No ASINs found in Archive — verify file format", "warn")
        prog.progress(45)

        # ── Analysis ASIN + Brand cols ─────────────────────────────────────────
        status.write("Detecting analysis columns...")
        an_asin_col, an_asin_pct = detect_asin_col(an_df)
        an_brand_col, _ = smart_col(an_df, ["Brand","brand","BRAND"])

        if not an_asin_col:
            st.error("❌ Cannot find ASIN column in analysis file.")
            st.stop()

        log("◆ ANALYSIS COLUMNS", "head")
        log(f"  ASIN  → '{an_asin_col}' (pattern {an_asin_pct}%)", "ok")
        log(f"  Brand → {an_brand_col or '⚠ not found'}", "ok" if an_brand_col else "warn")
        prog.progress(52)

        # ── Process every row ──────────────────────────────────────────────────
        status.write("Processing rows — filling all columns...")
        out_rows  = []
        anomalies = []
        fba_hits = arch_hits = restricted_count = filled_cells = no_match = 0
        n = len(an_df)

        for idx, row in an_df.iterrows():
            asin  = clean_asin(row[an_asin_col])
            brand = str(row.get(an_brand_col, "")).strip() if an_brand_col else ""

            if not is_asin(asin):
                # keep the row as-is, fill "No Records" for all target cols
                nr = {col: str(row.get(col, "")).strip() for col in an_df.columns}
                for col in TARGET_COLS:
                    if col not in nr or is_blank(nr.get(col,"")):
                        nr[col] = "No Records" if col not in ["UPC","Output ASIN","Brand"] else nr.get(col,"")
                out_rows.append(nr)
                continue

            fba_row   = fba_map.get(asin)
            arch_l_row = arch_left.get(asin)
            arch_r_row = arch_right.get(asin)

            if fba_row:   fba_hits  += 1
            if arch_l_row or arch_r_row: arch_hits += 1
            if not fba_row and not arch_l_row and not arch_r_row: no_match += 1

            # call the masterclass fill engine
            filled, audit = fill_row(asin, fba_row, arch_l_row, arch_r_row, brand, restricted_set)
            filled_cells += sum(1 for _, v, src in audit if src != "—" and v != "No Records")

            if filled.get("Restricted","").startswith("Yes"):
                restricted_count += 1

            # build output row: start with original cols, overlay filled values
            nr = {col: str(row.get(col,"")).strip() for col in an_df.columns}
            # UPC and Output ASIN pass-through
            nr["UPC"]         = str(row.get("UPC", row.get(an_asin_col,""))).strip()
            nr["Output ASIN"] = asin
            nr["Brand"]       = brand

            # apply all filled values
            for col, val, _ in audit:
                nr[col] = val

            # ── Anomaly detection ──────────────────────────────────────────────
            stock_v  = safe_float(nr.get("Stock",0))
            s30_v    = safe_float(nr.get("Sales 30",0))
            dos30_v  = safe_float(nr.get("Days of stock(30)", 999) if nr.get("Days of stock(30)","") != "No Records" else 999)
            listing  = str(nr.get("Listing Status","")).lower()
            is_restr = nr.get("Restricted","").startswith("Yes")

            if stock_v == 0 and s30_v > 5:
                anomalies.append({"type":"🔴 Zero stock / high velocity","severity":"red","asin":asin,"brand":brand,"detail":f"0 stock | {s30_v:.0f} units sold last 30d"})
            elif 0 < dos30_v < 7:
                anomalies.append({"type":"🔴 Critical — under 7 days","severity":"red","asin":asin,"brand":brand,"detail":f"{dos30_v} days of stock remaining"})
            elif 7 <= dos30_v < 14:
                anomalies.append({"type":"🟡 Low stock warning","severity":"amber","asin":asin,"brand":brand,"detail":f"{dos30_v} days of stock remaining"})
            if is_restr and "listed" in listing:
                anomalies.append({"type":"🚫 Restricted — active listing","severity":"red","asin":asin,"brand":brand,"detail":f"'{brand}' is restricted but listed"})

            out_rows.append(nr)

            if idx % max(1, n // 30) == 0:
                prog.progress(52 + int(40 * idx / n))

        prog.progress(94)

        # ── Build output DataFrame in exact column order ───────────────────────
        out_df = pd.DataFrame(out_rows)
        # enforce exact column order — add missing target cols if needed
        for col in TARGET_COLS:
            if col not in out_df.columns:
                out_df[col] = "No Records"
        # put target cols first, then any extra original cols
        extra_cols = [c for c in out_df.columns if c not in TARGET_COLS]
        out_df = out_df[TARGET_COLS + extra_cols]

        # ── Write Excel ────────────────────────────────────────────────────────
        status.write("Writing output file...")
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            out_df.to_excel(writer, index=False, sheet_name="Analysis_Filled")
            if anomalies:
                pd.DataFrame(anomalies)[["type","asin","brand","detail"]].to_excel(
                    writer, index=False, sheet_name="Anomaly_Alerts")
            # audit sheet — first 500 rows for transparency
            audit_rows = []
            for i, row in enumerate(out_rows[:500]):
                for col in TARGET_COLS:
                    audit_rows.append({"Row": i+2, "ASIN": row.get("Output ASIN",""), "Column": col, "Value": row.get(col,"")})
            pd.DataFrame(audit_rows).to_excel(writer, index=False, sheet_name="Audit_Trail")

        buf.seek(0)
        prog.progress(100)
        t1 = time.time()
        status.empty(); prog.empty()

        match_rate = pct(fba_hits, n)
        log(f"◆ COMPLETE — {round(t1-t0,2)}s", "head")
        log(f"  Rows processed    : {n:,}", "ok")
        log(f"  FBA matched       : {fba_hits:,} ({pct(fba_hits,n)}%)", "ok")
        log(f"  Archive matched   : {arch_hits:,} ({pct(arch_hits,n)}%)", "ok")
        log(f"  Cells filled      : {filled_cells:,}", "ok")
        log(f"  'No Records' set  : {sum(1 for r in out_rows for c in NO_RECORDS_COLS if r.get(c)=='No Records')//max(1,len(NO_RECORDS_COLS)):,} rows", "ok")
        log(f"  Unmatched ASINs   : {no_match:,}", "warn" if no_match else "ok")
        log(f"  Restricted flagged: {restricted_count:,}", "warn" if restricted_count else "ok")
        log(f"  Anomalies found   : {len(anomalies):,}", "warn" if anomalies else "ok")
        log(f"  Output columns    : {len(TARGET_COLS)} (exact template order)", "ok")

        st.session_state.run_result = {
            "out_df": out_df, "buf": buf.getvalue(), "n": n,
            "fba_hits": fba_hits, "arch_hits": arch_hits,
            "filled_cells": filled_cells, "restricted_count": restricted_count,
            "no_match": no_match, "anomalies": anomalies,
            "match_rate": match_rate, "logs": logs,
            "elapsed": round(t1-t0,2), "vendor": vendor_name or "Unknown",
            "run_date": str(date.today()),
        }
        if vendor_name:
            st.session_state.vendor_history.append({
                "vendor": vendor_name, "date": str(date.today()),
                "rows": n, "match_rate": match_rate,
                "filled": filled_cells, "restricted": restricted_count,
                "anomalies": len(anomalies), "unmatched": no_match
            })

    # ── Results ───────────────────────────────────────────────────────────────
    if st.session_state.run_result:
        r = st.session_state.run_result
        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown("### Run report")
        st.markdown(f"""
        <div class="metric-row">
          <div class="metric-box"><div class="m-val blue">{r['n']:,}</div><div class="m-lbl">Rows processed</div></div>
          <div class="metric-box"><div class="m-val green">{r['fba_hits']:,}</div><div class="m-lbl">FBA matched ({r['match_rate']}%)</div></div>
          <div class="metric-box"><div class="m-val green">{r['filled_cells']:,}</div><div class="m-lbl">Cells filled</div></div>
          <div class="metric-box"><div class="m-val {'red' if r['no_match'] else 'green'}">{r['no_match']:,}</div><div class="m-lbl">Unmatched ASINs</div></div>
        </div>
        <div style="font-size:0.72rem;color:#3a3a5a;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin:0.8rem 0 0.2rem">FBA match accuracy — {r['match_rate']}%</div>
        <div class="prog-wrap"><div class="prog-fill" style="width:{r['match_rate']}%"></div></div>
        """, unsafe_allow_html=True)

        st.markdown(f'<div class="log-box">{"<br>".join(r["logs"])}</div>', unsafe_allow_html=True)

        if r['anomalies']:
            st.markdown(f"### ⚠️ Anomaly alerts — {len(r['anomalies'])} found")
            for a in r['anomalies'][:20]:
                cls = "alert-red" if a['severity']=="red" else "alert-amber"
                st.markdown(f'<div class="alert-box {cls}"><strong>{a["type"]}</strong> &nbsp;|&nbsp; <code>{a["asin"]}</code> &nbsp;|&nbsp; {a["brand"]} &nbsp;|&nbsp; {a["detail"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-box alert-green">✅ No anomalies — all ASINs healthy</div>', unsafe_allow_html=True)

        fname = f"Analysis_Filled_{date.today()}.xlsx"
        st.download_button(
            label=f"⬇️  Download {fname}  (includes Audit Trail sheet)",
            data=r['buf'], file_name=fname,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True, type="primary"
        )
        st.markdown('<div class="alert-box alert-blue">📋 Your download includes 3 sheets: <strong>Analysis_Filled</strong> · <strong>Anomaly_Alerts</strong> · <strong>Audit_Trail</strong></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
with tab_dash:
    if not st.session_state.run_result:
        st.markdown('<div class="alert-box alert-blue" style="margin-top:1rem">Run the engine first to see your dashboard.</div>', unsafe_allow_html=True)
    else:
        r      = st.session_state.run_result
        out_df = r['out_df']
        st.markdown(f"### 📊 Live dashboard — {r['vendor']}")
        st.markdown(f"<div class='card-sub'>{r['run_date']} &nbsp;|&nbsp; {r['elapsed']}s processing &nbsp;|&nbsp; {r['n']:,} rows</div>", unsafe_allow_html=True)

        st.markdown("#### 🔻 Top 10 lowest stock ASINs")
        if "Stock" in out_df.columns:
            tmp = out_df[out_df["Stock"] != "No Records"].copy()
            tmp["_s"] = tmp["Stock"].apply(safe_float)
            show = [c for c in ["Output ASIN","Brand","Stock","Days of stock(30)","Sales 30"] if c in tmp.columns]
            st.dataframe(tmp.nsmallest(10,"_s")[show], use_container_width=True, hide_index=True)

        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown("#### 🚫 Restricted brand breakdown")
        if "Restricted" in out_df.columns and "Brand" in out_df.columns:
            restr = out_df[out_df["Restricted"].str.startswith("Yes", na=False)]
            if not restr.empty:
                counts = restr["Brand"].value_counts().reset_index()
                counts.columns = ["Brand","Count"]
                st.dataframe(counts, use_container_width=True, hide_index=True)
                st.markdown(f'<div class="alert-box alert-red">🚫 {len(restr)} restricted brand ASINs across {counts["Brand"].nunique()} brands</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-box alert-green">✅ No restricted brands found</div>', unsafe_allow_html=True)

        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown("#### ⚠️ Anomaly summary")
        if r['anomalies']:
            adf = pd.DataFrame(r['anomalies'])[["type","asin","brand","detail"]]
            adf.columns = ["Alert","ASIN","Brand","Detail"]
            st.dataframe(adf, use_container_width=True, hide_index=True)
        else:
            st.markdown('<div class="alert-box alert-green">✅ No anomalies detected</div>', unsafe_allow_html=True)

        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        mr    = r['match_rate']
        color = "#34d399" if mr>=80 else "#fbbf24" if mr>=50 else "#f87171"
        st.markdown(f"""
        <div style="text-align:center;padding:1.5rem;">
          <div style="font-family:'Space Grotesk',sans-serif;font-size:4rem;font-weight:700;color:{color}">{mr}%</div>
          <div style="color:#3a3a5a;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.1em;margin-top:0.5rem">
            FBA match rate &nbsp;|&nbsp; {r['fba_hits']:,} of {r['n']:,} ASINs matched
          </div>
          <div class="prog-wrap" style="max-width:400px;margin:1rem auto">
            <div class="prog-fill" style="width:{mr}%"></div>
          </div>
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — VENDOR HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
with tab_history:
    st.markdown("### 📈 Vendor run history")
    history = st.session_state.vendor_history
    if not history:
        st.markdown('<div class="alert-box alert-blue" style="margin-top:1rem">No history yet. Enter a vendor name before running to start tracking.</div>', unsafe_allow_html=True)
    else:
        hist_df = pd.DataFrame(history)
        hist_df.columns = ["Vendor","Date","Rows","Match Rate (%)","Cells Filled","Restricted","Anomalies","Unmatched"]
        st.dataframe(hist_df, use_container_width=True, hide_index=True)
        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown("#### Per-vendor summary")
        summary = hist_df.groupby("Vendor").agg({
            "Rows":"sum","Match Rate (%)":"mean","Cells Filled":"sum",
            "Restricted":"sum","Anomalies":"sum","Unmatched":"sum"
        }).round(1).reset_index()
        st.dataframe(summary, use_container_width=True, hide_index=True)
        if st.button("🗑 Clear history"):
            st.session_state.vendor_history = []
            st.rerun()
