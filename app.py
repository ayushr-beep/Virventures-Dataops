import streamlit as st
import pandas as pd
import io
import time
from datetime import date
from difflib import SequenceMatcher

st.set_page_config(
    page_title="BuyIQ — Analysis Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #07070f; color: #e0e0f0; }
.block-container { padding-top: 1.5rem !important; }

.hero {
    background: linear-gradient(135deg, #0d0d1f 0%, #111128 60%, #0d1a12 100%);
    border: 1px solid #1c1c3a; border-radius: 20px;
    padding: 2.5rem 2.5rem 2rem; margin-bottom: 1.5rem;
}
.hero-badge {
    display: inline-block; background: rgba(99,102,241,0.15); color: #818cf8;
    border: 1px solid rgba(99,102,241,0.3); border-radius: 20px;
    padding: 3px 14px; font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.8rem;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif; font-size: 2.6rem; font-weight: 700;
    background: linear-gradient(135deg, #a5b4fc 0%, #818cf8 40%, #34d399 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin: 0 0 0.4rem; line-height: 1.1;
}
.hero-sub { font-size: 0.95rem; color: #555570; font-weight: 400; margin: 0; }

.card-title { font-family:'Space Grotesk',sans-serif; font-size:0.95rem; font-weight:600; color:#c0c0e0; margin-bottom:0.2rem; }
.card-sub   { font-size:0.7rem; color:#3a3a5a; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:1rem; }

.metric-row { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin:1.2rem 0; }
.metric-box { background:#080814; border:1px solid #161630; border-radius:12px; padding:1rem 1.1rem; text-align:center; }
.m-val { font-family:'Space Grotesk',sans-serif; font-size:1.9rem; font-weight:700; line-height:1; }
.m-val.blue  { color:#818cf8; } .m-val.green { color:#34d399; }
.m-val.amber { color:#fbbf24; } .m-val.red   { color:#f87171; }
.m-lbl { font-size:0.68rem; color:#3a3a5a; margin-top:4px; text-transform:uppercase; letter-spacing:0.08em; }

.log-box {
    background:#040410; border:1px solid #111128; border-radius:12px;
    padding:1rem 1.3rem; font-family:'Courier New',monospace; font-size:0.78rem;
    line-height:1.9; max-height:280px; overflow-y:auto; margin:0.8rem 0;
}
.lok { color:#34d399; } .lwarn { color:#fbbf24; }
.lerr { color:#f87171; } .lhead { color:#818cf8; font-weight:700; }
.linfo{ color:#3a3a5a; }

.prog-wrap { background:#151530; border-radius:8px; height:5px; margin:0.5rem 0; overflow:hidden; }
.prog-fill { height:100%; border-radius:8px; background:linear-gradient(90deg,#6366f1,#34d399); }

.alert-box { border-radius:12px; padding:0.9rem 1.1rem; margin:0.5rem 0; font-size:0.82rem; }
.alert-red   { background:rgba(248,113,113,0.08); border:1px solid rgba(248,113,113,0.25); color:#fca5a5; }
.alert-amber { background:rgba(251,191,36,0.08);  border:1px solid rgba(251,191,36,0.25);  color:#fde68a; }
.alert-green { background:rgba(52,211,153,0.08);  border:1px solid rgba(52,211,153,0.25);  color:#6ee7b7; }
.alert-blue  { background:rgba(129,140,248,0.08); border:1px solid rgba(129,140,248,0.25); color:#a5b4fc; }

.heal-box { background:#0a0a20; border:1px solid #20205a; border-radius:10px; padding:0.9rem 1.1rem; margin:0.4rem 0; font-size:0.82rem; }
.heal-found { color:#fbbf24; font-weight:600; }
.heal-sugg  { color:#818cf8; font-weight:600; }

.divhr { border:none; border-top:1px solid #141428; margin:1.2rem 0; }
.debug-box { background:#0a0a0a; border:1px solid #222; border-radius:10px; padding:1rem; font-family:monospace; font-size:0.75rem; color:#888; margin:0.5rem 0; max-height:200px; overflow-y:auto; }

.stTabs [data-baseweb="tab-list"] { gap:4px; background:#0d0d1c; border-radius:12px; padding:4px; }
.stTabs [data-baseweb="tab"] { border-radius:8px; padding:6px 18px; font-size:0.82rem; color:#555570; }
.stTabs [aria-selected="true"] { background:#1a1a35 !important; color:#c0c0e0 !important; }

div[data-testid="stButton"] > button {
    background: linear-gradient(135deg,#6366f1,#4f46e5) !important;
    color:white !important; border:none !important; border-radius:12px !important;
    font-family:'Space Grotesk',sans-serif !important; font-weight:600 !important; font-size:0.95rem !important;
}
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg,#059669,#047857) !important;
    color:white !important; border:none !important; border-radius:12px !important;
    font-family:'Space Grotesk',sans-serif !important; font-weight:600 !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
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

def clean_asin(v):
    """Strip whitespace, quotes, byte-string prefixes like b' """
    s = str(v).strip()
    # remove b'...' or b"..." python byte string representation
    if s.startswith(("b'", 'b"')) and s.endswith(("'", '"')):
        s = s[2:-1]
    return s.strip().upper()

def similarity(a, b):
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

def smart_find_col(df, targets, threshold=0.55):
    """Returns (col, confidence) — confidence is 'exact', 'fuzzy', or None"""
    cols = list(df.columns)
    # 1. exact match
    for t in targets:
        for c in cols:
            if c.strip().lower() == t.strip().lower():
                return c, 'exact'
    # 2. substring match
    for t in targets:
        for c in cols:
            if t.lower() in c.lower() or c.lower() in t.lower():
                return c, 'fuzzy'
    # 3. similarity match
    best_col, best_score = None, 0
    for t in targets:
        for c in cols:
            s = similarity(c, t)
            if s > best_score:
                best_score, best_col = s, c
    if best_score >= threshold:
        return best_col, 'fuzzy'
    return None, None

def is_blank(v):
    return str(v).strip().lower() in ("", "n/a", "#n/a", "#value!", "nan", "none", "0")

def safe_float(v, default=0.0):
    try: return float(str(v).replace(",","").strip())
    except: return default

def pct(a, b): return round(a / b * 100, 1) if b else 0

# ═══════════════════════════════════════════════════════════════════════════════
# COLUMN KNOWLEDGE BASE — all known aliases for each logical column
# ═══════════════════════════════════════════════════════════════════════════════

# Analysis file ASIN column aliases
AN_ASIN_ALIASES  = ["Output ASIN", "output asin", "asin(A-Z)", "asin(Z-A)", "asin", "ASIN"]
AN_BRAND_ALIASES = ["Brand", "brand", "BRAND"]

# Columns we want to fill in analysis file → ranked list of source col names
FBA_FILL = {
    "Stock":   ["STOCK", "afn-fulfillable-quantity", "fulfillable"],
    "Reserve": ["RESERVE", "afn-reserved-quantity", "afn-reserve"],
    "Inbound": ["INBOUND", "afn-inbound-working-quantity", "afn-inbound-shipped-quantity", "afn-inbound"],
    "Total":   ["afn-total-quantity", "TOTAL"],
}
ARCH_FILL = {
    "Stock":   ["afn-fulfillable-quantity", "STOCK"],
    "Reserve": ["afn-reserved-quantity", "afn-reserved-quantity", "RESERVE"],
    "Total":   ["afn-total-quantity", "TOTAL"],
}

# Analysis file target column aliases
AN_STOCK_ALIASES   = ["Stock", "STOCK", "stock qty", "inv stock"]
AN_RESERVE_ALIASES = ["Reserve", "RESERVE", "reserved"]
AN_INBOUND_ALIASES = ["Inbound", "INBOUND", "inbound qty"]
AN_TOTAL_ALIASES   = ["TOTAL(Stock+Reserve+inbound)", "TOTAL", "total stock", "total qty"]
AN_RESTR_ALIASES   = ["Restricted", "restricted brand", "brand restricted"]
AN_DOS30_ALIASES   = ["Days of stock(30)", "dos30", "days of stock 30"]
AN_DOS3_ALIASES    = ["Days of stock(3)", "dos3", "days of stock 3"]
AN_S30_ALIASES     = ["Sales 30", "sales30", "30 day sales", "Sales30"]
AN_S3_ALIASES      = ["Sales 3",  "sales3",  "3 day sales",  "Sales3"]
AN_LISTING_ALIASES = ["Listing Status", "afn-listing-exists", "mfn-listing-exists", "listing"]

# FBA / Archive ASIN column aliases
FBA_ASIN_ALIASES  = ["asin", "ASIN"]
ARCH_ASIN_ALIASES = ["asin(A-Z)", "asin", "ASIN"]

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
if "run_result"      not in st.session_state: st.session_state.run_result      = None
if "vendor_history"  not in st.session_state: st.session_state.vendor_history  = []

# ═══════════════════════════════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-badge">⚡ Buying Intelligence Engine v2</div>
  <div class="hero-title">BuyIQ</div>
  <p class="hero-sub">Smart ASIN matching · Anomaly detection · Auto column healing · Live dashboard</p>
</div>
""", unsafe_allow_html=True)

tab_run, tab_dash, tab_history = st.tabs(["⚡  Run Engine", "📊  Dashboard", "📈  Vendor History"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — RUN
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
            missing = [n for f,n in [(fba_file,"FBA"),(rb_file,"Restricted Brands"),(arch_file,"Archive"),(an_file,"Analysis")] if not f]
            st.info("Waiting for: " + ", ".join(missing))

    # ── column detection preview ──────────────────────────────────────────────
    if an_file:
        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown("### 🔬 Column detection — Analysis file")
        an_prev = read_file(an_file)
        an_file.seek(0)

        if not an_prev.empty:
            st.markdown(f"<div class='card-sub'>Detected {len(an_prev.columns)} columns · {len(an_prev):,} rows</div>", unsafe_allow_html=True)

            # show what columns we found
            asin_col_found, asin_conf = smart_find_col(an_prev, AN_ASIN_ALIASES)
            checks = [
                ("ASIN column",   asin_col_found,                                        asin_conf),
                ("Brand column",  smart_find_col(an_prev, AN_BRAND_ALIASES)[0],          smart_find_col(an_prev, AN_BRAND_ALIASES)[1]),
                ("Stock",         smart_find_col(an_prev, AN_STOCK_ALIASES)[0],          smart_find_col(an_prev, AN_STOCK_ALIASES)[1]),
                ("Reserve",       smart_find_col(an_prev, AN_RESERVE_ALIASES)[0],        smart_find_col(an_prev, AN_RESERVE_ALIASES)[1]),
                ("Inbound",       smart_find_col(an_prev, AN_INBOUND_ALIASES)[0],        smart_find_col(an_prev, AN_INBOUND_ALIASES)[1]),
                ("TOTAL",         smart_find_col(an_prev, AN_TOTAL_ALIASES)[0],          smart_find_col(an_prev, AN_TOTAL_ALIASES)[1]),
                ("Sales 30",      smart_find_col(an_prev, AN_S30_ALIASES)[0],            smart_find_col(an_prev, AN_S30_ALIASES)[1]),
                ("Sales 3",       smart_find_col(an_prev, AN_S3_ALIASES)[0],             smart_find_col(an_prev, AN_S3_ALIASES)[1]),
                ("Days of stock(30)", smart_find_col(an_prev, AN_DOS30_ALIASES)[0],      smart_find_col(an_prev, AN_DOS30_ALIASES)[1]),
                ("Days of stock(3)",  smart_find_col(an_prev, AN_DOS3_ALIASES)[0],       smart_find_col(an_prev, AN_DOS3_ALIASES)[1]),
                ("Restricted",    smart_find_col(an_prev, AN_RESTR_ALIASES)[0],          smart_find_col(an_prev, AN_RESTR_ALIASES)[1]),
            ]
            for label, found, conf in checks:
                if found and conf == 'exact':
                    st.markdown(f'<div class="alert-box alert-green">✅ <strong>{label}</strong> → found as <code>{found}</code> (exact)</div>', unsafe_allow_html=True)
                elif found and conf == 'fuzzy':
                    st.markdown(f'<div class="heal-box">🔧 <strong>{label}</strong> → matched to <span class="heal-found">"{found}"</span> <span style="color:#555">(fuzzy — confirm this is correct)</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="alert-box alert-amber">⚠️ <strong>{label}</strong> → not found (will be skipped or created)</div>', unsafe_allow_html=True)

            # show first 3 ASIN values so user can verify
            if asin_col_found:
                sample_asins = an_prev[asin_col_found].head(3).tolist()
                st.markdown(f"<div class='card-sub' style='margin-top:0.8rem'>Sample ASINs from analysis file: <code>{'&nbsp;&nbsp;|&nbsp;&nbsp;'.join(sample_asins)}</code></div>", unsafe_allow_html=True)

    if fba_file:
        fba_prev = read_file(fba_file)
        fba_file.seek(0)
        if not fba_prev.empty:
            fba_asin_col, _ = smart_find_col(fba_prev, FBA_ASIN_ALIASES)
            if fba_asin_col:
                sample_fba = fba_prev[fba_asin_col].head(3).tolist()
                st.markdown(f"<div class='card-sub'>Sample ASINs from FBA file: <code>{'&nbsp;&nbsp;|&nbsp;&nbsp;'.join(sample_fba)}</code></div>", unsafe_allow_html=True)

    st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
    run_btn = st.button("⚡ Run BuyIQ Engine", disabled=not all_ready, use_container_width=True, type="primary")

    # ── RUN ───────────────────────────────────────────────────────────────────
    if run_btn and all_ready:
        t0   = time.time()
        logs = []

        def log(msg, kind="info"):
            cls = {"ok":"lok","warn":"lwarn","err":"lerr","head":"lhead"}.get(kind,"linfo")
            logs.append(f'<span class="{cls}">{msg}</span>')

        prog   = st.progress(0)
        status = st.empty()

        # read
        status.write("Reading files...")
        fba_df  = read_file(fba_file)
        rb_df   = read_file(rb_file)
        arch_df = read_file(arch_file)
        an_df   = read_file(an_file)

        if any(df.empty for df in [fba_df, rb_df, arch_df, an_df]):
            st.error("One or more files could not be read. Please check and re-upload.")
            st.stop()

        prog.progress(12)
        log("◆ FILES LOADED", "head")
        log(f"  FBA Inventory     → {len(fba_df):,} rows | cols: {', '.join(fba_df.columns[:6].tolist())}...", "ok")
        log(f"  Restricted Brands → {len(rb_df):,} brands", "ok")
        log(f"  Archive Inventory → {len(arch_df):,} rows", "ok")
        log(f"  Analysis file     → {len(an_df):,} rows | cols: {', '.join(an_df.columns[:6].tolist())}...", "ok")

        # restricted brands set
        rb_col = rb_df.columns[0]
        restricted_set = set(rb_df[rb_col].str.strip().str.lower().dropna())
        log(f"◆ RESTRICTED INDEX — {len(restricted_set):,} brands loaded", "head")
        prog.progress(22)

        # FBA map — keyed by clean ASIN
        fba_asin_col, fba_conf = smart_find_col(fba_df, FBA_ASIN_ALIASES)
        fba_map = {}
        if fba_asin_col:
            log(f"  FBA ASIN column   → '{fba_asin_col}' ({fba_conf})", "ok")
            for _, r in fba_df.iterrows():
                k = clean_asin(r[fba_asin_col])
                if k:
                    fba_map[k] = r.to_dict()
        else:
            log("  ⚠ Could not find ASIN column in FBA file!", "warn")
        log(f"◆ FBA MAP — {len(fba_map):,} unique ASINs indexed", "head")
        prog.progress(35)

        # Archive map
        arch_asin_col, arch_conf = smart_find_col(arch_df, ARCH_ASIN_ALIASES)
        arch_map = {}
        if arch_asin_col:
            log(f"  Archive ASIN col  → '{arch_asin_col}' ({arch_conf})", "ok")
            for _, r in arch_df.iterrows():
                k = clean_asin(r[arch_asin_col])
                if k and k not in arch_map:
                    arch_map[k] = r.to_dict()
        else:
            log("  ⚠ Could not find ASIN column in Archive file!", "warn")
        log(f"◆ ARCHIVE MAP — {len(arch_map):,} unique ASINs indexed", "head")
        prog.progress(48)

        # locate analysis file columns
        an_asin_col,   _ = smart_find_col(an_df, AN_ASIN_ALIASES)
        an_brand_col,  _ = smart_find_col(an_df, AN_BRAND_ALIASES)
        an_stock_col,  _ = smart_find_col(an_df, AN_STOCK_ALIASES)
        an_reserve_col,_ = smart_find_col(an_df, AN_RESERVE_ALIASES)
        an_inbound_col,_ = smart_find_col(an_df, AN_INBOUND_ALIASES)
        an_total_col,  _ = smart_find_col(an_df, AN_TOTAL_ALIASES)
        an_restr_col,  _ = smart_find_col(an_df, AN_RESTR_ALIASES)
        an_dos30_col,  _ = smart_find_col(an_df, AN_DOS30_ALIASES)
        an_dos3_col,   _ = smart_find_col(an_df, AN_DOS3_ALIASES)
        an_s30_col,    _ = smart_find_col(an_df, AN_S30_ALIASES)
        an_s3_col,     _ = smart_find_col(an_df, AN_S3_ALIASES)
        an_listing_col,_ = smart_find_col(an_df, AN_LISTING_ALIASES)

        log("◆ ANALYSIS COLUMNS", "head")
        log(f"  ASIN col   → {an_asin_col   or '⚠ NOT FOUND'}", "ok" if an_asin_col   else "warn")
        log(f"  Brand col  → {an_brand_col  or '⚠ NOT FOUND'}", "ok" if an_brand_col  else "warn")
        log(f"  Stock col  → {an_stock_col  or '⚠ NOT FOUND'}", "ok" if an_stock_col  else "warn")
        log(f"  Reserve col→ {an_reserve_col or '⚠ NOT FOUND'}", "ok" if an_reserve_col else "warn")
        log(f"  Inbound col→ {an_inbound_col or '⚠ NOT FOUND'}", "ok" if an_inbound_col else "warn")
        log(f"  Total col  → {an_total_col  or '⚠ NOT FOUND'}", "ok" if an_total_col  else "warn")

        if not an_asin_col:
            st.error("❌ Could not find ASIN column in analysis file. Please check column headers.")
            st.stop()

        prog.progress(58)

        # ── process rows ──────────────────────────────────────────────────────
        status.write("Processing rows...")
        out_rows = []
        fba_hits = arch_hits = restricted_count = filled_cells = 0
        anomalies = []
        n = len(an_df)

        def get_fba_val(fba_row, aliases):
            for alias in aliases:
                for k, v in fba_row.items():
                    if k.strip().lower() == alias.strip().lower() and not is_blank(v):
                        return v
            return None

        for idx, row in an_df.iterrows():
            nr    = row.to_dict()
            asin  = clean_asin(row[an_asin_col])
            brand = str(row.get(an_brand_col, "")).strip().lower() if an_brand_col else ""
            brand_display = str(row.get(an_brand_col, "")).strip() if an_brand_col else ""

            fba_hit  = asin in fba_map
            arch_hit = asin in arch_map

            if fba_hit:
                fba_hits += 1
                fba = fba_map[asin]

                fill_pairs = [
                    (an_stock_col,   FBA_FILL["Stock"]),
                    (an_reserve_col, FBA_FILL["Reserve"]),
                    (an_inbound_col, FBA_FILL["Inbound"]),
                    (an_total_col,   FBA_FILL["Total"]),
                ]
                for an_c, src_aliases in fill_pairs:
                    if an_c and is_blank(nr.get(an_c, "")):
                        v = get_fba_val(fba, src_aliases)
                        if v is not None:
                            nr[an_c] = v
                            filled_cells += 1

            if arch_hit:
                if not fba_hit:
                    arch_hits += 1
                arch = arch_map[asin]
                arch_pairs = [
                    (an_stock_col,   ARCH_FILL["Stock"]),
                    (an_reserve_col, ARCH_FILL["Reserve"]),
                    (an_total_col,   ARCH_FILL["Total"]),
                ]
                for an_c, src_aliases in arch_pairs:
                    if an_c and is_blank(nr.get(an_c, "")):
                        v = get_fba_val(arch, src_aliases)
                        if v is not None:
                            nr[an_c] = v
                            filled_cells += 1

            # restricted brand
            is_r = bool(brand and brand in restricted_set)
            if is_r: restricted_count += 1
            flag = "Yes — Restricted" if is_r else "No"
            target_restr = an_restr_col or "Restricted"
            nr[target_restr] = flag

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
            stock_v  = safe_float(nr.get(an_stock_col, 0)) if an_stock_col else 0
            s30_v    = safe_float(nr.get(an_s30_col, 0))   if an_s30_col   else 0
            dos30_v  = safe_float(nr.get(an_dos30_col, 999)) if an_dos30_col else 999
            listing  = str(nr.get(an_listing_col, "")).lower() if an_listing_col else ""

            if stock_v == 0 and s30_v > 5:
                anomalies.append({"type": "🔴 Zero stock / high velocity", "severity": "red",
                    "asin": asin, "brand": brand_display, "detail": f"0 stock | {s30_v:.0f} units sold last 30d"})
            elif 0 < dos30_v < 7:
                anomalies.append({"type": "🔴 Critical low stock", "severity": "red",
                    "asin": asin, "brand": brand_display, "detail": f"{dos30_v} days of stock left"})
            elif 7 <= dos30_v < 14:
                anomalies.append({"type": "🟡 Low stock warning", "severity": "amber",
                    "asin": asin, "brand": brand_display, "detail": f"{dos30_v} days of stock left"})
            if is_r and "yes" in listing:
                anomalies.append({"type": "🚫 Restricted brand — active listing", "severity": "red",
                    "asin": asin, "brand": brand_display, "detail": f"'{brand_display}' restricted but listing active"})

            out_rows.append(nr)
            if idx % max(1, n // 20) == 0:
                prog.progress(58 + int(35 * idx / n))

        prog.progress(95)
        out_df = pd.DataFrame(out_rows)

        # write output
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

        log(f"◆ COMPLETE in {t1-t0:.2f}s", "head")
        log(f"  Total rows      : {n:,}", "ok")
        log(f"  FBA matched     : {fba_hits:,} ({pct(fba_hits,n)}%)", "ok")
        log(f"  Archive matched : {arch_hits:,} ({pct(arch_hits,n)}%)", "ok")
        log(f"  Cells filled    : {filled_cells:,}", "ok")
        log(f"  Restricted      : {restricted_count:,}", "warn" if restricted_count else "ok")
        log(f"  Anomalies       : {len(anomalies):,}", "warn" if anomalies else "ok")

        match_rate = pct(fba_hits, n)
        result = {
            "out_df": out_df, "buf": buf.getvalue(),
            "n": n, "fba_hits": fba_hits, "arch_hits": arch_hits,
            "filled_cells": filled_cells, "restricted_count": restricted_count,
            "anomalies": anomalies, "match_rate": match_rate, "logs": logs,
            "elapsed": round(t1-t0, 2), "vendor": vendor_name or "Unknown",
            "run_date": str(date.today()),
            "an_stock_col": an_stock_col, "an_asin_col": an_asin_col, "an_brand_col": an_brand_col,
        }
        st.session_state.run_result = result
        if vendor_name:
            st.session_state.vendor_history.append({
                "vendor": vendor_name, "date": str(date.today()),
                "rows": n, "match_rate": match_rate,
                "filled": filled_cells, "restricted": restricted_count,
                "anomalies": len(anomalies)
            })
        prog.empty()

    # show results
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
        <div style="font-size:0.72rem;color:#3a3a5a;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin:0.5rem 0 0.2rem">
          FBA match accuracy — {r['match_rate']}%
        </div>
        <div class="prog-wrap"><div class="prog-fill" style="width:{r['match_rate']}%"></div></div>
        """, unsafe_allow_html=True)

        st.markdown(f'<div class="log-box">{"<br>".join(r["logs"])}</div>', unsafe_allow_html=True)

        if r['anomalies']:
            st.markdown(f"### ⚠️ Anomaly alerts — {len(r['anomalies'])} found")
            for a in r['anomalies'][:15]:
                cls = "alert-red" if a['severity']=="red" else "alert-amber"
                st.markdown(f'<div class="alert-box {cls}"><strong>{a["type"]}</strong> &nbsp;|&nbsp; <code>{a["asin"]}</code> &nbsp;|&nbsp; {a["brand"]} &nbsp;|&nbsp; {a["detail"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-box alert-green">✅ No anomalies detected</div>', unsafe_allow_html=True)

        fname = f"Analysis_Filled_{date.today()}.xlsx"
        st.download_button(
            label=f"⬇️  Download {fname}",
            data=r['buf'], file_name=fname,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True, type="primary"
        )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
with tab_dash:
    if not st.session_state.run_result:
        st.markdown('<div class="alert-box alert-blue" style="margin-top:1rem">Run the engine first to see your dashboard.</div>', unsafe_allow_html=True)
    else:
        r = st.session_state.run_result
        out_df = r['out_df']
        st.markdown(f"### 📊 Live dashboard")
        st.markdown(f"<div class='card-sub'>Vendor: {r['vendor']} &nbsp;|&nbsp; {r['run_date']} &nbsp;|&nbsp; {r['elapsed']}s</div>", unsafe_allow_html=True)

        # top 10 low stock
        st.markdown("#### 🔻 Top 10 lowest stock ASINs")
        sc = r.get('an_stock_col')
        ac = r.get('an_asin_col')
        bc = r.get('an_brand_col')
        if sc and sc in out_df.columns:
            tmp = out_df.copy()
            tmp["_s"] = tmp[sc].apply(safe_float)
            cols_show = [c for c in [ac, bc, sc] if c]
            low = tmp.nsmallest(10, "_s")[cols_show]
            low.columns = ["ASIN","Brand","Stock"][:len(cols_show)]
            st.dataframe(low, use_container_width=True, hide_index=True)
        else:
            st.info("Stock column not available.")

        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown("#### 🚫 Restricted brand breakdown")
        restr_col = "Restricted"
        if restr_col in out_df.columns and bc and bc in out_df.columns:
            restr_df = out_df[out_df[restr_col].str.contains("Restricted", na=False)]
            if not restr_df.empty:
                counts = restr_df[bc].value_counts().reset_index()
                counts.columns = ["Brand","Count"]
                st.dataframe(counts, use_container_width=True, hide_index=True)
            else:
                st.markdown('<div class="alert-box alert-green">✅ No restricted brands in this file</div>', unsafe_allow_html=True)

        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown("#### ⚠️ Anomaly summary")
        if r['anomalies']:
            st.dataframe(pd.DataFrame(r['anomalies'])[["type","asin","brand","detail"]].rename(
                columns={"type":"Alert","asin":"ASIN","brand":"Brand","detail":"Detail"}),
                use_container_width=True, hide_index=True)
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
# TAB 3 — VENDOR HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
with tab_history:
    st.markdown("### 📈 Vendor run history")
    history = st.session_state.vendor_history
    if not history:
        st.markdown('<div class="alert-box alert-blue" style="margin-top:1rem">No history yet. Enter a vendor name before running to start tracking.</div>', unsafe_allow_html=True)
    else:
        hist_df = pd.DataFrame(history)
        hist_df.columns = ["Vendor","Date","Rows","Match Rate (%)","Cells Filled","Restricted","Anomalies"]
        st.dataframe(hist_df, use_container_width=True, hide_index=True)
        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown("#### Per-vendor summary")
        summary = hist_df.groupby("Vendor").agg({"Rows":"sum","Match Rate (%)":"mean","Cells Filled":"sum","Restricted":"sum","Anomalies":"sum"}).round(1).reset_index()
        st.dataframe(summary, use_container_width=True, hide_index=True)
        if st.button("🗑 Clear history"):
            st.session_state.vendor_history = []
            st.rerun()
