"""
VirVentures DataOps — Buying Intelligence Engine
Supabase-backed · Pattern ASIN detection · Dual-table archive · Full audit trail
"""

import streamlit as st
import pandas as pd
import io, re, time, base64
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

st.set_page_config(
    page_title="VirVentures DataOps",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════════════════════
#  BRAND COLORS
#  Orange: #F47920   Navy: #1E2D4E   Light Navy: #2A3F6F   BG: #07080F
# ═══════════════════════════════════════════════════════════════════════════════

def get_logo_b64():
    try:
        logo_path = Path(__file__).parent / "logo.jpg"
        if logo_path.exists():
            return base64.b64encode(logo_path.read_bytes()).decode()
    except: pass
    return None

LOGO_B64 = get_logo_b64()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}

/* ── BASE ── */
.stApp{background:#F5F6FA;color:#1E2D4E;}
.block-container{padding-top:0!important;max-width:1400px;}
section[data-testid="stSidebar"]{display:none;}

/* ── TOPBAR ── */
.topbar{
    background:linear-gradient(135deg,#1E2D4E 0%,#2A3F6F 100%);
    border-bottom:3px solid #F47920;
    padding:1rem 2.5rem;
    display:flex;align-items:center;gap:1.4rem;
    margin-bottom:0;
    box-shadow:0 4px 24px rgba(30,45,78,0.15);
}
.topbar-logo{height:52px;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.3);}
.topbar-title{font-family:'Space Grotesk',sans-serif;font-size:1.4rem;font-weight:800;color:#ffffff;letter-spacing:0.01em;margin:0;}
.topbar-sub{font-size:0.7rem;color:#F47920;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;margin:2px 0 0;}
.topbar-badge{
    margin-left:auto;background:#F47920;color:white;
    border-radius:20px;padding:5px 16px;
    font-size:0.7rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;
    box-shadow:0 2px 8px rgba(244,121,32,0.4);
}

/* ── MAIN CONTENT AREA ── */
.main-content{background:#F5F6FA;padding:1.5rem 0;}

/* ── CARDS ── */
.vv-card{background:#ffffff;border:1px solid #E8EBF0;border-radius:16px;padding:1.5rem 1.6rem;margin-bottom:1rem;box-shadow:0 2px 12px rgba(30,45,78,0.06);}
.card-title{font-family:'Space Grotesk',sans-serif;font-size:0.95rem;font-weight:700;color:#F47920;margin-bottom:0.2rem;}
.card-sub{font-size:0.7rem;color:#8A9BB5;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:1rem;}

/* ── METRICS ── */
.metric-row{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:1.2rem 0;}
.metric-box{
    background:#ffffff;border:1px solid #E8EBF0;border-radius:14px;
    padding:1.2rem 1.1rem;text-align:center;
    box-shadow:0 2px 10px rgba(30,45,78,0.06);
    border-top:3px solid #E8EBF0;
    transition:transform 0.15s;
}
.metric-box:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(30,45,78,0.1);}
.metric-box.orange{border-top-color:#F47920;}
.metric-box.navy  {border-top-color:#1E2D4E;}
.metric-box.green {border-top-color:#16a34a;}
.metric-box.red   {border-top-color:#dc2626;}
.m-val{font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:800;line-height:1;}
.m-val.orange{color:#F47920;}.m-val.navy{color:#1E2D4E;}
.m-val.green{color:#16a34a;}.m-val.red{color:#dc2626;}
.m-lbl{font-size:0.65rem;color:#8A9BB5;margin-top:5px;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;}

/* ── LOG BOX ── */
.log-box{
    background:#1E2D4E;border:1px solid #2A3F6F;border-radius:12px;
    padding:1rem 1.3rem;font-family:'Courier New',monospace;
    font-size:0.77rem;line-height:1.9;max-height:280px;overflow-y:auto;margin:0.8rem 0;
}
.lok{color:#4ade80;}.lwarn{color:#fb923c;}.lerr{color:#f87171;}
.lhead{color:#F47920;font-weight:700;}.linfo{color:#6b7fa3;}

/* ── PROGRESS ── */
.prog-wrap{background:#E8EBF0;border-radius:8px;height:6px;margin:0.5rem 0;overflow:hidden;}
.prog-fill{height:100%;border-radius:8px;background:linear-gradient(90deg,#F47920,#ffb347);}

/* ── ALERTS ── */
.alert-box{border-radius:12px;padding:0.9rem 1.2rem;margin:0.4rem 0;font-size:0.83rem;font-weight:500;}
.alert-red   {background:#FEF2F2;border:1px solid #FECACA;color:#991B1B;}
.alert-amber {background:#FFF7ED;border:1px solid #FED7AA;color:#92400E;}
.alert-green {background:#F0FDF4;border:1px solid #BBF7D0;color:#166534;}
.alert-blue  {background:#EFF6FF;border:1px solid #BFDBFE;color:#1E40AF;}
.alert-orange{background:#FFF7ED;border:1px solid #F47920;color:#9A3412;}

/* ── MAP TABLE ── */
.map-table{width:100%;border-collapse:collapse;font-size:0.79rem;margin:0.5rem 0;}
.map-table th{background:#F8F9FC;color:#8A9BB5;font-weight:700;padding:9px 14px;text-align:left;letter-spacing:0.07em;font-size:0.67rem;text-transform:uppercase;border-bottom:2px solid #E8EBF0;}
.map-table td{padding:8px 14px;border-bottom:1px solid #F0F2F7;color:#4A5568;}
.map-table td:first-child{color:#1E2D4E;font-weight:600;}
.map-table tr:hover td{background:#F8F9FC;}
.pill{display:inline-block;padding:2px 10px;border-radius:20px;font-size:0.67rem;font-weight:700;}
.p-fba  {background:#FFF7ED;color:#C2410C;}
.p-arch {background:#EFF6FF;color:#1D4ED8;}
.p-rb   {background:#FEF2F2;color:#B91C1C;}
.p-calc {background:#F0FDF4;color:#15803D;}
.p-na   {background:#F3F4F6;color:#6B7280;}

/* ── DIVIDER ── */
.divhr{border:none;border-top:1px solid #E8EBF0;margin:1.2rem 0;}
.section-title{font-family:'Space Grotesk',sans-serif;font-size:1.05rem;font-weight:700;color:#1E2D4E;margin:1.2rem 0 0.6rem;}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"]{
    gap:4px;background:#ffffff;border-radius:14px;padding:5px;
    border:1px solid #E8EBF0;box-shadow:0 2px 8px rgba(30,45,78,0.06);
}
.stTabs [data-baseweb="tab"]{border-radius:10px;padding:8px 22px;font-size:0.83rem;color:#8A9BB5;font-weight:600;}
.stTabs [aria-selected="true"]{background:#1E2D4E!important;color:#F47920!important;font-weight:700!important;box-shadow:0 2px 8px rgba(30,45,78,0.2)!important;}

/* ── BUTTONS ── */
div[data-testid="stButton"]>button{
    background:linear-gradient(135deg,#F47920 0%,#e06010 100%)!important;
    color:white!important;border:none!important;border-radius:12px!important;
    font-family:'Space Grotesk',sans-serif!important;font-weight:700!important;
    font-size:0.95rem!important;letter-spacing:0.02em!important;
    box-shadow:0 4px 14px rgba(244,121,32,0.35)!important;
    padding:0.6rem 1.5rem!important;
}
div[data-testid="stButton"]>button:hover{
    box-shadow:0 6px 20px rgba(244,121,32,0.5)!important;
    transform:translateY(-1px)!important;
}
div[data-testid="stDownloadButton"]>button{
    background:linear-gradient(135deg,#1E2D4E 0%,#2A3F6F 100%)!important;
    color:white!important;border:none!important;border-radius:12px!important;
    font-family:'Space Grotesk',sans-serif!important;font-weight:700!important;
    box-shadow:0 4px 14px rgba(30,45,78,0.25)!important;
}

/* ── DB STATUS ── */
.db-status{
    display:flex;align-items:center;gap:0.6rem;font-size:0.79rem;font-weight:500;
    padding:0.6rem 1.1rem;background:#ffffff;
    border:1px solid #E8EBF0;border-radius:10px;margin-bottom:1rem;
    box-shadow:0 1px 4px rgba(30,45,78,0.06);color:#1E2D4E;
}
.db-dot{width:9px;height:9px;border-radius:50%;background:#16a34a;flex-shrink:0;box-shadow:0 0 6px rgba(22,163,74,0.5);}
.db-dot.off{background:#dc2626;box-shadow:0 0 6px rgba(220,38,38,0.5);}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"]{background:#ffffff;border-radius:12px;border:1.5px dashed #D1D9E6;padding:0.5rem;}
[data-testid="stFileUploader"]:hover{border-color:#F47920;}

/* ── INPUTS ── */
[data-testid="stTextInput"] input{
    background:#ffffff!important;border:1.5px solid #E8EBF0!important;
    border-radius:10px!important;color:#1E2D4E!important;font-weight:500!important;
}
[data-testid="stTextInput"] input:focus{border-color:#F47920!important;}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"]{background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #E8EBF0;}

/* ── STREAMLIT OVERRIDES ── */
h1,h2,h3,h4{color:#1E2D4E!important;}
p{color:#4A5568;}
label{color:#1E2D4E!important;font-weight:600!important;}
.stSuccess{background:#F0FDF4!important;color:#166534!important;border:1px solid #BBF7D0!important;border-radius:10px!important;}
.stError{background:#FEF2F2!important;color:#991B1B!important;border:1px solid #FECACA!important;border-radius:10px!important;}
.stWarning{background:#FFF7ED!important;color:#92400E!important;border:1px solid #FED7AA!important;border-radius:10px!important;}
.stInfo{background:#EFF6FF!important;color:#1E40AF!important;border:1px solid #BFDBFE!important;border-radius:10px!important;}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  TOPBAR WITH LOGO
# ═══════════════════════════════════════════════════════════════════════════════
logo_html = f'<img src="data:image/jpeg;base64,{LOGO_B64}" class="topbar-logo">' if LOGO_B64 else '<div style="width:48px;height:48px;background:#F47920;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:900;color:white;font-size:1.2rem;">VV</div>'

st.markdown(f"""
<div class="topbar">
  {logo_html}
  <div class="topbar-text">
    <div class="topbar-title">VirVentures DataOps</div>
    <div class="topbar-sub">Buying Intelligence Engine</div>
  </div>
  <div class="topbar-badge">⚡ v4.0 Production</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  SUPABASE CONNECTION
# ═══════════════════════════════════════════════════════════════════════════════

SUPABASE_URL = "https://tbdrqhakplletazsjiat.supabase.co"
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")
DB_PASSWORD  = st.secrets.get("DB_PASSWORD", "")

def get_supabase():
    try:
        from supabase import create_client
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        return None

def db_connected():
    if not SUPABASE_KEY:
        return False
    sb = get_supabase()
    if sb is None:
        return False
    try:
        sb.table("fba_inventory").select("asin").limit(1).execute()
        return True
    except:
        return False

# ═══════════════════════════════════════════════════════════════════════════════
#  CORE UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

ASIN_RE = re.compile(r'^B0[A-Z0-9]{8}$')

def is_asin(v):
    return bool(ASIN_RE.match(str(v).strip().upper()))

def clean_asin(v):
    s = str(v).strip()
    if s.startswith(("b'", 'b"')) and s.endswith(("'", '"')):
        s = s[2:-1]
    return s.strip().upper()

def is_blank(v):
    return str(v).strip().lower() in ("", "n/a", "#n/a", "#value!", "nan", "none")

def safe_float(v):
    try: return float(str(v).replace(",","").strip())
    except: return 0.0

def pct(a, b): return round(a/b*100,1) if b else 0.0

def sim(a, b):
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

def smart_col(df, targets, threshold=0.55):
    cols = list(df.columns)
    for t in targets:
        for c in cols:
            if c.strip().lower() == t.strip().lower(): return c, 'exact'
    for t in targets:
        for c in cols:
            if t.lower() in c.lower() or c.lower() in t.lower(): return c, 'fuzzy'
    best_col, best_score = None, 0.0
    for t in targets:
        for c in cols:
            s = sim(c, t)
            if s > best_score: best_score, best_col = s, c
    if best_score >= threshold: return best_col, 'fuzzy'
    return None, None

def detect_asin_col(df, sample=60):
    best_col, best_score = None, 0.0
    for col in df.columns:
        vals = df[col].head(sample).astype(str).str.strip()
        vals = vals[vals.str.len() > 0]
        if len(vals) == 0: continue
        hits = vals.apply(lambda v: bool(ASIN_RE.match(clean_asin(v)))).sum()
        score = hits / len(vals)
        if score > best_score: best_score, best_col = score, col
    if best_score >= 0.5: return best_col, round(best_score*100,1)
    return None, 0.0

def get_src_val(row_dict, *aliases):
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
    if f is None: return pd.DataFrame()
    try:
        f.seek(0)
        if f.name.lower().endswith(".csv"):
            return pd.read_csv(f, dtype=str).fillna("")
        return pd.read_excel(f, dtype=str).fillna("")
    except Exception as e:
        st.error(f"Cannot read {f.name}: {e}")
        return pd.DataFrame()

def read_archive_dual(f):
    if f is None: return {}, {}
    try:
        f.seek(0)
        raw = pd.read_excel(f, header=None, dtype=str).fillna("")
        header_row = raw.iloc[0].tolist()
        asin_col_indices = [i for i, v in enumerate(header_row) if "asin" in str(v).lower()]

        if not asin_col_indices:
            f.seek(0)
            df = pd.read_excel(f, dtype=str).fillna("")
            asin_col, _ = detect_asin_col(df)
            if not asin_col: return {}, {}
            m = {}
            for _, r in df.iterrows():
                k = clean_asin(r[asin_col])
                if is_asin(k): m[k] = r.to_dict()
            return m, {}

        maps = []
        for i, start_col in enumerate(asin_col_indices):
            end_col = asin_col_indices[i+1] if i+1 < len(asin_col_indices) else len(raw.columns)
            sub = raw.iloc[:, start_col:end_col].copy()
            sub.columns = [str(v).strip() for v in sub.iloc[0]]
            sub = sub.iloc[1:].reset_index(drop=True).astype(str).fillna("")
            asin_col, _ = detect_asin_col(sub)
            if not asin_col:
                for col in sub.columns:
                    if "asin" in col.lower(): asin_col = col; break
            table_map = {}
            if asin_col:
                for _, r in sub.iterrows():
                    k = clean_asin(r[asin_col])
                    if is_asin(k) and k not in table_map:
                        table_map[k] = r.to_dict()
            maps.append(table_map)

        return maps[0] if len(maps) > 0 else {}, maps[1] if len(maps) > 1 else {}
    except Exception as e:
        st.error(f"Archive parse error: {e}")
        return {}, {}

def build_fba_map(df):
    asin_col, asin_pct = detect_asin_col(df)
    if not asin_col: asin_col, _ = smart_col(df, ["asin","ASIN"])
    result = {}
    if asin_col:
        for _, r in df.iterrows():
            k = clean_asin(r[asin_col])
            if is_asin(k): result[k] = r.to_dict()
    return result, asin_col, asin_pct

# ═══════════════════════════════════════════════════════════════════════════════
#  SUPABASE DB OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def upload_to_supabase(fba_map, arch_left, arch_right, restricted_set):
    """Push source data to Supabase tables."""
    sb = get_supabase()
    if not sb:
        st.error("Supabase not connected. Check your secrets.")
        return False
    try:
        # FBA inventory
        fba_rows = [{"asin": k, "data": v} for k, v in list(fba_map.items())[:5000]]
        sb.table("fba_inventory").delete().neq("asin","__none__").execute()
        for i in range(0, len(fba_rows), 500):
            sb.table("fba_inventory").insert(fba_rows[i:i+500]).execute()

        # Archive left
        arch_l_rows = [{"asin": k, "side": "A-Z", "data": v} for k, v in list(arch_left.items())[:5000]]
        arch_r_rows = [{"asin": k, "side": "Z-A", "data": v} for k, v in list(arch_right.items())[:5000]]
        sb.table("archive_inventory").delete().neq("asin","__none__").execute()
        all_arch = arch_l_rows + arch_r_rows
        for i in range(0, len(all_arch), 500):
            sb.table("archive_inventory").insert(all_arch[i:i+500]).execute()

        # Restricted brands
        rb_rows = [{"brand": b} for b in list(restricted_set)[:2000]]
        sb.table("restricted_brands").delete().neq("brand","__none__").execute()
        for i in range(0, len(rb_rows), 500):
            sb.table("restricted_brands").insert(rb_rows[i:i+500]).execute()

        return True
    except Exception as e:
        st.error(f"Upload error: {e}")
        return False

def fetch_from_supabase(asins):
    """Fetch source data for a list of ASINs from Supabase."""
    sb = get_supabase()
    if not sb: return {}, {}, {}, set()
    try:
        asin_list = list(set(asins))

        # FBA
        fba_resp = sb.table("fba_inventory").select("asin,data").in_("asin", asin_list).execute()
        fba_map  = {r["asin"]: r["data"] for r in (fba_resp.data or [])}

        # Archive
        arch_resp = sb.table("archive_inventory").select("asin,side,data").in_("asin", asin_list).execute()
        arch_left, arch_right = {}, {}
        for r in (arch_resp.data or []):
            if r["side"] == "A-Z": arch_left[r["asin"]]  = r["data"]
            else:                   arch_right[r["asin"]] = r["data"]

        # Restricted
        rb_resp = sb.table("restricted_brands").select("brand").execute()
        restricted_set = set(r["brand"].lower().strip() for r in (rb_resp.data or []))

        return fba_map, arch_left, arch_right, restricted_set
    except Exception as e:
        st.error(f"Fetch error: {e}")
        return {}, {}, {}, set()

# ═══════════════════════════════════════════════════════════════════════════════
#  EXACT COLUMN FILL ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

TARGET_COLS = [
    "UPC","Output ASIN","INV(A-Z)","INV(Z-A)","Listing Status",
    "Restricted","SKU Status(A-Z)","SKU Status(Z-A)","Ageing","Return",
    "FBM-LIFETIME","FBM-LAST YEAR","FBM-CURRENT YEAR",
    "Net Ordered GMS($)","Net Ordered Units",
    "Lifetime","Sales 2025","Current year",
    "Sales 30","Sales 3","Sales 1",
    "Stock","Reserve","Inbound",
    "TOTAL(Stock+Reserve+inbound)","Days of stock(30)","Days of stock(3)","Brand"
]

NO_RECORDS_COLS = [
    "Ageing","Return","FBM-LIFETIME","FBM-LAST YEAR","FBM-CURRENT YEAR",
    "Net Ordered GMS($)","Net Ordered Units","Lifetime","Sales 2025","Current year",
]

def fill_row(asin, fba_row, arch_l, arch_r, brand, restricted_set):
    fba    = fba_row or {}
    arch_l = arch_l or {}
    arch_r = arch_r or {}
    result = {}

    def fill(col, val, src): result[col] = (val, src)

    # INV(A-Z) — SKU from archive left
    v, k = get_src_val(arch_l, "sku(A-Z)","sku","SKU")
    fill("INV(A-Z)", v or "No Records", f"Archive(A-Z).{k}" if v else "—")

    # INV(Z-A) — SKU from archive right
    v, k = get_src_val(arch_r, "sku(Z-A)","sku","SKU")
    fill("INV(Z-A)", v or "No Records", f"Archive(Z-A).{k}" if v else "—")

    # Listing Status
    v, k = get_src_val(fba, "afn-listing-exists","mfn-listing-exists","listing")
    if v:
        normalized = "Listed" if v.lower() in ("yes","true","1","active","listed") else "Not Listed"
        fill("Listing Status", normalized, f"FBA.{k}")
    else:
        fill("Listing Status", "No Records", "—")

    # Restricted
    brand_lower = brand.strip().lower() if brand else ""
    is_r = bool(brand_lower and brand_lower in restricted_set)
    fill("Restricted", "Yes — Restricted" if is_r else "No", "Restricted Brands list")

    # SKU Status(A-Z)
    v, k = get_src_val(arch_l, "sku(A-Z)","sku","SKU")
    fill("SKU Status(A-Z)", v or "No Records", f"Archive(A-Z).{k}" if v else "—")

    # SKU Status(Z-A)
    v, k = get_src_val(arch_r, "sku(Z-A)","sku","SKU")
    fill("SKU Status(Z-A)", v or "No Records", f"Archive(Z-A).{k}" if v else "—")

    # No Records columns
    for col in NO_RECORDS_COLS:
        fill(col, "No Records", "—")

    # Sales 30 / 3 / 1
    for col, aliases in [
        ("Sales 30", ["Sales 30","sales30","30 day sales","ordered-units"]),
        ("Sales 3",  ["Sales 3","sales3","3 day sales"]),
        ("Sales 1",  ["Sales 1","sales1","1 day sales"]),
    ]:
        v, k = get_src_val(fba, *aliases)
        fill(col, v or "No Records", f"FBA.{k}" if v else "—")

    # Stock
    v, k = get_src_val(fba, "STOCK","afn-fulfillable-quantity","fulfillable")
    if not v: v, k = get_src_val(arch_l, "afn-fulfillable-quantity","STOCK")
    fill("Stock", v or "0", f"{'FBA' if fba else 'Archive'}.{k}" if v else "defaulted 0")

    # Reserve
    v, k = get_src_val(fba, "RESERVE","afn-reserved-quantity","afn-reserve")
    if not v: v, k = get_src_val(arch_l, "afn-reserved-quantity","RESERVE")
    fill("Reserve", v or "0", f"FBA.{k}" if v else "defaulted 0")

    # Inbound
    v, k = get_src_val(fba, "INBOUND","afn-inbound-working-quantity","afn-inbound-shipped-quantity","afn-inbound")
    fill("Inbound", v or "0", f"FBA.{k}" if v else "defaulted 0")

    # TOTAL
    v, k = get_src_val(fba, "afn-total-quantity","TOTAL")
    if not v: v, k = get_src_val(arch_l, "afn-total-quantity","TOTAL")
    if not v:
        try:
            calc = safe_float(result.get("Stock",("0",""))[0]) + safe_float(result.get("Reserve",("0",""))[0]) + safe_float(result.get("Inbound",("0",""))[0])
            v = str(int(calc)); k = "calculated"
        except: v = "0"
    fill("TOTAL(Stock+Reserve+inbound)", v, f"FBA.{k}" if k else "calculated")

    # Days of stock(30)
    try:
        sv  = safe_float(result.get("Stock",("0",""))[0])
        s30 = safe_float(result.get("Sales 30",("0",""))[0])
        fill("Days of stock(30)", str(round(sv/(s30/30),1)) if s30>0 else "No Records",
             "Stock÷(Sales30÷30)" if s30>0 else "Sales 30 unavailable")
    except: fill("Days of stock(30)", "No Records", "—")

    # Days of stock(3)
    try:
        sv = safe_float(result.get("Stock",("0",""))[0])
        s3 = safe_float(result.get("Sales 3",("0",""))[0])
        fill("Days of stock(3)", str(round(sv/(s3/3),1)) if s3>0 else "No Records",
             "Stock÷(Sales3÷3)" if s3>0 else "Sales 3 unavailable")
    except: fill("Days of stock(3)", "No Records", "—")

    # Brand
    fill("Brand", brand.strip() if brand and brand.strip() else "No Records", "Analysis file")

    return {col: val for col, (val, _) in result.items()}

# ═══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
if "run_result"     not in st.session_state: st.session_state.run_result     = None
if "vendor_history" not in st.session_state: st.session_state.vendor_history = []
if "db_mode"        not in st.session_state: st.session_state.db_mode        = "file"
if "source_loaded"  not in st.session_state: st.session_state.source_loaded  = False

# ═══════════════════════════════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════════════════════════════
tab_run, tab_upload, tab_dash, tab_history, tab_map = st.tabs([
    "⚡  Run Analysis", "☁️  Update Database", "📊  Dashboard", "📈  History", "📋  Column Map"
])

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB — COLUMN MAP
# ═══════════════════════════════════════════════════════════════════════════════
with tab_map:
    st.markdown('<div class="section-title">Exact Column Mapping Reference</div>', unsafe_allow_html=True)
    st.markdown("""
<table class="map-table">
<tr><th>#</th><th>Analysis Column</th><th>Source</th><th>Source Column</th><th>Logic</th></tr>
<tr><td>1</td><td>UPC</td><td><span class="pill p-na">Pass-through</span></td><td>—</td><td>Kept from analysis file</td></tr>
<tr><td>2</td><td>Output ASIN</td><td><span class="pill p-na">Pass-through</span></td><td>—</td><td>Match key — detected by pattern</td></tr>
<tr><td>3</td><td>INV(A-Z)</td><td><span class="pill p-arch">Archive Left</span></td><td>sku(A-Z)</td><td>SKU from asin(A-Z) table</td></tr>
<tr><td>4</td><td>INV(Z-A)</td><td><span class="pill p-arch">Archive Right</span></td><td>sku(Z-A)</td><td>SKU from asin(Z-A) table</td></tr>
<tr><td>5</td><td>Listing Status</td><td><span class="pill p-fba">FBA Inv</span></td><td>afn-listing-exists</td><td>Yes→Listed / No→Not Listed</td></tr>
<tr><td>6</td><td>Restricted</td><td><span class="pill p-rb">Restricted Brands</span></td><td>Brand name list</td><td>Exact match → Yes/No</td></tr>
<tr><td>7</td><td>SKU Status(A-Z)</td><td><span class="pill p-arch">Archive Left</span></td><td>sku(A-Z)</td><td>SKU from asin(A-Z) table</td></tr>
<tr><td>8</td><td>SKU Status(Z-A)</td><td><span class="pill p-arch">Archive Right</span></td><td>sku(Z-A)</td><td>SKU from asin(Z-A) table</td></tr>
<tr><td>9-18</td><td>Ageing, Return, FBM-*, Net Ordered*, Lifetime, Sales 2025, Current year</td><td><span class="pill p-na">No Records</span></td><td>—</td><td>Not available in source files</td></tr>
<tr><td>19</td><td>Sales 30</td><td><span class="pill p-fba">FBA Inv</span></td><td>Sales 30</td><td>Direct fill</td></tr>
<tr><td>20</td><td>Sales 3</td><td><span class="pill p-fba">FBA Inv</span></td><td>Sales 3</td><td>Direct fill</td></tr>
<tr><td>21</td><td>Sales 1</td><td><span class="pill p-fba">FBA Inv</span></td><td>Sales 1</td><td>Direct fill</td></tr>
<tr><td>22</td><td>Stock</td><td><span class="pill p-fba">FBA Inv</span></td><td>STOCK</td><td>FBA → Archive fallback</td></tr>
<tr><td>23</td><td>Reserve</td><td><span class="pill p-fba">FBA Inv</span></td><td>RESERVE</td><td>FBA → Archive fallback</td></tr>
<tr><td>24</td><td>Inbound</td><td><span class="pill p-fba">FBA Inv</span></td><td>INBOUND</td><td>FBA only</td></tr>
<tr><td>25</td><td>TOTAL(Stock+Reserve+inbound)</td><td><span class="pill p-fba">FBA Inv</span></td><td>afn-total-quantity</td><td>FBA → Archive → Calculated</td></tr>
<tr><td>26</td><td>Days of stock(30)</td><td><span class="pill p-calc">Calculated</span></td><td>—</td><td>Stock ÷ (Sales30 ÷ 30)</td></tr>
<tr><td>27</td><td>Days of stock(3)</td><td><span class="pill p-calc">Calculated</span></td><td>—</td><td>Stock ÷ (Sales3 ÷ 3)</td></tr>
<tr><td>28</td><td>Brand</td><td><span class="pill p-na">Pass-through</span></td><td>—</td><td>Kept from analysis file</td></tr>
</table>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB — UPDATE DATABASE (morning upload)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_upload:
    st.markdown('<div class="section-title">☁️ Update Source Database</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-sub">Do this once every morning after receiving the 3 daily files. The whole team benefits instantly.</div>', unsafe_allow_html=True)

    connected = db_connected()
    dot_cls   = "db-dot" if connected else "db-dot off"
    db_status = "Connected to Supabase — database ready" if connected else "Not connected — add SUPABASE_KEY to Streamlit Secrets"
    st.markdown(f'<div class="db-status"><div class="{dot_cls}"></div>{db_status}</div>', unsafe_allow_html=True)

    if not connected:
        st.markdown("""
        <div class="alert-box alert-amber">
        <strong>Setup required:</strong> Add your Supabase key to Streamlit Secrets.<br>
        In Streamlit Cloud → Your app → Settings → Secrets → paste:<br><br>
        <code>SUPABASE_KEY = "your-anon-public-key-here"</code><br>
        <code>DB_PASSWORD  = "VIRvenAmiVen"</code>
        </div>
        """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        up_fba  = st.file_uploader("📦 FBA Inventory",     type=["xlsx","xls","csv"], key="up_fba")
    with col2:
        up_rb   = st.file_uploader("🚫 Restricted Brands", type=["xlsx","xls","csv"], key="up_rb")
    with col3:
        up_arch = st.file_uploader("🗃️ Archive Inventory", type=["xlsx","xls","csv"], key="up_arch")

    upload_ready = all([up_fba, up_rb, up_arch])
    if st.button("☁️ Push to Database", disabled=not upload_ready, use_container_width=True, type="primary"):
        with st.spinner("Processing and uploading source files..."):
            prog2 = st.progress(0)
            fba_df2 = read_file(up_fba);   prog2.progress(15)
            rb_df2  = read_file(up_rb);    prog2.progress(25)
            fba_map2, _, _ = build_fba_map(fba_df2); prog2.progress(40)
            arch_l2, arch_r2 = read_archive_dual(up_arch); prog2.progress(60)
            rb_col2 = rb_df2.columns[0]
            rb_set2 = set(rb_df2[rb_col2].str.strip().str.lower().dropna()); prog2.progress(70)

            if connected:
                ok = upload_to_supabase(fba_map2, arch_l2, arch_r2, rb_set2)
                prog2.progress(100)
                if ok:
                    st.success(f"✅ Database updated! FBA: {len(fba_map2):,} ASINs · Archive L: {len(arch_l2):,} · Archive R: {len(arch_r2):,} · Restricted: {len(rb_set2):,} brands")
                    st.session_state.source_loaded = True
            else:
                # store in session if no DB
                st.session_state["_fba_map"]  = fba_map2
                st.session_state["_arch_left"] = arch_l2
                st.session_state["_arch_right"]= arch_r2
                st.session_state["_rb_set"]    = rb_set2
                st.session_state.source_loaded = True
                prog2.progress(100)
                st.success(f"✅ Source data loaded in memory (no DB — add Supabase key to persist). FBA: {len(fba_map2):,} · Archive: {len(arch_l2)+len(arch_r2):,} · Restricted: {len(rb_set2):,}")

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB — RUN ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_run:
    connected = db_connected()
    src_ready = connected or st.session_state.source_loaded

    # mode selector
    st.markdown('<div class="section-title">Data source mode</div>', unsafe_allow_html=True)
    mc1, mc2 = st.columns(2)
    with mc1:
        if st.button("☁️ Use Database (recommended)" if src_ready else "☁️ Database — not ready yet",
                     use_container_width=True, type="primary" if st.session_state.db_mode=="db" else "secondary"):
            st.session_state.db_mode = "db"
    with mc2:
        if st.button("📁 Upload all 4 files manually", use_container_width=True,
                     type="primary" if st.session_state.db_mode=="file" else "secondary"):
            st.session_state.db_mode = "file"

    if st.session_state.db_mode == "db" and not src_ready:
        st.markdown('<div class="alert-box alert-amber">⚠️ No source data in database yet. Go to <strong>Update Database</strong> tab first, or switch to manual file mode.</div>', unsafe_allow_html=True)

    st.markdown("<hr class='divhr'>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2, gap="large")
    with col_l:
        st.markdown('<div class="card-title">Analysis file</div><div class="card-sub">Your template with Output ASIN column</div>', unsafe_allow_html=True)
        an_file     = st.file_uploader("📊 Analysis file", type=["xlsx","xls","csv"], key="an")
        vendor_name = st.text_input("Vendor / file label", placeholder="e.g. ALLWAY, 3M, Echo Park...")

    with col_r:
        if st.session_state.db_mode == "file":
            st.markdown('<div class="card-title">Source files (manual mode)</div><div class="card-sub">Upload all 3 source files</div>', unsafe_allow_html=True)
            fba_file  = st.file_uploader("📦 FBA Inventory",     type=["xlsx","xls","csv"], key="fba")
            rb_file   = st.file_uploader("🚫 Restricted Brands", type=["xlsx","xls","csv"], key="rb")
            arch_file = st.file_uploader("🗃️ Archive Inventory", type=["xlsx","xls","csv"], key="arch")
            all_ready = all([an_file, fba_file, rb_file, arch_file])
        else:
            st.markdown('<div class="card-title">Database mode</div><div class="card-sub">Source data loaded from Supabase</div>', unsafe_allow_html=True)
            dot = "db-dot" if src_ready else "db-dot off"
            st.markdown(f'<div class="db-status"><div class="{dot}"></div>{"Source data ready — just upload your analysis file" if src_ready else "No source data yet"}</div>', unsafe_allow_html=True)
            fba_file = rb_file = arch_file = None
            all_ready = bool(an_file and src_ready)

    # pre-flight
    if an_file:
        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔬 Pre-flight check</div>', unsafe_allow_html=True)
        an_prev = read_file(an_file); an_file.seek(0)
        if not an_prev.empty:
            asin_col_p, asin_pct_p = detect_asin_col(an_prev)
            brand_col_p, _ = smart_col(an_prev, ["Brand","brand","BRAND"])
            st.markdown(f"<div class='card-sub'>{len(an_prev):,} rows · {len(an_prev.columns)} columns</div>", unsafe_allow_html=True)
            if asin_col_p:
                samples = an_prev[asin_col_p].dropna().head(3).tolist()
                st.markdown(f'<div class="alert-box alert-green">✅ ASIN column: <strong>"{asin_col_p}"</strong> ({asin_pct_p}% pattern match) · <code>{" · ".join(samples)}</code></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-box alert-red">❌ No ASIN column found. Cells must contain values like B07QNLTK2M</div>', unsafe_allow_html=True)
            if brand_col_p:
                st.markdown(f'<div class="alert-box alert-green">✅ Brand column: <strong>"{brand_col_p}"</strong></div>', unsafe_allow_html=True)

    st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
    run_btn = st.button("⚡ Run VirVentures DataOps Engine", disabled=not all_ready, use_container_width=True, type="primary")

    if run_btn and all_ready:
        t0 = time.time()
        logs = []
        def log(msg, kind="info"):
            cls = {"ok":"lok","warn":"lwarn","err":"lerr","head":"lhead"}.get(kind,"linfo")
            logs.append(f'<span class="{cls}">{msg}</span>')

        prog = st.progress(0); status = st.empty()

        # read analysis
        status.write("Reading analysis file...")
        an_df = read_file(an_file)
        if an_df.empty: st.error("Analysis file could not be read."); st.stop()
        prog.progress(10)
        log(f"◆ ANALYSIS FILE — {len(an_df):,} rows | {len(an_df.columns)} cols", "head")

        # get source data
        status.write("Loading source data...")
        an_asin_col, an_asin_pct = detect_asin_col(an_df)
        if not an_asin_col: st.error("❌ Cannot find ASIN column in analysis file."); st.stop()

        all_asins = [clean_asin(v) for v in an_df[an_asin_col] if is_asin(clean_asin(v))]

        if st.session_state.db_mode == "db" and connected:
            fba_map, arch_left, arch_right, restricted_set = fetch_from_supabase(all_asins)
            log(f"◆ SOURCE DATA FROM SUPABASE — FBA: {len(fba_map):,} | Arch: {len(arch_left)+len(arch_right):,} | Restricted: {len(restricted_set):,}", "head")
        elif st.session_state.source_loaded and "_fba_map" in st.session_state:
            fba_map      = st.session_state["_fba_map"]
            arch_left    = st.session_state["_arch_left"]
            arch_right   = st.session_state["_arch_right"]
            restricted_set = st.session_state["_rb_set"]
            log(f"◆ SOURCE DATA FROM SESSION — FBA: {len(fba_map):,} | Arch: {len(arch_left)+len(arch_right):,}", "head")
        else:
            # manual file mode
            status.write("Reading source files...")
            fba_df2 = read_file(fba_file); rb_df2 = read_file(rb_file)
            fba_map, fba_ac, fba_ap = build_fba_map(fba_df2)
            arch_left, arch_right = read_archive_dual(arch_file)
            rb_col2 = rb_df2.columns[0]
            restricted_set = set(rb_df2[rb_col2].str.strip().str.lower().dropna())
            log(f"◆ SOURCE FILES — FBA: {len(fba_map):,} | Arch L: {len(arch_left):,} | Arch R: {len(arch_right):,} | Restricted: {len(restricted_set):,}", "head")

        prog.progress(45)

        an_brand_col, _ = smart_col(an_df, ["Brand","brand","BRAND"])
        log(f"  ASIN col  → '{an_asin_col}' ({an_asin_pct}% pattern)", "ok")
        log(f"  Brand col → {an_brand_col or '⚠ not found'}", "ok" if an_brand_col else "warn")
        prog.progress(52)

        # process
        status.write("Processing all rows...")
        out_rows  = []
        anomalies = []
        fba_hits = arch_hits = restricted_count = filled_cells = no_match = 0
        n = len(an_df)

        for idx, row in an_df.iterrows():
            asin  = clean_asin(row[an_asin_col])
            brand = str(row.get(an_brand_col,"")).strip() if an_brand_col else ""

            if not is_asin(asin):
                nr = row.to_dict()
                for col in TARGET_COLS:
                    if col not in nr: nr[col] = "No Records"
                out_rows.append(nr); continue

            fba_row   = fba_map.get(asin)
            arch_l_row = arch_left.get(asin)
            arch_r_row = arch_right.get(asin)

            if fba_row:                         fba_hits  += 1
            if arch_l_row or arch_r_row:        arch_hits += 1
            if not any([fba_row, arch_l_row, arch_r_row]): no_match += 1

            filled = fill_row(asin, fba_row, arch_l_row, arch_r_row, brand, restricted_set)
            filled_cells += sum(1 for v in filled.values() if v not in ("No Records","0","—"))

            if filled.get("Restricted","").startswith("Yes"): restricted_count += 1

            nr = row.to_dict()
            nr["UPC"]         = str(row.get("UPC","")).strip()
            nr["Output ASIN"] = asin
            nr["Brand"]       = brand
            nr.update(filled)

            # anomalies
            sv   = safe_float(nr.get("Stock",0))
            s30  = safe_float(nr.get("Sales 30",0))
            dos  = safe_float(nr.get("Days of stock(30)",999) if nr.get("Days of stock(30)","") not in ("No Records","") else 999)
            is_r = nr.get("Restricted","").startswith("Yes")
            lst  = str(nr.get("Listing Status","")).lower()

            if sv == 0 and s30 > 5:
                anomalies.append({"type":"🔴 Zero stock / high velocity","severity":"red","asin":asin,"brand":brand,"detail":f"0 stock | {s30:.0f} sold last 30d"})
            elif 0 < dos < 7:
                anomalies.append({"type":"🔴 Critical — under 7 days","severity":"red","asin":asin,"brand":brand,"detail":f"{dos} days remaining"})
            elif 7 <= dos < 14:
                anomalies.append({"type":"🟡 Low stock","severity":"amber","asin":asin,"brand":brand,"detail":f"{dos} days remaining"})
            if is_r and "listed" in lst:
                anomalies.append({"type":"🚫 Restricted + Active listing","severity":"red","asin":asin,"brand":brand,"detail":f"'{brand}' restricted but active"})

            out_rows.append(nr)
            if idx % max(1, n//30) == 0:
                prog.progress(52 + int(40*idx/n))

        prog.progress(94)
        out_df = pd.DataFrame(out_rows)
        for col in TARGET_COLS:
            if col not in out_df.columns: out_df[col] = "No Records"
        extra = [c for c in out_df.columns if c not in TARGET_COLS]
        out_df = out_df[TARGET_COLS + extra]

        # write
        status.write("Writing output...")
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            out_df.to_excel(writer, index=False, sheet_name="Analysis_Filled")
            if anomalies:
                pd.DataFrame(anomalies)[["type","asin","brand","detail"]].to_excel(writer, index=False, sheet_name="Anomaly_Alerts")
            audit = []
            for i, r2 in enumerate(out_rows[:300]):
                for col in TARGET_COLS:
                    audit.append({"Row":i+2,"ASIN":r2.get("Output ASIN",""),"Column":col,"Value":r2.get(col,"")})
            pd.DataFrame(audit).to_excel(writer, index=False, sheet_name="Audit_Trail")
        buf.seek(0); prog.progress(100); t1 = time.time()
        status.empty(); prog.empty()

        match_rate = pct(fba_hits, n)
        log(f"◆ COMPLETE — {round(t1-t0,2)}s", "head")
        log(f"  Rows : {n:,} | FBA: {fba_hits:,} ({match_rate}%) | Archive: {arch_hits:,} | Unmatched: {no_match:,}", "ok")
        log(f"  Cells filled: {filled_cells:,} | Restricted: {restricted_count:,} | Anomalies: {len(anomalies):,}", "ok" if not anomalies else "warn")

        st.session_state.run_result = {
            "out_df":out_df,"buf":buf.getvalue(),"n":n,
            "fba_hits":fba_hits,"arch_hits":arch_hits,"filled_cells":filled_cells,
            "restricted_count":restricted_count,"no_match":no_match,
            "anomalies":anomalies,"match_rate":match_rate,"logs":logs,
            "elapsed":round(t1-t0,2),"vendor":vendor_name or "Unknown","run_date":str(date.today()),
        }
        if vendor_name:
            st.session_state.vendor_history.append({
                "vendor":vendor_name,"date":str(date.today()),"rows":n,
                "match_rate":match_rate,"filled":filled_cells,
                "restricted":restricted_count,"anomalies":len(anomalies),"unmatched":no_match
            })

    # results
    if st.session_state.run_result:
        r = st.session_state.run_result
        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Run Report</div>', unsafe_allow_html=True)
        match_color = "green" if r['match_rate']>=80 else "amber" if r['match_rate']>=50 else "red"
        st.markdown(f"""
        <div class="metric-row">
          <div class="metric-box orange"><div class="m-val orange">{r['n']:,}</div><div class="m-lbl">Rows Processed</div></div>
          <div class="metric-box navy"><div class="m-val navy">{r['fba_hits']:,}</div><div class="m-lbl">FBA Matched ({r['match_rate']}%)</div></div>
          <div class="metric-box green"><div class="m-val green">{r['filled_cells']:,}</div><div class="m-lbl">Cells Filled</div></div>
          <div class="metric-box {'red' if r['no_match'] else 'green'}"><div class="m-val {'red' if r['no_match'] else 'green'}">{r['no_match']:,}</div><div class="m-lbl">Unmatched ASINs</div></div>
        </div>
        <div style="font-size:0.7rem;color:#F47920;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin:0.8rem 0 0.2rem">Match Accuracy — {r['match_rate']}%</div>
        <div class="prog-wrap"><div class="prog-fill" style="width:{r['match_rate']}%"></div></div>
        """, unsafe_allow_html=True)

        st.markdown(f'<div class="log-box">{"<br>".join(r["logs"])}</div>', unsafe_allow_html=True)

        if r['anomalies']:
            st.markdown(f'<div class="section-title">⚠️ Anomaly Alerts — {len(r["anomalies"])} found</div>', unsafe_allow_html=True)
            for a in r['anomalies'][:20]:
                cls = "alert-red" if a['severity']=="red" else "alert-amber"
                st.markdown(f'<div class="alert-box {cls}"><strong>{a["type"]}</strong> &nbsp;|&nbsp; <code>{a["asin"]}</code> &nbsp;|&nbsp; {a["brand"]} &nbsp;|&nbsp; {a["detail"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-box alert-green">✅ No anomalies — all ASINs healthy</div>', unsafe_allow_html=True)

        fname = f"VirVentures_Analysis_{date.today()}.xlsx"
        st.download_button(
            label=f"⬇️  Download {fname}  (Analysis + Anomalies + Audit Trail)",
            data=r['buf'], file_name=fname,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True, type="primary"
        )

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
with tab_dash:
    if not st.session_state.run_result:
        st.markdown('<div class="alert-box alert-blue" style="margin-top:1rem">Run the engine first to see your dashboard.</div>', unsafe_allow_html=True)
    else:
        r = st.session_state.run_result; out_df = r['out_df']
        st.markdown(f'<div class="section-title">📊 Dashboard — {r["vendor"]}</div>', unsafe_allow_html=True)
        st.markdown(f"<div class='card-sub'>{r['run_date']} &nbsp;|&nbsp; {r['elapsed']}s &nbsp;|&nbsp; {r['n']:,} rows</div>", unsafe_allow_html=True)

        st.markdown("#### 🔻 Top 10 Lowest Stock ASINs")
        if "Stock" in out_df.columns:
            tmp = out_df[out_df["Stock"].apply(lambda v: str(v) not in ("No Records",""))].copy()
            tmp["_s"] = tmp["Stock"].apply(safe_float)
            show = [c for c in ["Output ASIN","Brand","Stock","Days of stock(30)","Sales 30","Listing Status"] if c in tmp.columns]
            st.dataframe(tmp.nsmallest(10,"_s")[show], use_container_width=True, hide_index=True)

        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown("#### 🚫 Restricted Brand Breakdown")
        if "Restricted" in out_df.columns and "Brand" in out_df.columns:
            restr = out_df[out_df["Restricted"].str.startswith("Yes",na=False)]
            if not restr.empty:
                counts = restr["Brand"].value_counts().reset_index(); counts.columns=["Brand","Count"]
                st.dataframe(counts, use_container_width=True, hide_index=True)
                st.markdown(f'<div class="alert-box alert-red">🚫 {len(restr)} restricted ASINs across {counts["Brand"].nunique()} brands</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-box alert-green">✅ No restricted brands</div>', unsafe_allow_html=True)

        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        if r['anomalies']:
            adf = pd.DataFrame(r['anomalies'])[["type","asin","brand","detail"]]
            adf.columns=["Alert","ASIN","Brand","Detail"]
            st.dataframe(adf, use_container_width=True, hide_index=True)
        mr=r['match_rate']; color="#F47920" if mr>=80 else "#fbbf24" if mr>=50 else "#ef4444"
        st.markdown(f'<div style="text-align:center;padding:1.5rem;"><div style="font-family:Space Grotesk,sans-serif;font-size:4rem;font-weight:800;color:{color}">{mr}%</div><div style="color:#3a4060;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.1em;margin-top:0.5rem">FBA Match Rate &nbsp;|&nbsp; {r["fba_hits"]:,} of {r["n"]:,}</div><div class="prog-wrap" style="max-width:400px;margin:1rem auto"><div class="prog-fill" style="width:{mr}%"></div></div></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB — HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
with tab_history:
    st.markdown('<div class="section-title">📈 Vendor Run History</div>', unsafe_allow_html=True)
    history = st.session_state.vendor_history
    if not history:
        st.markdown('<div class="alert-box alert-blue" style="margin-top:1rem">No history yet. Enter a vendor name before running to start tracking.</div>', unsafe_allow_html=True)
    else:
        hist_df = pd.DataFrame(history)
        hist_df.columns = ["Vendor","Date","Rows","Match Rate (%)","Cells Filled","Restricted","Anomalies","Unmatched"]
        st.dataframe(hist_df, use_container_width=True, hide_index=True)
        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown("#### Per-vendor summary")
        summary = hist_df.groupby("Vendor").agg({"Rows":"sum","Match Rate (%)":"mean","Cells Filled":"sum","Restricted":"sum","Anomalies":"sum","Unmatched":"sum"}).round(1).reset_index()
        st.dataframe(summary, use_container_width=True, hide_index=True)
        if st.button("🗑 Clear history"): st.session_state.vendor_history=[]; st.rerun()
