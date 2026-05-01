import streamlit as st
import pandas as pd
import io
import time
from datetime import date

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
.stApp { background: #0a0a0f; color: #e8e8f0; }

.hero {
    background: linear-gradient(135deg, #0f0f1a 0%, #141428 50%, #0f1a0f 100%);
    border: 1px solid #1e1e3a; border-radius: 20px;
    padding: 3rem 2.5rem 2.5rem; margin-bottom: 2rem;
}
.hero-badge {
    display: inline-block; background: rgba(99,102,241,0.15); color: #818cf8;
    border: 1px solid rgba(99,102,241,0.3); border-radius: 20px;
    padding: 4px 14px; font-size: 0.72rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 1rem;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif; font-size: 2.8rem; font-weight: 700;
    background: linear-gradient(135deg, #a5b4fc 0%, #818cf8 40%, #34d399 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin: 0 0 0.5rem; line-height: 1.1;
}
.hero-sub { font-size: 1rem; color: #6b7280; font-weight: 400; margin: 0; }

.section-head { font-family: 'Space Grotesk', sans-serif; font-size: 1rem; font-weight: 600; color: #c8c8e8; margin: 0 0 0.3rem; }
.section-sub  { font-size: 0.75rem; color: #4f4f7a; margin: 0 0 1rem; text-transform: uppercase; letter-spacing: 0.08em; }

.log-container {
    background: #070710; border: 1px solid #151530; border-radius: 12px;
    padding: 1.2rem 1.4rem; font-family: 'Courier New', monospace;
    font-size: 0.8rem; line-height: 1.9; max-height: 300px; overflow-y: auto; margin: 1rem 0;
}
.log-ok   { color: #34d399; }
.log-warn { color: #fbbf24; }
.log-err  { color: #f87171; }
.log-head { color: #818cf8; font-weight: 700; }
.log-info { color: #6b7280; }

.prog-wrap { background: #1a1a30; border-radius: 8px; height: 6px; margin: 0.6rem 0; overflow: hidden; }
.prog-fill { height: 100%; border-radius: 8px; background: linear-gradient(90deg, #6366f1, #34d399); }

.col-map { width:100%; border-collapse:collapse; font-size:0.78rem; margin-top:0.6rem; }
.col-map th { background:#111124; color:#4f4f7a; font-weight:700; padding:8px 12px; text-align:left; letter-spacing:0.07em; font-size:0.68rem; text-transform:uppercase; border-bottom:1px solid #1e1e3a; }
.col-map td { padding:7px 12px; border-bottom:1px solid #0f0f1e; color:#9090b0; }
.col-map td:first-child { color:#c8c8e8; font-weight:500; }
.pill { display:inline-block; padding:2px 10px; border-radius:20px; font-size:0.68rem; font-weight:700; }
.p-fba  { background:rgba(99,102,241,0.15); color:#818cf8; }
.p-arch { background:rgba(16,185,129,0.12); color:#34d399; }
.p-rb   { background:rgba(251,191,36,0.12); color:#fbbf24; }
.p-calc { background:rgba(167,139,250,0.12); color:#c4b5fd; }
.divhr  { border:none; border-top:1px solid #1a1a2e; margin:1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ── hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-badge">⚡ Buying Intelligence Engine</div>
  <div class="hero-title">BuyIQ</div>
  <p class="hero-sub">Automated ASIN matching across FBA Inventory, Archive &amp; Restricted Brands — zero manual VLOOKUP.</p>
</div>
""", unsafe_allow_html=True)

# ── column map reference ──────────────────────────────────────────────────────
with st.expander("📋 Column mapping reference — click to expand"):
    st.markdown("""
<table class="col-map">
<tr><th>Analysis column</th><th>Source</th><th>Source column</th><th>Logic</th></tr>
<tr><td>Stock</td><td><span class="pill p-fba">FBA Inv</span></td><td>STOCK</td><td>Direct fill if blank</td></tr>
<tr><td>Reserve</td><td><span class="pill p-fba">FBA Inv</span></td><td>RESERVE</td><td>Direct fill if blank</td></tr>
<tr><td>Inbound</td><td><span class="pill p-fba">FBA Inv</span></td><td>INBOUND</td><td>Direct fill if blank</td></tr>
<tr><td>TOTAL(Stock+Reserve+inbound)</td><td><span class="pill p-fba">FBA Inv</span></td><td>afn-total-quantity</td><td>Direct fill if blank</td></tr>
<tr><td>Stock (fallback)</td><td><span class="pill p-arch">Archive</span></td><td>afn-fulfillable-quantity</td><td>Only if FBA had no match</td></tr>
<tr><td>Reserve (fallback)</td><td><span class="pill p-arch">Archive</span></td><td>afn-reserved-quantity</td><td>Only if FBA had no match</td></tr>
<tr><td>TOTAL (fallback)</td><td><span class="pill p-arch">Archive</span></td><td>afn-total-quantity</td><td>Only if FBA had no match</td></tr>
<tr><td>Restricted</td><td><span class="pill p-rb">Restricted Brands</span></td><td>Brand name list</td><td>Exact brand name match</td></tr>
<tr><td>Days of stock(30)</td><td><span class="pill p-calc">Calculated</span></td><td>—</td><td>Stock ÷ (Sales30 ÷ 30)</td></tr>
<tr><td>Days of stock(3)</td><td><span class="pill p-calc">Calculated</span></td><td>—</td><td>Stock ÷ (Sales3 ÷ 3)</td></tr>
</table>
""", unsafe_allow_html=True)

st.markdown("<hr class='divhr'>", unsafe_allow_html=True)

# ── helpers ───────────────────────────────────────────────────────────────────
def read_file(f):
    try:
        if f.name.lower().endswith(".csv"):
            return pd.read_csv(f, dtype=str).fillna("")
        return pd.read_excel(f, dtype=str).fillna("")
    except Exception as e:
        st.error(f"Cannot read {f.name}: {e}")
        return pd.DataFrame()

def col_exact(df, name):
    for c in df.columns:
        if c.strip().lower() == name.strip().lower():
            return c
    return None

def col_fuzzy(df, *candidates):
    for cand in candidates:
        for c in df.columns:
            if cand.lower() in c.lower():
                return c
    return None

def is_blank(v):
    return str(v).strip() in ("", "N/A", "#N/A", "#VALUE!", "nan", "NaN")

def pct(a, b):
    return round(a / b * 100, 1) if b else 0

# ── uploads ───────────────────────────────────────────────────────────────────
left, right = st.columns(2, gap="large")

with left:
    st.markdown('<div class="section-head">Step 1 — Source files</div><div class="section-sub">Upload the 3 daily files</div>', unsafe_allow_html=True)
    fba_file  = st.file_uploader("📦 FBA Inventory",     type=["xlsx","xls","csv"], key="fba")
    rb_file   = st.file_uploader("🚫 Restricted Brands", type=["xlsx","xls","csv"], key="rb")
    arch_file = st.file_uploader("🗃️ Archive Inventory", type=["xlsx","xls","csv"], key="arch")

with right:
    st.markdown('<div class="section-head">Step 2 — Analysis file</div><div class="section-sub">The file with blank / #N/A columns</div>', unsafe_allow_html=True)
    an_file = st.file_uploader("📊 Analysis file", type=["xlsx","xls","csv"], key="an")
    st.markdown("<br>", unsafe_allow_html=True)
    if fba_file and rb_file and arch_file and an_file:
        st.success("✅ All 4 files ready")
    else:
        missing = [n for f,n in [(fba_file,"FBA Inventory"),(rb_file,"Restricted Brands"),(arch_file,"Archive Inventory"),(an_file,"Analysis file")] if not f]
        st.info("Waiting for: " + ", ".join(missing))

st.markdown("<hr class='divhr'>", unsafe_allow_html=True)

run = st.button("⚡ Run BuyIQ Engine", disabled=not (fba_file and rb_file and arch_file and an_file), use_container_width=True, type="primary")

if run:
    t0 = time.time()
    logs = []

    def log(msg, kind="info"):
        cls = {"ok":"log-ok","warn":"log-warn","err":"log-err","head":"log-head"}.get(kind,"log-info")
        logs.append(f'<span class="{cls}">{msg}</span>')

    prog_bar = st.progress(0)
    status   = st.empty()

    # read
    status.write("Reading files...")
    fba_df  = read_file(fba_file)
    rb_df   = read_file(rb_file)
    arch_df = read_file(arch_file)
    an_df   = read_file(an_file)
    prog_bar.progress(15)

    log("◆ FILES LOADED", "head")
    log(f"  FBA Inventory    → {len(fba_df):,} rows | {len(fba_df.columns)} cols", "ok")
    log(f"  Restricted Brands→ {len(rb_df):,} entries", "ok")
    log(f"  Archive Inventory→ {len(arch_df):,} rows | {len(arch_df.columns)} cols", "ok")
    log(f"  Analysis file    → {len(an_df):,} rows | {len(an_df.columns)} cols", "ok")

    # restricted set
    rb_col = rb_df.columns[0]
    restricted_set = set(rb_df[rb_col].str.strip().str.lower().dropna())
    log(f"◆ RESTRICTED INDEX — {len(restricted_set):,} brands", "head")
    prog_bar.progress(25)

    # FBA map
    fba_asin_col = col_exact(fba_df,"asin") or col_fuzzy(fba_df,"asin")
    fba_map = {}
    if fba_asin_col:
        for _, r in fba_df.iterrows():
            k = str(r[fba_asin_col]).strip().upper()
            if k: fba_map[k] = r.to_dict()
    log(f"◆ FBA MAP — {len(fba_map):,} unique ASINs indexed", "head")
    prog_bar.progress(40)

    # Archive map — handle asin(A-Z) header
    arch_asin_col = col_exact(arch_df,"asin") or col_exact(arch_df,"asin(A-Z)") or col_fuzzy(arch_df,"asin")
    arch_map = {}
    if arch_asin_col:
        for _, r in arch_df.iterrows():
            k = str(r[arch_asin_col]).strip().upper()
            if k and k not in arch_map: arch_map[k] = r.to_dict()
    log(f"◆ ARCHIVE MAP — {len(arch_map):,} unique ASINs indexed", "head")
    prog_bar.progress(55)

    # locate analysis columns
    def ac(exact, *fuzzy):
        return col_exact(an_df, exact) or col_fuzzy(an_df, exact, *fuzzy)

    an_asin    = col_fuzzy(an_df, "asin")
    an_brand   = col_fuzzy(an_df, "brand")
    an_stock   = ac("Stock")
    an_reserve = ac("Reserve")
    an_inbound = ac("Inbound")
    an_total   = ac("TOTAL(Stock+Reserve+inbound)", "TOTAL(Stock", "total")
    an_restr   = ac("Restricted")
    an_dos30   = ac("Days of stock(30)", "days of stock(30)")
    an_dos3    = ac("Days of stock(3)",  "days of stock(3)")
    an_s30     = ac("Sales 30")
    an_s3      = ac("Sales 3")

    log("◆ ANALYSIS COLUMN MAP", "head")
    for lbl, col in [("ASIN", an_asin),("Brand", an_brand),("Stock", an_stock),
                     ("Reserve", an_reserve),("Inbound", an_inbound),("TOTAL", an_total),
                     ("Restricted", an_restr),("DoS-30", an_dos30),("DoS-3", an_dos3)]:
        log(f"  {lbl:14}→  {col or '⚠ not found'}", "ok" if col else "warn")
    prog_bar.progress(65)

    # process rows
    status.write("Processing rows...")
    out = []
    fba_hits = arch_hits = restricted_count = filled = 0
    n = len(an_df)

    for idx, row in an_df.iterrows():
        nr    = row.to_dict()
        asin  = str(row[an_asin]).strip().upper()  if an_asin  else ""
        brand = str(row[an_brand]).strip().lower() if an_brand else ""

        fba_hit  = asin in fba_map
        arch_hit = asin in arch_map

        if fba_hit:
            fba_hits += 1
            fba = fba_map[asin]
            for an_c, fba_c in [(an_stock,"STOCK"),(an_reserve,"RESERVE"),
                                 (an_inbound,"INBOUND"),(an_total,"afn-total-quantity")]:
                if an_c and is_blank(nr.get(an_c,"")):
                    v = fba.get(fba_c,"")
                    if not is_blank(v):
                        nr[an_c] = v; filled += 1

        if arch_hit:
            if not fba_hit: arch_hits += 1
            arch = arch_map[asin]
            for an_c, ar_c in [(an_stock,"afn-fulfillable-quantity"),
                                (an_reserve,"afn-reserved-quantity"),
                                (an_total,"afn-total-quantity")]:
                if an_c and is_blank(nr.get(an_c,"")):
                    v = arch.get(ar_c,"")
                    if not is_blank(v):
                        nr[an_c] = v; filled += 1

        # restricted
        is_r = bool(brand and brand in restricted_set)
        if is_r: restricted_count += 1
        flag = "Yes — Restricted" if is_r else "No"
        if an_restr: nr[an_restr] = flag
        else:        nr["Restricted"] = flag

        # days of stock
        try:
            stock_v = float(nr.get(an_stock,0) or 0) if an_stock else 0
            s30_v   = float(nr.get(an_s30,0)   or 0) if an_s30   else 0
            s3_v    = float(nr.get(an_s3,0)    or 0) if an_s3    else 0
            if an_dos30 and s30_v > 0:
                nr[an_dos30] = round(stock_v / (s30_v / 30), 1)
            if an_dos3 and s3_v > 0:
                nr[an_dos3]  = round(stock_v / (s3_v / 3),  1)
        except: pass

        out.append(nr)
        if idx % max(1, n // 20) == 0:
            prog_bar.progress(65 + int(30 * idx / n))

    prog_bar.progress(95)
    out_df = pd.DataFrame(out)

    # write excel
    status.write("Writing output...")
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        out_df.to_excel(writer, index=False, sheet_name="Analysis_Filled")
    buf.seek(0)
    prog_bar.progress(100)
    t1 = time.time()
    status.empty()

    log(f"◆ COMPLETE in {t1-t0:.2f}s", "head")
    log(f"  Total rows       : {n:,}", "ok")
    log(f"  FBA matches      : {fba_hits:,}  ({pct(fba_hits,n)}%)", "ok")
    log(f"  Archive matches  : {arch_hits:,}  ({pct(arch_hits,n)}%)", "ok")
    log(f"  Cells filled     : {filled:,}", "ok")
    log(f"  Restricted       : {restricted_count:,}", "warn" if restricted_count else "ok")
    unmatched = n - max(fba_hits, 1) if fba_hits else n
    if unmatched > 0:
        log(f"  Unmatched ASINs  : {unmatched:,}  — verify source files contain all ASINs", "warn")

    # ── results ───────────────────────────────────────────────────────────────
    st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
    st.markdown("### 📊 Run report")

    match_rate = pct(fba_hits, n)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows processed",     f"{n:,}")
    c2.metric("FBA matched",        f"{fba_hits:,}", f"{match_rate}% rate")
    c3.metric("Cells auto-filled",  f"{filled:,}")
    c4.metric("Restricted flagged", f"{restricted_count:,}")

    st.markdown(f"""
    <div style="margin:1rem 0 0.2rem;font-size:0.75rem;color:#6b7280;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;">Match accuracy — {match_rate}%</div>
    <div class="prog-wrap"><div class="prog-fill" style="width:{match_rate}%"></div></div>
    <div style="font-size:0.72rem;color:#4f4f7a;margin-bottom:1rem;">{fba_hits:,} of {n:,} ASINs found in FBA Inventory</div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="log-container">{"<br>".join(logs)}</div>', unsafe_allow_html=True)

    fname = f"Analysis_Filled_{date.today()}.xlsx"
    st.download_button(
        label=f"⬇️  Download  {fname}",
        data=buf, file_name=fname,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True, type="primary"
    )
