import streamlit as st
import pandas as pd
import io
import time
import json
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

.card {
    background: #0d0d1c; border: 1px solid #1a1a35;
    border-radius: 16px; padding: 1.5rem 1.6rem; margin-bottom: 1rem;
}
.card-title { font-family:'Space Grotesk',sans-serif; font-size:0.95rem; font-weight:600; color:#c0c0e0; margin-bottom:0.2rem; }
.card-sub   { font-size:0.7rem; color:#3a3a5a; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:1rem; }

.metric-row { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin:1.2rem 0; }
.metric-box { background:#080814; border:1px solid #161630; border-radius:12px; padding:1rem 1.1rem; text-align:center; }
.m-val { font-family:'Space Grotesk',sans-serif; font-size:1.9rem; font-weight:700; line-height:1; }
.m-val.blue  { color:#818cf8; }
.m-val.green { color:#34d399; }
.m-val.amber { color:#fbbf24; }
.m-val.red   { color:#f87171; }
.m-lbl { font-size:0.68rem; color:#3a3a5a; margin-top:4px; text-transform:uppercase; letter-spacing:0.08em; }

.log-box {
    background:#040410; border:1px solid #111128; border-radius:12px;
    padding:1rem 1.3rem; font-family:'Courier New',monospace; font-size:0.78rem;
    line-height:1.9; max-height:260px; overflow-y:auto; margin:0.8rem 0;
}
.lok  { color:#34d399; } .lwarn { color:#fbbf24; }
.lerr { color:#f87171; } .lhead { color:#818cf8; font-weight:700; }
.linfo{ color:#3a3a5a; }

.prog-wrap { background:#151530; border-radius:8px; height:5px; margin:0.5rem 0; overflow:hidden; }
.prog-fill { height:100%; border-radius:8px; background:linear-gradient(90deg,#6366f1,#34d399); }

.alert-box { border-radius:12px; padding:0.9rem 1.1rem; margin:0.5rem 0; font-size:0.82rem; }
.alert-red   { background:rgba(248,113,113,0.08); border:1px solid rgba(248,113,113,0.25); color:#fca5a5; }
.alert-amber { background:rgba(251,191,36,0.08);  border:1px solid rgba(251,191,36,0.25);  color:#fde68a; }
.alert-green { background:rgba(52,211,153,0.08);  border:1px solid rgba(52,211,153,0.25);  color:#6ee7b7; }
.alert-blue  { background:rgba(129,140,248,0.08); border:1px solid rgba(129,140,248,0.25); color:#a5b4fc; }

.heal-box { background:#0a0a20; border:1px solid #20205a; border-radius:10px; padding:0.9rem 1.1rem; margin:0.5rem 0; font-size:0.82rem; }
.heal-found { color:#fbbf24; font-weight:600; }
.heal-suggested { color:#818cf8; font-weight:600; }

.tab-content { padding: 1rem 0; }
.divhr { border:none; border-top:1px solid #141428; margin:1.2rem 0; }

.pill { display:inline-block; padding:2px 9px; border-radius:20px; font-size:0.67rem; font-weight:700; margin-right:4px; }
.p-fba  { background:rgba(99,102,241,0.15); color:#818cf8; }
.p-arch { background:rgba(16,185,129,0.12); color:#34d399; }
.p-rb   { background:rgba(251,191,36,0.12); color:#fbbf24; }
.p-calc { background:rgba(167,139,250,0.12); color:#c4b5fd; }
.p-red  { background:rgba(248,113,113,0.12); color:#f87171; }

.stTabs [data-baseweb="tab-list"] { gap:4px; background:#0d0d1c; border-radius:12px; padding:4px; }
.stTabs [data-baseweb="tab"] { border-radius:8px; padding:6px 18px; font-size:0.82rem; color:#555570; }
.stTabs [aria-selected="true"] { background:#1a1a35 !important; color:#c0c0e0 !important; }

div[data-testid="stButton"] > button {
    background: linear-gradient(135deg,#6366f1,#4f46e5) !important;
    color:white !important; border:none !important; border-radius:12px !important;
    font-family:'Space Grotesk',sans-serif !important; font-weight:600 !important;
    font-size:0.95rem !important; letter-spacing:0.02em !important;
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
        if f.name.lower().endswith(".csv"):
            return pd.read_csv(f, dtype=str).fillna("")
        return pd.read_excel(f, dtype=str).fillna("")
    except Exception as e:
        st.error(f"Cannot read {f.name}: {e}")
        return pd.DataFrame()

def similarity(a, b):
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

def smart_find_col(df, targets, threshold=0.6):
    """
    Returns (matched_col, confidence, found_name, suggested_name)
    confidence: 'exact' | 'fuzzy' | None
    """
    cols = list(df.columns)
    # exact match first
    for t in targets:
        for c in cols:
            if c.strip().lower() == t.strip().lower():
                return c, 'exact', c, t
    # fuzzy match
    best_col, best_score, best_target = None, 0, None
    for t in targets:
        for c in cols:
            s = similarity(c, t)
            if s > best_score:
                best_score, best_col, best_target = s, c, t
            # also check if target is contained in col or vice versa
            if t.lower() in c.lower() or c.lower() in t.lower():
                if 0.5 > best_score:
                    best_score, best_col, best_target = 0.75, c, t
    if best_score >= threshold:
        return best_col, 'fuzzy', best_col, best_target
    return None, None, None, None

def is_blank(v):
    return str(v).strip() in ("", "N/A", "#N/A", "#VALUE!", "nan", "NaN", "none", "None")

def safe_float(v, default=0.0):
    try: return float(str(v).replace(",","").strip())
    except: return default

def pct(a, b): return round(a/b*100,1) if b else 0

# ═══════════════════════════════════════════════════════════════════════════════
# COLUMN KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════════════════════

# Analysis file columns we want to fill → list of possible names in source files
AN_COL_TARGETS = {
    "Stock":                        ["Stock","STOCK","afn-fulfillable-quantity","Fulfillable","fulfillable qty","inv stock","stock qty"],
    "Reserve":                      ["Reserve","RESERVE","afn-reserved-quantity","afn-reserve","reserved qty"],
    "Inbound":                      ["Inbound","INBOUND","afn-inbound-working-quantity","afn-inbound","inbound qty","inbound working"],
    "TOTAL(Stock+Reserve+inbound)": ["TOTAL(Stock+Reserve+inbound)","TOTAL","afn-total-quantity","total qty","total stock"],
    "Restricted":                   ["Restricted","restricted brand","restricted flag","brand restricted"],
    "Days of stock(30)":            ["Days of stock(30)","dos30","days of stock 30","dos(30)"],
    "Days of stock(3)":             ["Days of stock(3)","dos3","days of stock 3","dos(3)"],
    "Sales 30":                     ["Sales 30","sales30","30 day sales","last 30","s30"],
    "Sales 3":                      ["Sales 3","sales3","3 day sales","last 3","s3"],
}

FBA_FILL_MAP = {
    "Stock":                        ["STOCK","afn-fulfillable-quantity","fulfillable"],
    "Reserve":                      ["RESERVE","afn-reserved-quantity","afn-reserve"],
    "Inbound":                      ["INBOUND","afn-inbound-working-quantity","afn-inbound"],
    "TOTAL(Stock+Reserve+inbound)": ["afn-total-quantity","TOTAL"],
}

ARCH_FILL_MAP = {
    "Stock":                        ["afn-fulfillable-quantity","STOCK","fulfillable"],
    "Reserve":                      ["afn-reserved-quantity","afn-reserve","RESERVE"],
    "TOTAL(Stock+Reserve+inbound)": ["afn-total-quantity","TOTAL"],
}

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════

if "col_overrides" not in st.session_state:
    st.session_state.col_overrides = {}
if "run_result" not in st.session_state:
    st.session_state.run_result = None
if "vendor_history" not in st.session_state:
    st.session_state.vendor_history = []

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

# ═══════════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════════

tab_run, tab_dash, tab_history = st.tabs(["⚡  Run Engine", "📊  Dashboard", "📈  Vendor History"])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — RUN ENGINE
# ─────────────────────────────────────────────────────────────────────────────
with tab_run:
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2, gap="large")

    with col_l:
        st.markdown('<div class="card-title">Step 1 — Source files</div><div class="card-sub">Upload today\'s 3 files</div>', unsafe_allow_html=True)
        fba_file  = st.file_uploader("📦 FBA Inventory",     type=["xlsx","xls","csv"], key="fba")
        rb_file   = st.file_uploader("🚫 Restricted Brands", type=["xlsx","xls","csv"], key="rb")
        arch_file = st.file_uploader("🗃️ Archive Inventory", type=["xlsx","xls","csv"], key="arch")

    with col_r:
        st.markdown('<div class="card-title">Step 2 — Analysis file</div><div class="card-sub">File with blank / N/A columns</div>', unsafe_allow_html=True)
        an_file     = st.file_uploader("📊 Analysis file", type=["xlsx","xls","csv"], key="an")
        vendor_name = st.text_input("Vendor name (for history tracking)", placeholder="e.g. ALLWAY, 3M, Scotch...")

        all_ready = fba_file and rb_file and arch_file and an_file
        if all_ready:
            st.success("✅ All 4 files ready")
        else:
            missing = [n for f,n in [(fba_file,"FBA"),(rb_file,"Restricted Brands"),(arch_file,"Archive"),(an_file,"Analysis")] if not f]
            st.info("Waiting for: " + ", ".join(missing))

    st.markdown("<hr class='divhr'>", unsafe_allow_html=True)

    # ── column healing preview (runs on upload before user clicks Run) ─────────
    if all_ready:
        st.markdown("### 🔬 Column auto-detection preview")
        st.markdown("<div class='card-sub'>Reviewing your analysis file columns before processing</div>", unsafe_allow_html=True)

        an_df_preview = read_file(an_file)
        an_file.seek(0)  # reset pointer for later use

        healing_needed = False
        heal_map = {}

        for an_col, targets in AN_COL_TARGETS.items():
            found_col, confidence, found_name, suggested = smart_find_col(an_df_preview, targets)
            if found_col:
                heal_map[an_col] = found_col
                if confidence == 'fuzzy':
                    healing_needed = True
                    st.markdown(f"""
                    <div class='heal-box'>
                        🔧 Column <span class='heal-found'>"{found_name}"</span> detected —
                        mapping to <span class='heal-suggested'>"{an_col}"</span>
                        <span class='pill p-calc'>fuzzy match</span>
                    </div>""", unsafe_allow_html=True)
            else:
                if an_col not in ["Days of stock(30)", "Days of stock(3)", "Sales 30", "Sales 3", "Restricted"]:
                    st.markdown(f"""
                    <div class='alert-box alert-amber'>
                        ⚠️ Could not find column <strong>"{an_col}"</strong> in analysis file.
                        It will be created if data is found.
                    </div>""", unsafe_allow_html=True)

        if not healing_needed:
            st.markdown("<div class='alert-box alert-green'>✅ All columns matched exactly — no healing needed</div>", unsafe_allow_html=True)

        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)

    run_btn = st.button("⚡ Run BuyIQ Engine", disabled=not all_ready, use_container_width=True, type="primary")

    if run_btn and all_ready:
        t0 = time.time()
        logs = []

        def log(msg, kind="info"):
            cls = {"ok":"lok","warn":"lwarn","err":"lerr","head":"lhead"}.get(kind,"linfo")
            logs.append(f'<span class="{cls}">{msg}</span>')

        prog = st.progress(0)
        status = st.empty()

        # ── read all files ──────────────────────────────────────────────────
        status.write("Reading files...")
        fba_file.seek(0); rb_file.seek(0); arch_file.seek(0); an_file.seek(0)
        fba_df  = read_file(fba_file)
        rb_df   = read_file(rb_file)
        arch_df = read_file(arch_file)
        an_df   = read_file(an_file)

        if any(df.empty for df in [fba_df, rb_df, arch_df, an_df]):
            st.error("One or more files could not be read. Please check the files and try again.")
            st.stop()

        prog.progress(12)
        log("◆ FILES LOADED", "head")
        log(f"  FBA Inventory    → {len(fba_df):,} rows | {len(fba_df.columns)} cols", "ok")
        log(f"  Restricted Brands→ {len(rb_df):,} brands", "ok")
        log(f"  Archive Inventory→ {len(arch_df):,} rows | {len(arch_df.columns)} cols", "ok")
        log(f"  Analysis file    → {len(an_df):,} rows | {len(an_df.columns)} cols", "ok")

        # ── restricted brands ───────────────────────────────────────────────
        status.write("Building restricted brands index...")
        rb_col = rb_df.columns[0]
        restricted_set = set(rb_df[rb_col].str.strip().str.lower().dropna())
        log(f"◆ RESTRICTED INDEX — {len(restricted_set):,} brands", "head")
        prog.progress(22)

        # ── FBA map ─────────────────────────────────────────────────────────
        status.write("Indexing FBA Inventory...")
        fba_asin_col, _, _, _ = smart_find_col(fba_df, ["asin","ASIN"])
        fba_map = {}
        if fba_asin_col:
            for _, r in fba_df.iterrows():
                k = str(r[fba_asin_col]).strip().upper()
                if k and k not in ("ASIN",""):
                    fba_map[k] = r.to_dict()
        log(f"◆ FBA MAP — {len(fba_map):,} unique ASINs", "head")
        prog.progress(35)

        # ── Archive map ──────────────────────────────────────────────────────
        status.write("Indexing Archive Inventory...")
        arch_asin_col, _, _, _ = smart_find_col(arch_df, ["asin","asin(A-Z)","ASIN"])
        arch_map = {}
        if arch_asin_col:
            for _, r in arch_df.iterrows():
                k = str(r[arch_asin_col]).strip().upper()
                if k and k not in ("ASIN","ASIN(A-Z)","ASIN(Z-A)",""):
                    if k not in arch_map:
                        arch_map[k] = r.to_dict()
        log(f"◆ ARCHIVE MAP — {len(arch_map):,} unique ASINs", "head")
        prog.progress(48)

        # ── locate analysis cols with smart detection ───────────────────────
        status.write("Smart column detection...")
        an_asin_col, _, _, _  = smart_find_col(an_df, ["asin","ASIN"])
        an_brand_col, _, _, _ = smart_find_col(an_df, ["brand","Brand","BRAND"])

        col_map = {}  # canonical_name → actual_col_in_an_df
        for canon, targets in AN_COL_TARGETS.items():
            found, conf, found_name, _ = smart_find_col(an_df, targets)
            col_map[canon] = found  # may be None

        log("◆ ANALYSIS COLUMN MAP", "head")
        for k, v in col_map.items():
            log(f"  {k:36} → {v or '⚠ will create'}", "ok" if v else "warn")
        prog.progress(58)

        # ── process rows ────────────────────────────────────────────────────
        status.write("Processing rows...")
        out_rows = []
        fba_hits = arch_hits = restricted_count = filled_cells = 0
        anomalies = []
        n = len(an_df)

        def get_an(row, canon):
            c = col_map.get(canon)
            return row.get(c, "") if c else ""

        def set_an(nr, canon, val):
            global filled_cells
            c = col_map.get(canon)
            if c is None:
                col_map[canon] = canon
                c = canon
            if is_blank(nr.get(c, "")):
                nr[c] = val
                return True
            return False

        def fba_val(fba_row, canon):
            for candidate in FBA_FILL_MAP.get(canon, []):
                for k, v in fba_row.items():
                    if k.strip().lower() == candidate.lower() and not is_blank(v):
                        return v
            return None

        def arch_val(arch_row, canon):
            for candidate in ARCH_FILL_MAP.get(canon, []):
                for k, v in arch_row.items():
                    if k.strip().lower() == candidate.lower() and not is_blank(v):
                        return v
            return None

        for idx, row in an_df.iterrows():
            nr    = row.to_dict()
            asin  = str(row[an_asin_col]).strip().upper()  if an_asin_col  else ""
            brand = str(row[an_brand_col]).strip().lower() if an_brand_col else ""
            brand_display = str(row[an_brand_col]).strip() if an_brand_col else ""

            fba_hit  = asin in fba_map
            arch_hit = asin in arch_map

            if fba_hit:
                fba_hits += 1
                fba = fba_map[asin]
                for canon in ["Stock", "Reserve", "Inbound", "TOTAL(Stock+Reserve+inbound)"]:
                    v = fba_val(fba, canon)
                    if v is not None:
                        if set_an(nr, canon, v):
                            filled_cells += 1

            if arch_hit:
                if not fba_hit: arch_hits += 1
                arch = arch_map[asin]
                for canon in ["Stock", "Reserve", "TOTAL(Stock+Reserve+inbound)"]:
                    v = arch_val(arch, canon)
                    if v is not None:
                        if set_an(nr, canon, v):
                            filled_cells += 1

            # restricted flag
            is_r = bool(brand and brand in restricted_set)
            if is_r: restricted_count += 1
            restr_col = col_map.get("Restricted") or "Restricted"
            if restr_col not in nr or is_blank(nr.get(restr_col,"")):
                nr[restr_col] = "Yes — Restricted" if is_r else "No"
                if restr_col not in col_map: col_map["Restricted"] = restr_col

            # recalculate days of stock
            stock_v = safe_float(nr.get(col_map.get("Stock",""), 0))
            s30_v   = safe_float(nr.get(col_map.get("Sales 30",""), 0))
            s3_v    = safe_float(nr.get(col_map.get("Sales 3",""),  0))

            dos30_col = col_map.get("Days of stock(30)")
            dos3_col  = col_map.get("Days of stock(3)")
            if dos30_col and s30_v > 0:
                nr[dos30_col] = round(stock_v / (s30_v / 30), 1)
            if dos3_col and s3_v > 0:
                nr[dos3_col]  = round(stock_v / (s3_v / 3),  1)

            # ── anomaly detection ───────────────────────────────────────────
            listing_col, _, _, _ = smart_find_col(an_df, ["listing status","afn-listing","mfn-listing"])
            listing_val = str(nr.get(listing_col or "", "")).lower() if listing_col else ""

            if stock_v == 0 and s30_v > 5:
                anomalies.append({
                    "type": "🔴 Zero stock, high velocity",
                    "asin": asin, "brand": brand_display,
                    "detail": f"0 stock | {s30_v:.0f} units sold last 30d",
                    "severity": "red"
                })
            elif dos30_col and s30_v > 0:
                dos_val = safe_float(nr.get(dos30_col, 999))
                if 0 < dos_val < 7:
                    anomalies.append({
                        "type": "🟡 Critical low stock",
                        "asin": asin, "brand": brand_display,
                        "detail": f"{dos_val} days of stock remaining",
                        "severity": "amber"
                    })
                elif 7 <= dos_val < 14:
                    anomalies.append({
                        "type": "🟠 Low stock warning",
                        "asin": asin, "brand": brand_display,
                        "detail": f"{dos_val} days of stock remaining",
                        "severity": "amber"
                    })

            if is_r and "yes" in listing_val:
                anomalies.append({
                    "type": "🚫 Restricted brand active listing",
                    "asin": asin, "brand": brand_display,
                    "detail": f"Brand '{brand_display}' is restricted but listing is active",
                    "severity": "red"
                })

            out_rows.append(nr)
            if idx % max(1, n // 25) == 0:
                prog.progress(58 + int(35 * idx / n))

        prog.progress(95)
        out_df = pd.DataFrame(out_rows)

        # write excel
        status.write("Writing output...")
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            out_df.to_excel(writer, index=False, sheet_name="Analysis_Filled")
            # anomalies sheet
            if anomalies:
                anom_df = pd.DataFrame(anomalies)
                anom_df.to_excel(writer, index=False, sheet_name="Anomaly_Alerts")
        buf.seek(0)
        prog.progress(100)
        t1 = time.time()
        status.empty()

        log(f"◆ COMPLETE in {t1-t0:.2f}s", "head")
        log(f"  Rows processed   : {n:,}", "ok")
        log(f"  FBA matched      : {fba_hits:,} ({pct(fba_hits,n)}%)", "ok")
        log(f"  Archive matched  : {arch_hits:,} ({pct(arch_hits,n)}%)", "ok")
        log(f"  Cells auto-filled: {filled_cells:,}", "ok")
        log(f"  Restricted flagged: {restricted_count:,}", "warn" if restricted_count else "ok")
        log(f"  Anomalies found  : {len(anomalies):,}", "warn" if anomalies else "ok")

        # save result to session
        match_rate = pct(fba_hits, n)
        result = {
            "out_df": out_df, "buf": buf.getvalue(),
            "n": n, "fba_hits": fba_hits, "arch_hits": arch_hits,
            "filled_cells": filled_cells, "restricted_count": restricted_count,
            "anomalies": anomalies, "match_rate": match_rate,
            "logs": logs, "elapsed": round(t1-t0,2),
            "vendor": vendor_name or "Unknown",
            "run_date": str(date.today()),
            "an_df": an_df, "col_map": col_map,
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

    # ── show results if available ──────────────────────────────────────────────
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
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="font-size:0.72rem;color:#3a3a5a;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin:0.5rem 0 0.2rem">
          Match accuracy — {r['match_rate']}%
        </div>
        <div class="prog-wrap"><div class="prog-fill" style="width:{r['match_rate']}%"></div></div>
        """, unsafe_allow_html=True)

        st.markdown(f'<div class="log-box">{"<br>".join(r["logs"])}</div>', unsafe_allow_html=True)

        # anomaly alerts
        if r['anomalies']:
            st.markdown(f"### ⚠️ Anomaly alerts ({len(r['anomalies'])} found)")
            red_a   = [a for a in r['anomalies'] if a['severity']=='red']
            amber_a = [a for a in r['anomalies'] if a['severity']=='amber']

            if red_a:
                st.markdown(f"**🔴 Critical ({len(red_a)})**")
                for a in red_a[:10]:
                    st.markdown(f"""
                    <div class="alert-box alert-red">
                      <strong>{a['type']}</strong> &nbsp;|&nbsp; ASIN: <code>{a['asin']}</code>
                      &nbsp;|&nbsp; Brand: {a['brand']} &nbsp;|&nbsp; {a['detail']}
                    </div>""", unsafe_allow_html=True)
            if amber_a:
                st.markdown(f"**🟡 Warnings ({len(amber_a)})**")
                for a in amber_a[:10]:
                    st.markdown(f"""
                    <div class="alert-box alert-amber">
                      <strong>{a['type']}</strong> &nbsp;|&nbsp; ASIN: <code>{a['asin']}</code>
                      &nbsp;|&nbsp; Brand: {a['brand']} &nbsp;|&nbsp; {a['detail']}
                    </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-box alert-green">✅ No anomalies detected — all ASINs look healthy</div>', unsafe_allow_html=True)

        fname = f"Analysis_Filled_{date.today()}.xlsx"
        st.download_button(
            label=f"⬇️  Download  {fname}  ({len(r['anomalies'])} anomalies flagged inside)",
            data=r['buf'], file_name=fname,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True, type="primary"
        )

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
with tab_dash:
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)

    if not st.session_state.run_result:
        st.markdown('<div class="alert-box alert-blue">Run the engine first to see your dashboard.</div>', unsafe_allow_html=True)
    else:
        r = st.session_state.run_result
        out_df  = r['out_df']
        col_map = r['col_map']

        st.markdown("### 📊 Live dashboard")
        st.markdown(f"<div class='card-sub'>Vendor: {r['vendor']} &nbsp;|&nbsp; Run date: {r['run_date']} &nbsp;|&nbsp; {r['elapsed']}s processing time</div>", unsafe_allow_html=True)

        # top 10 low stock ASINs
        st.markdown("#### 🔻 Top 10 lowest stock ASINs")
        stock_col_actual = col_map.get("Stock")
        asin_col_actual  = r['an_df'].columns[0] if not out_df.empty else None
        an_asin_c, _, _, _ = smart_find_col(out_df, ["asin","ASIN"])
        an_brand_c, _, _, _ = smart_find_col(out_df, ["brand","Brand"])

        if stock_col_actual and stock_col_actual in out_df.columns:
            tmp = out_df.copy()
            tmp["_stock_num"] = tmp[stock_col_actual].apply(safe_float)
            low_stock = tmp.nsmallest(10, "_stock_num")[[c for c in [an_asin_c, an_brand_c, stock_col_actual] if c]]
            low_stock.columns = [c for c in ["ASIN","Brand","Stock"] if c][:len(low_stock.columns)]
            st.dataframe(low_stock, use_container_width=True, hide_index=True)
        else:
            st.info("Stock column not found in output — run engine first.")

        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)

        # restricted brand summary
        st.markdown("#### 🚫 Restricted brand breakdown")
        restr_col_actual = col_map.get("Restricted","Restricted")
        if restr_col_actual in out_df.columns and an_brand_c:
            restr_df = out_df[out_df[restr_col_actual].str.contains("Restricted",na=False)]
            if not restr_df.empty:
                brand_counts = restr_df[an_brand_c].value_counts().reset_index()
                brand_counts.columns = ["Brand","Count"]
                st.dataframe(brand_counts, use_container_width=True, hide_index=True)
                st.markdown(f'<div class="alert-box alert-red">🚫 {len(restr_df)} restricted brand ASINs found across {brand_counts["Brand"].nunique()} brands</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-box alert-green">✅ No restricted brands detected in this file</div>', unsafe_allow_html=True)

        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)

        # anomaly summary
        st.markdown("#### ⚠️ Anomaly summary")
        anomalies = r['anomalies']
        if anomalies:
            anom_df_view = pd.DataFrame(anomalies)[["type","asin","brand","detail"]]
            anom_df_view.columns = ["Alert Type","ASIN","Brand","Detail"]
            st.dataframe(anom_df_view, use_container_width=True, hide_index=True)
        else:
            st.markdown('<div class="alert-box alert-green">✅ No anomalies detected</div>', unsafe_allow_html=True)

        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)

        # match rate gauge
        st.markdown("#### 🎯 Match accuracy")
        mr = r['match_rate']
        color = "#34d399" if mr >= 80 else "#fbbf24" if mr >= 50 else "#f87171"
        st.markdown(f"""
        <div style="text-align:center; padding:1.5rem;">
          <div style="font-family:'Space Grotesk',sans-serif; font-size:4rem; font-weight:700; color:{color};">{mr}%</div>
          <div style="color:#3a3a5a; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.1em; margin-top:0.5rem;">
            FBA match rate &nbsp;|&nbsp; {r['fba_hits']:,} of {r['n']:,} ASINs matched
          </div>
          <div class="prog-wrap" style="max-width:400px; margin:1rem auto;">
            <div class="prog-fill" style="width:{mr}%"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — VENDOR HISTORY
# ─────────────────────────────────────────────────────────────────────────────
with tab_history:
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    st.markdown("### 📈 Vendor run history")
    st.markdown("<div class='card-sub'>Tracks every time you run the engine with a vendor name</div>", unsafe_allow_html=True)

    history = st.session_state.vendor_history
    if not history:
        st.markdown('<div class="alert-box alert-blue">No history yet. Enter a vendor name in the Run tab before processing to start tracking.</div>', unsafe_allow_html=True)
    else:
        hist_df = pd.DataFrame(history)
        hist_df.columns = ["Vendor","Date","Rows","Match Rate (%)","Cells Filled","Restricted","Anomalies"]
        st.dataframe(hist_df, use_container_width=True, hide_index=True)

        # summary per vendor
        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown("#### Per-vendor summary")
        summary = hist_df.groupby("Vendor").agg({
            "Rows": "sum",
            "Match Rate (%)": "mean",
            "Cells Filled": "sum",
            "Restricted": "sum",
            "Anomalies": "sum"
        }).round(1).reset_index()
        st.dataframe(summary, use_container_width=True, hide_index=True)

        if st.button("🗑 Clear history"):
            st.session_state.vendor_history = []
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
