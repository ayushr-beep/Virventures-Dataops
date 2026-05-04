import streamlit as st
import pandas as pd
import io, re, time
from datetime import date
from difflib import SequenceMatcher

st.set_page_config(page_title="BuyIQ — Analysis Engine", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

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
.log-box{background:#040410;border:1px solid #111128;border-radius:12px;padding:1rem 1.3rem;font-family:'Courier New',monospace;font-size:0.78rem;line-height:1.9;max-height:300px;overflow-y:auto;margin:0.8rem 0;}
.lok{color:#34d399;}.lwarn{color:#fbbf24;}.lerr{color:#f87171;}.lhead{color:#818cf8;font-weight:700;}.linfo{color:#3a3a5a;}
.prog-wrap{background:#151530;border-radius:8px;height:5px;margin:0.5rem 0;overflow:hidden;}
.prog-fill{height:100%;border-radius:8px;background:linear-gradient(90deg,#6366f1,#34d399);}
.alert-box{border-radius:12px;padding:0.9rem 1.1rem;margin:0.5rem 0;font-size:0.82rem;}
.alert-red{background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.25);color:#fca5a5;}
.alert-amber{background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.25);color:#fde68a;}
.alert-green{background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.25);color:#6ee7b7;}
.alert-blue{background:rgba(129,140,248,0.08);border:1px solid rgba(129,140,248,0.25);color:#a5b4fc;}
.divhr{border:none;border-top:1px solid #141428;margin:1.2rem 0;}
.stTabs [data-baseweb="tab-list"]{gap:4px;background:#0d0d1c;border-radius:12px;padding:4px;}
.stTabs [data-baseweb="tab"]{border-radius:8px;padding:6px 18px;font-size:0.82rem;color:#555570;}
.stTabs [aria-selected="true"]{background:#1a1a35!important;color:#c0c0e0!important;}
div[data-testid="stButton"]>button{background:linear-gradient(135deg,#6366f1,#4f46e5)!important;color:white!important;border:none!important;border-radius:12px!important;font-family:'Space Grotesk',sans-serif!important;font-weight:600!important;font-size:0.95rem!important;}
div[data-testid="stDownloadButton"]>button{background:linear-gradient(135deg,#059669,#047857)!important;color:white!important;border:none!important;border-radius:12px!important;font-family:'Space Grotesk',sans-serif!important;font-weight:600!important;}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  CORE UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

ASIN_PATTERN = re.compile(r'^B0[A-Z0-9]{8}$')

def is_asin(v):
    return bool(ASIN_PATTERN.match(str(v).strip().upper()))

def clean_asin(v):
    s = str(v).strip()
    if s.startswith(("b'", 'b"')) and s.endswith(("'", '"')):
        s = s[2:-1]
    return s.strip().upper()

def is_blank(v):
    return str(v).strip().lower() in ("", "n/a", "#n/a", "#value!", "nan", "none")

def safe_float(v, default=0.0):
    try: return float(str(v).replace(",", "").strip())
    except: return default

def pct(a, b): return round(a / b * 100, 1) if b else 0

def similarity(a, b):
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

def smart_col(df, targets, threshold=0.55):
    """Find column by exact → substring → similarity match. Returns (col, confidence)."""
    cols = list(df.columns)
    for t in targets:
        for c in cols:
            if c.strip().lower() == t.strip().lower():
                return c, 'exact'
    for t in targets:
        for c in cols:
            if t.lower() in c.lower() or c.lower() in t.lower():
                return c, 'fuzzy'
    best_col, best_score = None, 0
    for t in targets:
        for c in cols:
            s = similarity(c, t)
            if s > best_score:
                best_score, best_col = s, c
    if best_score >= threshold:
        return best_col, 'fuzzy'
    return None, None

# ── ASIN column detection by VALUE PATTERN ─────────────────────────────────────
def detect_asin_col_by_pattern(df, sample_rows=50):
    """
    Scans every column's values (up to sample_rows).
    Returns the column where ≥60% of non-empty values match ASIN pattern.
    This works regardless of what the column header says.
    """
    best_col, best_score = None, 0
    check = df.head(sample_rows)
    for col in df.columns:
        vals = check[col].dropna().astype(str).str.strip()
        vals = vals[vals != ""]
        if len(vals) == 0:
            continue
        hits = vals.apply(lambda v: bool(ASIN_PATTERN.match(clean_asin(v)))).sum()
        score = hits / len(vals)
        if score > best_score:
            best_score, best_col = score, col
    if best_score >= 0.6:
        return best_col, round(best_score * 100, 1)
    return None, 0

# ── Archive file: read BOTH side-by-side tables ────────────────────────────────
def read_archive(f):
    """
    Archive has 2 tables side by side in one sheet.
    Strategy: read raw with openpyxl, find all header rows that contain 'asin',
    split into sub-tables, return combined unique ASIN map.
    """
    if f is None:
        return {}
    try:
        f.seek(0)
        # read raw — keep all columns, no header assumption
        raw = pd.read_excel(f, header=None, dtype=str).fillna("")

        asin_map = {}
        # find all columns whose row-0 value contains 'asin'
        header_row = raw.iloc[0]
        table_starts = []  # list of col indices where a table begins (has 'asin' in header)

        for col_idx, val in enumerate(header_row):
            if "asin" in str(val).lower():
                table_starts.append(col_idx)

        if not table_starts:
            # fallback: just read normally
            f.seek(0)
            df = pd.read_excel(f, dtype=str).fillna("")
            asin_col, _ = detect_asin_col_by_pattern(df)
            if asin_col:
                for _, r in df.iterrows():
                    k = clean_asin(r[asin_col])
                    if is_asin(k) and k not in asin_map:
                        asin_map[k] = r.to_dict()
            return asin_map

        # for each table start, figure out its column range
        for i, start_col in enumerate(table_starts):
            end_col = table_starts[i + 1] if i + 1 < len(table_starts) else len(raw.columns)
            sub = raw.iloc[:, start_col:end_col].copy()
            sub.columns = sub.iloc[0]   # use first row as header
            sub = sub.iloc[1:].reset_index(drop=True)
            sub = sub.fillna("").astype(str)

            # find ASIN col in this sub-table
            asin_col, conf = detect_asin_col_by_pattern(sub)
            if not asin_col:
                # try header name match
                for col in sub.columns:
                    if "asin" in str(col).lower():
                        asin_col = col
                        break

            if asin_col:
                for _, r in sub.iterrows():
                    k = clean_asin(r[asin_col])
                    if is_asin(k) and k not in asin_map:
                        asin_map[k] = r.to_dict()

        return asin_map

    except Exception as e:
        st.error(f"Archive read error: {e}")
        return {}

# ── Standard file reader ────────────────────────────────────────────────────────
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

# ── Build FBA map ───────────────────────────────────────────────────────────────
def build_fba_map(df):
    asin_col, conf = detect_asin_col_by_pattern(df)
    if not asin_col:
        asin_col, conf = smart_col(df, ["asin", "ASIN"])
    result = {}
    if asin_col:
        for _, r in df.iterrows():
            k = clean_asin(r[asin_col])
            if is_asin(k):
                result[k] = r.to_dict()
    return result, asin_col, conf

# ── Source value lookup ─────────────────────────────────────────────────────────
def get_val(source_row, aliases):
    """Scan source row dict for first matching non-blank alias value."""
    for alias in aliases:
        for k, v in source_row.items():
            if str(k).strip().lower() == alias.strip().lower() and not is_blank(v):
                return v
    return None

# ═══════════════════════════════════════════════════════════════════════════════
#  COLUMN KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════════════════════

AN_BRAND_ALIASES   = ["Brand", "brand", "BRAND"]
AN_STOCK_ALIASES   = ["Stock", "STOCK", "stock qty", "inv stock"]
AN_RESERVE_ALIASES = ["Reserve", "RESERVE", "reserved"]
AN_INBOUND_ALIASES = ["Inbound", "INBOUND", "inbound qty", "afn-inbound"]
AN_TOTAL_ALIASES   = ["TOTAL(Stock+Reserve+inbound)", "TOTAL", "total stock", "total qty"]
AN_RESTR_ALIASES   = ["Restricted", "restricted brand", "brand restricted"]
AN_DOS30_ALIASES   = ["Days of stock(30)", "dos30", "days of stock 30"]
AN_DOS3_ALIASES    = ["Days of stock(3)",  "dos3",  "days of stock 3"]
AN_S30_ALIASES     = ["Sales 30", "sales30", "30 day sales", "Sales30"]
AN_S3_ALIASES      = ["Sales 3",  "sales3",  "3 day sales",  "Sales3"]
AN_LISTING_ALIASES = ["Listing Status", "afn-listing-exists", "mfn-listing-exists", "listing"]

# FBA source column aliases (in order of preference)
FBA_STOCK_SRC   = ["STOCK", "afn-fulfillable-quantity", "fulfillable"]
FBA_RESERVE_SRC = ["RESERVE", "afn-reserved-quantity", "afn-reserve"]
FBA_INBOUND_SRC = ["INBOUND", "afn-inbound-working-quantity", "afn-inbound-shipped-quantity", "afn-inbound"]
FBA_TOTAL_SRC   = ["afn-total-quantity", "TOTAL"]

# Archive source aliases
ARCH_STOCK_SRC   = ["afn-fulfillable-quantity", "STOCK"]
ARCH_RESERVE_SRC = ["afn-reserved-quantity", "afn-reserve", "RESERVE"]
ARCH_TOTAL_SRC   = ["afn-total-quantity", "TOTAL"]

# ═══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
if "run_result"     not in st.session_state: st.session_state.run_result     = None
if "vendor_history" not in st.session_state: st.session_state.vendor_history = []

# ═══════════════════════════════════════════════════════════════════════════════
#  UI
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-badge">⚡ Buying Intelligence Engine v3</div>
  <div class="hero-title">BuyIQ</div>
  <p class="hero-sub">Pattern-based ASIN detection · Dual-table archive parsing · Anomaly alerts · Live dashboard</p>
</div>
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
        st.markdown('<div class="card-title">Step 2 — Analysis file</div><div class="card-sub">File with blank / N/A columns to fill</div>', unsafe_allow_html=True)
        an_file     = st.file_uploader("📊 Analysis file", type=["xlsx","xls","csv"], key="an")
        vendor_name = st.text_input("Vendor name (for history tracking)", placeholder="e.g. ALLWAY, 3M...")

        all_ready = all([fba_file, rb_file, arch_file, an_file])
        if all_ready:
            st.success("✅ All 4 files ready")
        else:
            missing = [n for f, n in [(fba_file,"FBA"),(rb_file,"Restricted Brands"),(arch_file,"Archive"),(an_file,"Analysis")] if not f]
            st.info("Waiting for: " + ", ".join(missing))

    # ── Pre-flight column detection preview ──────────────────────────────────
    if an_file:
        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown("### 🔬 Pre-flight check")
        an_prev = read_file(an_file)
        an_file.seek(0)

        if not an_prev.empty:
            asin_col_prev, asin_pct = detect_asin_col_by_pattern(an_prev)
            st.markdown(f"<div class='card-sub'>Analysis file: {len(an_prev):,} rows · {len(an_prev.columns)} columns</div>", unsafe_allow_html=True)

            if asin_col_prev:
                sample = an_prev[asin_col_prev].dropna().head(3).tolist()
                st.markdown(f'<div class="alert-box alert-green">✅ ASIN column auto-detected: <strong>"{asin_col_prev}"</strong> ({asin_pct}% of values match ASIN pattern)<br>Sample: <code>{" · ".join(sample)}</code></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-box alert-red">❌ Could not auto-detect ASIN column. Make sure your file has a column with values like B07QNLTK2M</div>', unsafe_allow_html=True)

            for label, aliases in [("Stock", AN_STOCK_ALIASES),("Reserve", AN_RESERVE_ALIASES),
                                    ("Inbound", AN_INBOUND_ALIASES),("TOTAL", AN_TOTAL_ALIASES),
                                    ("Sales 30", AN_S30_ALIASES),("Sales 3", AN_S3_ALIASES),
                                    ("Days of stock(30)", AN_DOS30_ALIASES),("Days of stock(3)", AN_DOS3_ALIASES)]:
                col_f, conf = smart_col(an_prev, aliases)
                icon = "✅" if col_f and conf == 'exact' else ("🔧" if col_f else "⚠️")
                color = "alert-green" if col_f and conf == 'exact' else ("alert-amber" if col_f else "alert-red")
                note = f'found as <strong>"{col_f}"</strong>' if col_f else "not found — will be skipped"
                st.markdown(f'<div class="alert-box {color}" style="padding:0.5rem 1rem;margin:0.3rem 0">{icon} <strong>{label}</strong> → {note}</div>', unsafe_allow_html=True)

    if fba_file:
        fba_prev = read_file(fba_file)
        fba_file.seek(0)
        if not fba_prev.empty:
            fba_asin_prev, fba_pct = detect_asin_col_by_pattern(fba_prev)
            if fba_asin_prev:
                sample = fba_prev[fba_asin_prev].dropna().head(3).tolist()
                st.markdown(f'<div class="alert-box alert-green">✅ FBA ASIN column: <strong>"{fba_asin_prev}"</strong> ({fba_pct}%) · Sample: <code>{" · ".join(sample)}</code></div>', unsafe_allow_html=True)

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

        # ── Read files ─────────────────────────────────────────────────────────
        status.write("Reading files...")
        fba_df = read_file(fba_file)
        rb_df  = read_file(rb_file)
        an_df  = read_file(an_file)

        if any(df.empty for df in [fba_df, rb_df, an_df]):
            st.error("One or more files could not be read.")
            st.stop()

        prog.progress(10)
        log("◆ FILES LOADED", "head")
        log(f"  FBA Inventory     → {len(fba_df):,} rows | {len(fba_df.columns)} cols", "ok")
        log(f"  Restricted Brands → {len(rb_df):,} rows", "ok")
        log(f"  Analysis file     → {len(an_df):,} rows | {len(an_df.columns)} cols", "ok")

        # ── Restricted brands ──────────────────────────────────────────────────
        status.write("Building restricted brands index...")
        rb_col = rb_df.columns[0]
        restricted_set = set(rb_df[rb_col].str.strip().str.lower().dropna())
        log(f"◆ RESTRICTED INDEX — {len(restricted_set):,} brands", "head")
        prog.progress(20)

        # ── FBA map — pattern-based ASIN detection ─────────────────────────────
        status.write("Indexing FBA Inventory...")
        fba_map, fba_asin_col, fba_conf = build_fba_map(fba_df)
        log(f"◆ FBA MAP — {len(fba_map):,} ASINs | col: '{fba_asin_col}' ({fba_conf})", "head" if fba_map else "warn")
        if not fba_map:
            log("  ⚠ No ASINs found in FBA file — check file format", "warn")
        prog.progress(35)

        # ── Archive map — dual-table parser ────────────────────────────────────
        status.write("Parsing Archive Inventory (dual-table)...")
        arch_map = read_archive(arch_file)
        log(f"◆ ARCHIVE MAP — {len(arch_map):,} unique ASINs from all tables", "head" if arch_map else "warn")
        prog.progress(52)

        # ── Detect analysis file columns ───────────────────────────────────────
        status.write("Detecting analysis columns...")
        an_asin_col, an_asin_pct = detect_asin_col_by_pattern(an_df)
        if not an_asin_col:
            st.error("❌ Cannot find ASIN column in analysis file. Make sure it has cells like B07QNLTK2M")
            st.stop()

        an_brand_col,   _ = smart_col(an_df, AN_BRAND_ALIASES)
        an_stock_col,   _ = smart_col(an_df, AN_STOCK_ALIASES)
        an_reserve_col, _ = smart_col(an_df, AN_RESERVE_ALIASES)
        an_inbound_col, _ = smart_col(an_df, AN_INBOUND_ALIASES)
        an_total_col,   _ = smart_col(an_df, AN_TOTAL_ALIASES)
        an_restr_col,   _ = smart_col(an_df, AN_RESTR_ALIASES)
        an_dos30_col,   _ = smart_col(an_df, AN_DOS30_ALIASES)
        an_dos3_col,    _ = smart_col(an_df, AN_DOS3_ALIASES)
        an_s30_col,     _ = smart_col(an_df, AN_S30_ALIASES)
        an_s3_col,      _ = smart_col(an_df, AN_S3_ALIASES)
        an_listing_col, _ = smart_col(an_df, AN_LISTING_ALIASES)

        log("◆ ANALYSIS COLUMNS DETECTED", "head")
        log(f"  ASIN     → '{an_asin_col}' (pattern match {an_asin_pct}%)", "ok")
        for lbl, col in [("Brand", an_brand_col),("Stock", an_stock_col),
                          ("Reserve", an_reserve_col),("Inbound", an_inbound_col),
                          ("TOTAL", an_total_col),("Sales30", an_s30_col),("Sales3", an_s3_col)]:
            log(f"  {lbl:10} → {col or '⚠ not found'}", "ok" if col else "warn")
        prog.progress(62)

        # ── Process rows ───────────────────────────────────────────────────────
        status.write("Processing rows...")
        out_rows = []
        fba_hits = arch_hits = restricted_count = filled_cells = 0
        anomalies = []
        n = len(an_df)

        for idx, row in an_df.iterrows():
            nr    = row.to_dict()
            asin  = clean_asin(row[an_asin_col])
            brand = str(row.get(an_brand_col, "")).strip().lower() if an_brand_col else ""
            brand_display = str(row.get(an_brand_col, "")).strip() if an_brand_col else ""

            if not is_asin(asin):
                out_rows.append(nr)
                continue

            fba_hit  = asin in fba_map
            arch_hit = asin in arch_map

            # fill from FBA first
            if fba_hit:
                fba_hits += 1
                fba = fba_map[asin]
                for an_c, src_aliases in [
                    (an_stock_col,   FBA_STOCK_SRC),
                    (an_reserve_col, FBA_RESERVE_SRC),
                    (an_inbound_col, FBA_INBOUND_SRC),
                    (an_total_col,   FBA_TOTAL_SRC),
                ]:
                    if an_c and is_blank(nr.get(an_c, "")):
                        v = get_val(fba, src_aliases)
                        if v is not None:
                            nr[an_c] = v
                            filled_cells += 1

            # fill remaining blanks from Archive
            if arch_hit:
                if not fba_hit: arch_hits += 1
                arch = arch_map[asin]
                for an_c, src_aliases in [
                    (an_stock_col,   ARCH_STOCK_SRC),
                    (an_reserve_col, ARCH_RESERVE_SRC),
                    (an_total_col,   ARCH_TOTAL_SRC),
                ]:
                    if an_c and is_blank(nr.get(an_c, "")):
                        v = get_val(arch, src_aliases)
                        if v is not None:
                            nr[an_c] = v
                            filled_cells += 1

            # restricted brand flag
            is_r = bool(brand and brand in restricted_set)
            if is_r: restricted_count += 1
            flag_col = an_restr_col or "Restricted"
            nr[flag_col] = "Yes — Restricted" if is_r else "No"

            # recalculate days of stock
            try:
                stock_v = safe_float(nr.get(an_stock_col, 0)) if an_stock_col else 0
                s30_v   = safe_float(nr.get(an_s30_col, 0))   if an_s30_col   else 0
                s3_v    = safe_float(nr.get(an_s3_col, 0))    if an_s3_col    else 0
                if an_dos30_col and s30_v > 0:
                    nr[an_dos30_col] = round(stock_v / (s30_v / 30), 1)
                if an_dos3_col and s3_v > 0:
                    nr[an_dos3_col]  = round(stock_v / (s3_v / 3),  1)
            except: pass

            # anomaly detection
            stock_v = safe_float(nr.get(an_stock_col, 0)) if an_stock_col else 0
            s30_v   = safe_float(nr.get(an_s30_col, 0))   if an_s30_col   else 0
            dos30_v = safe_float(nr.get(an_dos30_col, 999)) if an_dos30_col else 999
            listing = str(nr.get(an_listing_col, "")).lower() if an_listing_col else ""

            if stock_v == 0 and s30_v > 5:
                anomalies.append({"type":"🔴 Zero stock / high velocity","severity":"red",
                    "asin":asin,"brand":brand_display,"detail":f"0 stock | {s30_v:.0f} sold last 30d"})
            elif 0 < dos30_v < 7:
                anomalies.append({"type":"🔴 Critical — under 7 days stock","severity":"red",
                    "asin":asin,"brand":brand_display,"detail":f"{dos30_v} days remaining"})
            elif 7 <= dos30_v < 14:
                anomalies.append({"type":"🟡 Low stock warning","severity":"amber",
                    "asin":asin,"brand":brand_display,"detail":f"{dos30_v} days remaining"})
            if is_r and "yes" in listing:
                anomalies.append({"type":"🚫 Restricted brand — active listing","severity":"red",
                    "asin":asin,"brand":brand_display,"detail":f"'{brand_display}' restricted but listing is active"})

            out_rows.append(nr)
            if idx % max(1, n // 25) == 0:
                prog.progress(62 + int(33 * idx / n))

        prog.progress(96)
        out_df = pd.DataFrame(out_rows)

        # ── Write output ───────────────────────────────────────────────────────
        status.write("Writing output file...")
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            out_df.to_excel(writer, index=False, sheet_name="Analysis_Filled")
            if anomalies:
                pd.DataFrame(anomalies)[["type","asin","brand","detail"]].to_excel(
                    writer, index=False, sheet_name="Anomaly_Alerts")
        buf.seek(0)
        prog.progress(100)
        t1 = time.time()
        status.empty()
        prog.empty()

        log(f"◆ COMPLETE — {round(t1-t0,2)}s", "head")
        log(f"  Rows processed  : {n:,}", "ok")
        log(f"  FBA matched     : {fba_hits:,} ({pct(fba_hits, n)}%)", "ok")
        log(f"  Archive matched : {arch_hits:,} ({pct(arch_hits, n)}%)", "ok")
        log(f"  Cells filled    : {filled_cells:,}", "ok")
        log(f"  Restricted      : {restricted_count:,}", "warn" if restricted_count else "ok")
        log(f"  Anomalies       : {len(anomalies):,}", "warn" if anomalies else "ok")

        match_rate = pct(fba_hits, n)
        st.session_state.run_result = {
            "out_df": out_df, "buf": buf.getvalue(),
            "n": n, "fba_hits": fba_hits, "arch_hits": arch_hits,
            "filled_cells": filled_cells, "restricted_count": restricted_count,
            "anomalies": anomalies, "match_rate": match_rate, "logs": logs,
            "elapsed": round(t1-t0,2), "vendor": vendor_name or "Unknown",
            "run_date": str(date.today()),
            "an_stock_col": an_stock_col, "an_asin_col": an_asin_col, "an_brand_col": an_brand_col,
        }
        if vendor_name:
            st.session_state.vendor_history.append({
                "vendor": vendor_name, "date": str(date.today()),
                "rows": n, "match_rate": match_rate, "filled": filled_cells,
                "restricted": restricted_count, "anomalies": len(anomalies)
            })

    # ── Show results ──────────────────────────────────────────────────────────
    if st.session_state.run_result:
        r = st.session_state.run_result
        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown("### Run report")
        st.markdown(f"""
        <div class="metric-row">
          <div class="metric-box"><div class="m-val blue">{r['n']:,}</div><div class="m-lbl">Rows processed</div></div>
          <div class="metric-box"><div class="m-val green">{r['fba_hits']:,}</div><div class="m-lbl">FBA matched ({r['match_rate']}%)</div></div>
          <div class="metric-box"><div class="m-val green">{r['filled_cells']:,}</div><div class="m-lbl">Cells auto-filled</div></div>
          <div class="metric-box"><div class="m-val {'red' if r['restricted_count'] else 'green'}">{r['restricted_count']:,}</div><div class="m-lbl">Restricted flagged</div></div>
        </div>
        <div style="font-size:0.72rem;color:#3a3a5a;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin:0.5rem 0 0.2rem">FBA match accuracy — {r['match_rate']}%</div>
        <div class="prog-wrap"><div class="prog-fill" style="width:{r['match_rate']}%"></div></div>
        """, unsafe_allow_html=True)

        st.markdown(f'<div class="log-box">{"<br>".join(r["logs"])}</div>', unsafe_allow_html=True)

        if r['anomalies']:
            st.markdown(f"### ⚠️ Anomaly alerts — {len(r['anomalies'])} found")
            for a in r['anomalies'][:20]:
                cls = "alert-red" if a['severity'] == "red" else "alert-amber"
                st.markdown(f'<div class="alert-box {cls}"><strong>{a["type"]}</strong> &nbsp;|&nbsp; <code>{a["asin"]}</code> &nbsp;|&nbsp; {a["brand"]} &nbsp;|&nbsp; {a["detail"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-box alert-green">✅ No anomalies detected — all ASINs healthy</div>', unsafe_allow_html=True)

        fname = f"Analysis_Filled_{date.today()}.xlsx"
        st.download_button(
            label=f"⬇️  Download {fname}",
            data=r['buf'], file_name=fname,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True, type="primary"
        )

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
with tab_dash:
    if not st.session_state.run_result:
        st.markdown('<div class="alert-box alert-blue" style="margin-top:1rem">Run the engine first to see your dashboard.</div>', unsafe_allow_html=True)
    else:
        r      = st.session_state.run_result
        out_df = r['out_df']
        sc     = r.get('an_stock_col')
        ac     = r.get('an_asin_col')
        bc     = r.get('an_brand_col')

        st.markdown(f"### 📊 Live dashboard")
        st.markdown(f"<div class='card-sub'>Vendor: {r['vendor']} &nbsp;|&nbsp; {r['run_date']} &nbsp;|&nbsp; {r['elapsed']}s</div>", unsafe_allow_html=True)

        st.markdown("#### 🔻 Top 10 lowest stock ASINs")
        if sc and sc in out_df.columns:
            tmp = out_df.copy()
            tmp["_s"] = tmp[sc].apply(safe_float)
            show_cols = [c for c in [ac, bc, sc] if c and c in tmp.columns]
            low = tmp.nsmallest(10, "_s")[show_cols]
            low.columns = ["ASIN","Brand","Stock"][:len(show_cols)]
            st.dataframe(low, use_container_width=True, hide_index=True)
        else:
            st.info("Stock column not available.")

        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown("#### 🚫 Restricted brand breakdown")
        restr_col = r.get('an_restr_col') or "Restricted"
        if bc and bc in out_df.columns and restr_col in out_df.columns:
            restr_df = out_df[out_df[restr_col].str.contains("Restricted", na=False)]
            if not restr_df.empty:
                counts = restr_df[bc].value_counts().reset_index()
                counts.columns = ["Brand","Count"]
                st.dataframe(counts, use_container_width=True, hide_index=True)
            else:
                st.markdown('<div class="alert-box alert-green">✅ No restricted brands found</div>', unsafe_allow_html=True)

        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown("#### ⚠️ Anomaly summary")
        if r['anomalies']:
            anom_view = pd.DataFrame(r['anomalies'])[["type","asin","brand","detail"]]
            anom_view.columns = ["Alert","ASIN","Brand","Detail"]
            st.dataframe(anom_view, use_container_width=True, hide_index=True)
        else:
            st.markdown('<div class="alert-box alert-green">✅ No anomalies</div>', unsafe_allow_html=True)

        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        mr    = r['match_rate']
        color = "#34d399" if mr >= 80 else "#fbbf24" if mr >= 50 else "#f87171"
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
        st.markdown('<div class="alert-box alert-blue" style="margin-top:1rem">No history yet. Enter a vendor name in the Run tab to start tracking.</div>', unsafe_allow_html=True)
    else:
        hist_df = pd.DataFrame(history)
        hist_df.columns = ["Vendor","Date","Rows","Match Rate (%)","Cells Filled","Restricted","Anomalies"]
        st.dataframe(hist_df, use_container_width=True, hide_index=True)
        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown("#### Per-vendor summary")
        summary = hist_df.groupby("Vendor").agg({
            "Rows":"sum","Match Rate (%)":"mean",
            "Cells Filled":"sum","Restricted":"sum","Anomalies":"sum"
        }).round(1).reset_index()
        st.dataframe(summary, use_container_width=True, hide_index=True)
        if st.button("🗑 Clear history"):
            st.session_state.vendor_history = []
            st.rerun()
