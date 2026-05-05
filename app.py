"""
VirVentures DataOps — Buying Intelligence Engine v5
- 3 required + up to 3 optional source files
- Output = exact same file as input, only target columns filled
- Smart column detection across all source files
- Supabase-backed persistent storage
- Pattern-based ASIN detection
- Dual-table archive parsing
- Full anomaly detection + audit trail
"""

import streamlit as st
import pandas as pd
import io, re, time, base64
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

st.set_page_config(
    page_title="VirVentures DataOps",
    page_icon="🛒", layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════════════════════
#  STYLES
# ═══════════════════════════════════════════════════════════════════════════════
def get_logo_b64():
    try:
        p = Path(__file__).parent / "virventures_com_logo.jpg"
        if p.exists(): return base64.b64encode(p.read_bytes()).decode()
    except: pass
    return None

LOGO_B64 = get_logo_b64()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:#F5F6FA;color:#1E2D4E;}
.block-container{padding-top:0!important;padding-left:1rem!important;padding-right:1rem!important;max-width:1400px;}
section[data-testid="stSidebar"]{display:none;}
#MainMenu{visibility:hidden!important;}
header[data-testid="stHeader"]{height:0!important;min-height:0!important;visibility:hidden!important;}
footer{visibility:hidden!important;}
[data-testid="stToolbar"]{display:none!important;}
div[data-testid="stDecoration"]{display:none!important;}

.topbar{background:linear-gradient(135deg,#1E2D4E 0%,#2A3F6F 100%);border-bottom:3px solid #F47920;padding:1rem 2.5rem;display:flex;align-items:center;gap:1.4rem;box-shadow:0 4px 24px rgba(30,45,78,0.15);}
.topbar-logo{height:52px;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.3);}
.topbar-title{font-family:'Space Grotesk',sans-serif;font-size:1.4rem;font-weight:800;color:#ffffff;letter-spacing:0.01em;margin:0;}
.topbar-sub{font-size:0.7rem;color:#F47920;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;margin:2px 0 0;}
.topbar-badge{margin-left:auto;background:#F47920;color:white;border-radius:20px;padding:5px 16px;font-size:0.7rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;box-shadow:0 2px 8px rgba(244,121,32,0.4);}

.section-title{font-family:'Space Grotesk',sans-serif;font-size:1.05rem;font-weight:700;color:#1E2D4E;margin:1.2rem 0 0.5rem;}
.card-title{font-family:'Space Grotesk',sans-serif;font-size:0.9rem;font-weight:700;color:#F47920;margin-bottom:0.15rem;}
.card-sub{font-size:0.68rem;color:#8A9BB5;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.8rem;}

.metric-row{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:1.2rem 0;}
.metric-box{background:#fff;border:1px solid #E8EBF0;border-radius:14px;padding:1.1rem;text-align:center;box-shadow:0 2px 10px rgba(30,45,78,0.06);border-top:3px solid #E8EBF0;transition:transform 0.15s;}
.metric-box:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(30,45,78,0.1);}
.metric-box.orange{border-top-color:#F47920;}.metric-box.navy{border-top-color:#1E2D4E;}
.metric-box.green{border-top-color:#16a34a;}.metric-box.red{border-top-color:#dc2626;}.metric-box.blue{border-top-color:#2563eb;}
.m-val{font-family:'Space Grotesk',sans-serif;font-size:1.8rem;font-weight:800;line-height:1;}
.m-val.orange{color:#F47920;}.m-val.navy{color:#1E2D4E;}.m-val.green{color:#16a34a;}.m-val.red{color:#dc2626;}.m-val.blue{color:#2563eb;}
.m-lbl{font-size:0.63rem;color:#8A9BB5;margin-top:5px;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;}

.log-box{background:#1E2D4E;border:none;border-radius:14px;padding:1.1rem 1.4rem;font-family:'Courier New',monospace;font-size:0.76rem;line-height:1.9;max-height:280px;overflow-y:auto;margin:0.8rem 0;box-shadow:0 4px 16px rgba(30,45,78,0.15);}
.lok{color:#4ade80;}.lwarn{color:#fb923c;}.lerr{color:#f87171;}.lhead{color:#F47920;font-weight:700;}.linfo{color:#6b7fa3;}

.prog-wrap{background:#E8EBF0;border-radius:8px;height:6px;margin:0.5rem 0;overflow:hidden;}
.prog-fill{height:100%;border-radius:8px;background:linear-gradient(90deg,#F47920,#ffb347);}

.alert-box{border-radius:12px;padding:0.9rem 1.2rem;margin:0.4rem 0;font-size:0.82rem;font-weight:500;}
.alert-red{background:#FEF2F2;border:1px solid #FECACA;color:#991B1B;}
.alert-amber{background:#FFF7ED;border:1px solid #FED7AA;color:#92400E;}
.alert-green{background:#F0FDF4;border:1px solid #BBF7D0;color:#166534;}
.alert-blue{background:#EFF6FF;border:1px solid #BFDBFE;color:#1E40AF;}
.alert-orange{background:#FFF7ED;border:1px solid #F47920;color:#9A3412;}

.file-card{background:#fff;border:1.5px dashed #D1D9E6;border-radius:14px;padding:1.1rem 1.2rem;margin-bottom:0.7rem;transition:border-color 0.2s;}
.file-card:hover{border-color:#F47920;}
.file-card.optional{border-style:dashed;opacity:0.85;}
.file-badge{display:inline-block;padding:2px 10px;border-radius:20px;font-size:0.65rem;font-weight:700;margin-bottom:0.4rem;}
.badge-required{background:#FFF7ED;color:#C2410C;border:1px solid #FED7AA;}
.badge-optional{background:#EFF6FF;color:#1D4ED8;border:1px solid #BFDBFE;}

.map-table{width:100%;border-collapse:collapse;font-size:0.78rem;}
.map-table th{background:#F8F9FC;color:#8A9BB5;font-weight:700;padding:9px 14px;text-align:left;letter-spacing:0.07em;font-size:0.66rem;text-transform:uppercase;border-bottom:2px solid #E8EBF0;}
.map-table td{padding:7px 14px;border-bottom:1px solid #F0F2F7;color:#4A5568;}
.map-table td:first-child{color:#1E2D4E;font-weight:600;}
.map-table tr:hover td{background:#F8F9FC;}
.pill{display:inline-block;padding:2px 9px;border-radius:20px;font-size:0.66rem;font-weight:700;}
.p-fba{background:#FFF7ED;color:#C2410C;}.p-arch{background:#EFF6FF;color:#1D4ED8;}
.p-rb{background:#FEF2F2;color:#B91C1C;}.p-calc{background:#F0FDF4;color:#15803D;}
.p-opt{background:#F5F3FF;color:#6D28D9;}.p-na{background:#F3F4F6;color:#6B7280;}

.divhr{border:none;border-top:1px solid #E8EBF0;margin:1rem 0;}
.db-status{display:flex;align-items:center;gap:0.6rem;font-size:0.79rem;font-weight:500;padding:0.6rem 1.1rem;background:#fff;border:1px solid #E8EBF0;border-radius:10px;margin-bottom:1rem;box-shadow:0 1px 4px rgba(30,45,78,0.06);color:#1E2D4E;}
.db-dot{width:9px;height:9px;border-radius:50%;flex-shrink:0;}
.db-dot.on{background:#16a34a;box-shadow:0 0 6px rgba(22,163,74,0.5);}
.db-dot.off{background:#dc2626;box-shadow:0 0 6px rgba(220,38,38,0.5);}

.stTabs [data-baseweb="tab-list"]{gap:4px;background:#fff;border-radius:14px;padding:5px;border:1px solid #E8EBF0;box-shadow:0 2px 8px rgba(30,45,78,0.06);}
.stTabs [data-baseweb="tab"]{border-radius:10px;padding:8px 22px;font-size:0.82rem;color:#8A9BB5;font-weight:600;}
.stTabs [aria-selected="true"]{background:#1E2D4E!important;color:#F47920!important;font-weight:700!important;box-shadow:0 2px 8px rgba(30,45,78,0.2)!important;}

div[data-testid="stButton"]>button{background:linear-gradient(135deg,#F47920,#e06010)!important;color:white!important;border:none!important;border-radius:12px!important;font-family:'Space Grotesk',sans-serif!important;font-weight:700!important;font-size:0.95rem!important;box-shadow:0 4px 14px rgba(244,121,32,0.3)!important;transition:all 0.2s!important;}
div[data-testid="stButton"]>button:hover{box-shadow:0 6px 20px rgba(244,121,32,0.5)!important;transform:translateY(-1px)!important;}
div[data-testid="stDownloadButton"]>button{background:linear-gradient(135deg,#1E2D4E,#2A3F6F)!important;color:white!important;border:none!important;border-radius:12px!important;font-family:'Space Grotesk',sans-serif!important;font-weight:700!important;box-shadow:0 4px 14px rgba(30,45,78,0.2)!important;}

[data-testid="stFileUploader"]{background:#fff;border-radius:12px;}
[data-testid="stTextInput"] input{background:#fff!important;border:1.5px solid #E8EBF0!important;border-radius:10px!important;color:#1E2D4E!important;font-weight:500!important;}
[data-testid="stTextInput"] input:focus{border-color:#F47920!important;}
[data-testid="stDataFrame"]{background:#fff;border-radius:12px;overflow:hidden;border:1px solid #E8EBF0;}
h1,h2,h3,h4{color:#1E2D4E!important;}
.stSuccess{background:#F0FDF4!important;color:#166534!important;border:1px solid #BBF7D0!important;border-radius:10px!important;}
.stError{background:#FEF2F2!important;color:#991B1B!important;border:1px solid #FECACA!important;border-radius:10px!important;}
.stInfo{background:#EFF6FF!important;color:#1E40AF!important;border:1px solid #BFDBFE!important;border-radius:10px!important;}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  TOPBAR
# ═══════════════════════════════════════════════════════════════════════════════
logo_html = f'<img src="data:image/jpeg;base64,{LOGO_B64}" class="topbar-logo">' if LOGO_B64 else \
    '<div style="width:52px;height:52px;background:#F47920;border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:900;color:white;font-size:1.3rem;">VV</div>'

st.markdown(f"""
<div class="topbar">
  {logo_html}
  <div>
    <div class="topbar-title">VirVentures DataOps</div>
    <div class="topbar-sub">Buying Intelligence Engine</div>
  </div>
  <div class="topbar-badge">⚡ v5.0 Production</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# Exact target columns to fill in analysis file (in order)
TARGET_COLS = [
    "INV(A-Z)", "INV(Z-A)", "Listing Status", "Restricted",
    "SKU Status(A-Z)", "SKU Status(Z-A)", "Ageing", "Return",
    "FBM-LIFETIME", "FBM-LAST YEAR", "FBM-CURRENT YEAR",
    "Net Ordered GMS($)", "Net Ordered Units",
    "Lifetime", "Sales 2023", "Current year",
    "Sales 30", "Sales 3", "Sales 1",
    "Stock", "Reserve", "Inbound",
    "TOTAL(Stock+Reserve+inbound)", "Days of stock(30)", "Days of stock(3)"
]

# Columns that map from optional files (smart detection keywords)
OPTIONAL_COL_KEYWORDS = {
    "Lifetime":           ["lifetime","life time","lifetime sales","total lifetime"],
    "FBM-LIFETIME":       ["fbm lifetime","fbm-lifetime","fbm life"],
    "FBM-LAST YEAR":      ["fbm last year","fbm-last year","fbm ly"],
    "FBM-CURRENT YEAR":   ["fbm current","fbm-current","fbm cy"],
    "Sales 2023":         ["sales 2023","2023 sales","ordered units 2023"],
    "Current year":       ["current year","cy sales","current yr","sales cy"],
    "Ageing":             ["ageing","aging","age","days aged"],
    "Return":             ["return","returns","return rate","returned"],
    "Net Ordered GMS($)": ["net ordered gms","gms","ordered gms","net gms"],
    "Net Ordered Units":  ["net ordered units","ordered units","net units"],
}

SUPABASE_URL = "https://tbdrqhakplletazsjiat.supabase.co"
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

# ═══════════════════════════════════════════════════════════════════════════════
#  CORE UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════
ASIN_RE = re.compile(r'^B0[A-Z0-9]{8}$')

def is_asin(v):    return bool(ASIN_RE.match(str(v).strip().upper()))
def clean_asin(v):
    s = str(v).strip()
    if s.startswith(("b'","b\"")) and s.endswith(("'",'"')): s=s[2:-1]
    return s.strip().upper()
def is_blank(v):   return str(v).strip().lower() in ("","n/a","#n/a","#value!","nan","none")
def safe_float(v):
    try: return float(str(v).replace(",","").strip())
    except: return 0.0
def pct(a,b):      return round(a/b*100,1) if b else 0.0
def sim(a,b):      return SequenceMatcher(None,a.lower().strip(),b.lower().strip()).ratio()

def smart_col(df, targets, threshold=0.52):
    cols = list(df.columns)
    for t in targets:
        for c in cols:
            if c.strip().lower()==t.strip().lower(): return c,'exact'
    for t in targets:
        for c in cols:
            if t.lower() in c.lower() or c.lower() in t.lower(): return c,'fuzzy'
    best_col,best_score=None,0.0
    for t in targets:
        for c in cols:
            s=sim(c,t)
            if s>best_score: best_score,best_col=s,c
    if best_score>=threshold: return best_col,'fuzzy'
    return None,None

def detect_asin_col(df, sample=60):
    best_col,best_score=None,0.0
    for col in df.columns:
        vals=df[col].head(sample).astype(str).str.strip()
        vals=vals[vals.str.len()>0]
        if not len(vals): continue
        hits=vals.apply(lambda v: bool(ASIN_RE.match(clean_asin(v)))).sum()
        score=hits/len(vals)
        if score>best_score: best_score,best_col=score,col
    return (best_col,round(best_score*100,1)) if best_score>=0.5 else (None,0.0)

def get_src_val(row_dict, *aliases):
    for alias in aliases:
        for k,v in row_dict.items():
            if str(k).strip().lower()==alias.strip().lower():
                c=str(v).strip()
                if c and c.lower() not in ("","nan","none"): return c,k
    return None,None

# ═══════════════════════════════════════════════════════════════════════════════
#  FILE READERS
# ═══════════════════════════════════════════════════════════════════════════════
def read_file(f):
    if f is None: return pd.DataFrame()
    try:
        f.seek(0)
        return pd.read_csv(f,dtype=str).fillna("") if f.name.lower().endswith(".csv") \
               else pd.read_excel(f,dtype=str).fillna("")
    except Exception as e:
        st.error(f"Cannot read {f.name}: {e}"); return pd.DataFrame()

def read_archive_dual(f):
    if f is None: return {},{}
    try:
        f.seek(0)
        raw=pd.read_excel(f,header=None,dtype=str).fillna("")
        header_row=raw.iloc[0].tolist()
        asin_cols=[i for i,v in enumerate(header_row) if "asin" in str(v).lower()]
        if not asin_cols:
            f.seek(0); df=pd.read_excel(f,dtype=str).fillna("")
            ac,_=detect_asin_col(df)
            if not ac: return {},{}
            m={}
            for _,r in df.iterrows():
                k=clean_asin(r[ac])
                if is_asin(k): m[k]=r.to_dict()
            return m,{}
        maps=[]
        for i,sc in enumerate(asin_cols):
            ec=asin_cols[i+1] if i+1<len(asin_cols) else len(raw.columns)
            sub=raw.iloc[:,sc:ec].copy()
            sub.columns=[str(v).strip() for v in sub.iloc[0]]
            sub=sub.iloc[1:].reset_index(drop=True).astype(str).fillna("")
            ac,_=detect_asin_col(sub)
            if not ac:
                for col in sub.columns:
                    if "asin" in col.lower(): ac=col; break
            tm={}
            if ac:
                for _,r in sub.iterrows():
                    k=clean_asin(r[ac])
                    if is_asin(k) and k not in tm: tm[k]=r.to_dict()
            maps.append(tm)
        return (maps[0] if maps else {}),(maps[1] if len(maps)>1 else {})
    except Exception as e:
        st.error(f"Archive parse error: {e}"); return {},{}

def build_fba_map(df):
    ac,ap=detect_asin_col(df)
    if not ac: ac,_=smart_col(df,["asin","ASIN"])
    m={}
    if ac:
        for _,r in df.iterrows():
            k=clean_asin(r[ac])
            if is_asin(k): m[k]=r.to_dict()
    return m,ac,ap

def build_generic_map(df):
    """Build ASIN map from any file — pattern-based detection."""
    ac,ap=detect_asin_col(df)
    if not ac: return {},None
    m={}
    for _,r in df.iterrows():
        k=clean_asin(r[ac])
        if is_asin(k) and k not in m: m[k]=r.to_dict()
    return m,ac

def smart_map_optional_cols(source_row, target_cols_needed):
    """
    Given a source row dict, try to find values for each target column
    using keyword matching. Returns {target_col: value}.
    """
    result={}
    for target_col in target_cols_needed:
        if target_col not in OPTIONAL_COL_KEYWORDS: continue
        keywords=OPTIONAL_COL_KEYWORDS[target_col]
        for src_key,src_val in source_row.items():
            src_key_lower=str(src_key).lower().strip()
            for kw in keywords:
                if kw in src_key_lower or src_key_lower in kw:
                    v=str(src_val).strip()
                    if v and v.lower() not in ("","nan","none"):
                        result[target_col]=v
                        break
            if target_col in result: break
    return result

# ═══════════════════════════════════════════════════════════════════════════════
#  SUPABASE
# ═══════════════════════════════════════════════════════════════════════════════
def get_sb():
    try:
        from supabase import create_client
        return create_client(SUPABASE_URL,SUPABASE_KEY) if SUPABASE_KEY else None
    except: return None

def db_connected():
    sb=get_sb()
    if not sb: return False
    try: sb.table("fba_inventory").select("asin").limit(1).execute(); return True
    except: return False

def push_to_db(fba_map,arch_left,arch_right,rb_set,optional_maps):
    sb=get_sb()
    if not sb: return False,""
    try:
        def upsert_chunks(table,rows,pk="asin"):
            sb.table(table).delete().neq(pk,"__x__").execute()
            for i in range(0,len(rows),500):
                sb.table(table).insert(rows[i:i+500]).execute()

        upsert_chunks("fba_inventory",[{"asin":k,"data":v} for k,v in list(fba_map.items())[:8000]])
        arch_rows=[{"asin":k,"side":"A-Z","data":v} for k,v in list(arch_left.items())[:8000]] + \
                  [{"asin":k,"side":"Z-A","data":v} for k,v in list(arch_right.items())[:8000]]
        upsert_chunks("archive_inventory",arch_rows)
        upsert_chunks("restricted_brands",[{"brand":b} for b in list(rb_set)[:3000]],"brand")

        # optional files stored as generic_sources
        if optional_maps:
            opt_rows=[]
            for label,omap in optional_maps.items():
                for asin,row in list(omap.items())[:5000]:
                    opt_rows.append({"asin":asin,"source_label":label,"data":row})
            if opt_rows:
                sb.table("optional_sources").delete().neq("asin","__x__").execute()
                for i in range(0,len(opt_rows),500):
                    sb.table("optional_sources").insert(opt_rows[i:i+500]).execute()
        return True,""
    except Exception as e: return False,str(e)

def fetch_from_db(asins):
    sb=get_sb()
    if not sb: return {},{},{},set(),{}
    try:
        al=list(set(asins))
        fba_r=sb.table("fba_inventory").select("asin,data").in_("asin",al).execute()
        fba_map={r["asin"]:r["data"] for r in (fba_r.data or [])}
        arch_r=sb.table("archive_inventory").select("asin,side,data").in_("asin",al).execute()
        arch_l,arch_rr={},{}
        for r in (arch_r.data or []):
            if r["side"]=="A-Z": arch_l[r["asin"]]=r["data"]
            else:                arch_rr[r["asin"]]=r["data"]
        rb_r=sb.table("restricted_brands").select("brand").execute()
        rb_set=set(r["brand"].lower().strip() for r in (rb_r.data or []))
        try:
            opt_r=sb.table("optional_sources").select("asin,source_label,data").in_("asin",al).execute()
            opt_maps={}
            for r in (opt_r.data or []):
                opt_maps.setdefault(r["source_label"],{})[r["asin"]]=r["data"]
        except: opt_maps={}
        return fba_map,arch_l,arch_rr,rb_set,opt_maps
    except Exception as e:
        st.error(f"DB fetch error: {e}"); return {},{},{},set(),{}

# ═══════════════════════════════════════════════════════════════════════════════
#  CORE FILL ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
def fill_row(asin, fba, arch_l, arch_r, brand, restricted_set, optional_maps):
    fba=fba or {}; arch_l=arch_l or {}; arch_r=arch_r or {}
    result={}

    def f(col,val): result[col]=val

    # INV(A-Z) & SKU Status(A-Z) — SKU from archive left
    v,_=get_src_val(arch_l,"sku(A-Z)","sku","SKU")
    f("INV(A-Z)", v or "N/A"); f("SKU Status(A-Z)", v or "N/A")

    # INV(Z-A) & SKU Status(Z-A) — SKU from archive right
    v,_=get_src_val(arch_r,"sku(Z-A)","sku","SKU")
    f("INV(Z-A)", v or "N/A"); f("SKU Status(Z-A)", v or "N/A")

    # Listing Status
    v,_=get_src_val(fba,"afn-listing-exists","mfn-listing-exists","listing")
    f("Listing Status","Listed" if v and v.lower() in ("yes","true","1","active","listed") else ("Not Listed" if v else "N/A"))

    # Restricted
    brand_l=brand.strip().lower() if brand else ""
    is_r=bool(brand_l and brand_l in restricted_set)
    f("Restricted","Yes — Restricted" if is_r else "No")

    # Sales 30 / 3 / 1
    for col,aliases in [("Sales 30",["Sales 30","sales30","30 day sales"]),
                        ("Sales 3", ["Sales 3","sales3","3 day sales"]),
                        ("Sales 1", ["Sales 1","sales1","1 day sales"])]:
        v,_=get_src_val(fba,*aliases); f(col,v or "N/A")

    # Stock — FBA first, Archive fallback
    v,_=get_src_val(fba,"STOCK","afn-fulfillable-quantity","fulfillable")
    if not v: v,_=get_src_val(arch_l,"afn-fulfillable-quantity","STOCK")
    f("Stock",v or "0")

    # Reserve
    v,_=get_src_val(fba,"RESERVE","afn-reserved-quantity","afn-reserve")
    if not v: v,_=get_src_val(arch_l,"afn-reserved-quantity","RESERVE")
    f("Reserve",v or "0")

    # Inbound
    v,_=get_src_val(fba,"INBOUND","afn-inbound-working-quantity","afn-inbound-shipped-quantity","afn-inbound")
    f("Inbound",v or "0")

    # TOTAL
    v,_=get_src_val(fba,"afn-total-quantity","TOTAL")
    if not v: v,_=get_src_val(arch_l,"afn-total-quantity","TOTAL")
    if not v:
        try: v=str(int(safe_float(result.get("Stock","0"))+safe_float(result.get("Reserve","0"))+safe_float(result.get("Inbound","0"))))
        except: v="0"
    f("TOTAL(Stock+Reserve+inbound)",v)

    # Days of stock
    try:
        sv=safe_float(result.get("Stock","0")); s30=safe_float(result.get("Sales 30","0"))
        f("Days of stock(30)",str(round(sv/(s30/30),1)) if s30>0 else "N/A")
    except: f("Days of stock(30)","N/A")
    try:
        sv=safe_float(result.get("Stock","0")); s3=safe_float(result.get("Sales 3","0"))
        f("Days of stock(3)",str(round(sv/(s3/3),1)) if s3>0 else "N/A")
    except: f("Days of stock(3)","N/A")

    # Optional files — smart column detection
    opt_cols_needed=[c for c in TARGET_COLS if c not in result]
    all_opt_rows=[]
    if optional_maps:
        for label,omap in optional_maps.items():
            if asin in omap: all_opt_rows.append(omap[asin])
    for opt_row in all_opt_rows:
        mapped=smart_map_optional_cols(opt_row,opt_cols_needed)
        for col,val in mapped.items():
            if col not in result or result[col]=="N/A":
                result[col]=val

    # Fill remaining with N/A
    for col in TARGET_COLS:
        if col not in result: f(col,"N/A")

    return result, is_r

# ═══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
for k,v in [("run_result",None),("vendor_history",[]),("source_loaded",False)]:
    if k not in st.session_state: st.session_state[k]=v

# ═══════════════════════════════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════════════════════════════
tab_run, tab_upload, tab_dash, tab_history, tab_map = st.tabs([
    "⚡  Run Analysis","☁️  Update Database","📊  Dashboard","📈  History","📋  Column Map"
])

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB — COLUMN MAP
# ═══════════════════════════════════════════════════════════════════════════════
with tab_map:
    st.markdown('<div class="section-title">Exact Column Mapping Reference</div>', unsafe_allow_html=True)
    st.markdown("""
<table class="map-table">
<tr><th>#</th><th>Analysis Column</th><th>Source</th><th>Source Column</th><th>Logic</th></tr>
<tr><td>1</td><td>INV(A-Z)</td><td><span class="pill p-arch">Archive Left</span></td><td>sku(A-Z)</td><td>SKU from asin(A-Z) table</td></tr>
<tr><td>2</td><td>INV(Z-A)</td><td><span class="pill p-arch">Archive Right</span></td><td>sku(Z-A)</td><td>SKU from asin(Z-A) table</td></tr>
<tr><td>3</td><td>Listing Status</td><td><span class="pill p-fba">FBA Inv</span></td><td>afn-listing-exists</td><td>Yes→Listed / No→Not Listed</td></tr>
<tr><td>4</td><td>Restricted</td><td><span class="pill p-rb">Restricted Brands</span></td><td>Brand name list</td><td>Exact brand match</td></tr>
<tr><td>5</td><td>SKU Status(A-Z)</td><td><span class="pill p-arch">Archive Left</span></td><td>sku(A-Z)</td><td>SKU from asin(A-Z) table</td></tr>
<tr><td>6</td><td>SKU Status(Z-A)</td><td><span class="pill p-arch">Archive Right</span></td><td>sku(Z-A)</td><td>SKU from asin(Z-A) table</td></tr>
<tr><td>7</td><td>Ageing</td><td><span class="pill p-opt">Optional File</span></td><td>ageing / aging</td><td>Smart keyword match</td></tr>
<tr><td>8</td><td>Return</td><td><span class="pill p-opt">Optional File</span></td><td>return / returns</td><td>Smart keyword match</td></tr>
<tr><td>9</td><td>FBM-LIFETIME</td><td><span class="pill p-opt">Optional File</span></td><td>fbm lifetime</td><td>Smart keyword match</td></tr>
<tr><td>10</td><td>FBM-LAST YEAR</td><td><span class="pill p-opt">Optional File</span></td><td>fbm last year</td><td>Smart keyword match</td></tr>
<tr><td>11</td><td>FBM-CURRENT YEAR</td><td><span class="pill p-opt">Optional File</span></td><td>fbm current year</td><td>Smart keyword match</td></tr>
<tr><td>12</td><td>Net Ordered GMS($)</td><td><span class="pill p-opt">Optional File</span></td><td>net ordered gms / gms</td><td>Smart keyword match</td></tr>
<tr><td>13</td><td>Net Ordered Units</td><td><span class="pill p-opt">Optional File</span></td><td>net ordered units</td><td>Smart keyword match</td></tr>
<tr><td>14</td><td>Lifetime</td><td><span class="pill p-opt">Optional File</span></td><td>lifetime / lifetime sales</td><td>Smart keyword match</td></tr>
<tr><td>15</td><td>Sales 2023</td><td><span class="pill p-opt">Optional File</span></td><td>sales 2023 / 2023</td><td>Smart keyword match</td></tr>
<tr><td>16</td><td>Current year</td><td><span class="pill p-opt">Optional File</span></td><td>current year / cy sales</td><td>Smart keyword match</td></tr>
<tr><td>17</td><td>Sales 30</td><td><span class="pill p-fba">FBA Inv</span></td><td>Sales 30</td><td>Direct fill</td></tr>
<tr><td>18</td><td>Sales 3</td><td><span class="pill p-fba">FBA Inv</span></td><td>Sales 3</td><td>Direct fill</td></tr>
<tr><td>19</td><td>Sales 1</td><td><span class="pill p-fba">FBA Inv</span></td><td>Sales 1</td><td>Direct fill</td></tr>
<tr><td>20</td><td>Stock</td><td><span class="pill p-fba">FBA Inv</span></td><td>STOCK</td><td>FBA → Archive fallback</td></tr>
<tr><td>21</td><td>Reserve</td><td><span class="pill p-fba">FBA Inv</span></td><td>RESERVE</td><td>FBA → Archive fallback</td></tr>
<tr><td>22</td><td>Inbound</td><td><span class="pill p-fba">FBA Inv</span></td><td>INBOUND</td><td>FBA only</td></tr>
<tr><td>23</td><td>TOTAL(Stock+Reserve+inbound)</td><td><span class="pill p-fba">FBA Inv</span></td><td>afn-total-quantity</td><td>FBA → Archive → Calculated</td></tr>
<tr><td>24</td><td>Days of stock(30)</td><td><span class="pill p-calc">Calculated</span></td><td>—</td><td>Stock ÷ (Sales30 ÷ 30)</td></tr>
<tr><td>25</td><td>Days of stock(3)</td><td><span class="pill p-calc">Calculated</span></td><td>—</td><td>Stock ÷ (Sales3 ÷ 3)</td></tr>
</table>
""", unsafe_allow_html=True)
    st.markdown("""
<div class="alert-box alert-blue" style="margin-top:1rem">
<strong>Output guarantee:</strong> The downloaded file is your exact analysis file — same columns, same order, same formatting.
Only the 25 target columns above are filled. Everything else is untouched.
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB — UPDATE DATABASE
# ═══════════════════════════════════════════════════════════════════════════════
with tab_upload:
    st.markdown('<div class="section-title">☁️ Update Source Database</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-sub">Do this once every morning. The whole team benefits instantly — no one else needs to upload source files.</div>', unsafe_allow_html=True)

    connected=db_connected()
    st.markdown(f'<div class="db-status"><div class="db-dot {"on" if connected else "off"}"></div>{"Connected to Supabase — ready" if connected else "Not connected — add SUPABASE_KEY to Streamlit Secrets"}</div>', unsafe_allow_html=True)

    if not connected:
        st.markdown("""<div class="alert-box alert-orange">
        <strong>Setup:</strong> Streamlit Cloud → Your app → Settings → Secrets → add:<br><br>
        <code>SUPABASE_KEY = "your-eyJ-anon-key-here"</code>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Required files <span style="color:#C2410C;font-size:0.75rem;font-weight:600;margin-left:8px;">Upload all 3 every morning</span></div>', unsafe_allow_html=True)
    rc1,rc2,rc3=st.columns(3)
    with rc1:
        st.markdown('<div class="card-title">📦 FBA Inventory</div><div class="card-sub">Required daily</div>', unsafe_allow_html=True)
        up_fba=st.file_uploader("FBA Inventory",type=["xlsx","xls","csv"],key="up_fba",label_visibility="collapsed")
    with rc2:
        st.markdown('<div class="card-title">🚫 Restricted Brands</div><div class="card-sub">Required daily</div>', unsafe_allow_html=True)
        up_rb=st.file_uploader("Restricted Brands",type=["xlsx","xls","csv"],key="up_rb",label_visibility="collapsed")
    with rc3:
        st.markdown('<div class="card-title">🗃️ Archive Inventory</div><div class="card-sub">Required daily</div>', unsafe_allow_html=True)
        up_arch=st.file_uploader("Archive Inventory",type=["xlsx","xls","csv"],key="up_arch",label_visibility="collapsed")

    st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Optional files <span style="color:#1D4ED8;font-size:0.75rem;font-weight:600;margin-left:8px;">Upload when available — smart column detection</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-box alert-blue">These files are matched by ASIN. Column names are auto-detected — upload any file with an ASIN column and the engine maps it automatically.</div>', unsafe_allow_html=True)

    oc1,oc2,oc3=st.columns(3)
    optional_files={}
    with oc1:
        label1=st.text_input("File 1 label","Lifetime Sales Report",key="opt_label1")
        up_opt1=st.file_uploader(f"Upload: {label1}",type=["xlsx","xls","csv"],key="up_opt1",label_visibility="collapsed")
        if up_opt1: optional_files[label1]=up_opt1
    with oc2:
        label2=st.text_input("File 2 label","Optional File 2",key="opt_label2")
        up_opt2=st.file_uploader(f"Upload: {label2}",type=["xlsx","xls","csv"],key="up_opt2",label_visibility="collapsed")
        if up_opt2: optional_files[label2]=up_opt2
    with oc3:
        label3=st.text_input("File 3 label","Optional File 3",key="opt_label3")
        up_opt3=st.file_uploader(f"Upload: {label3}",type=["xlsx","xls","csv"],key="up_opt3",label_visibility="collapsed")
        if up_opt3: optional_files[label3]=up_opt3

    upload_ready=all([up_fba,up_rb,up_arch])
    st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
    if st.button("☁️  Push All to Database",disabled=not upload_ready,use_container_width=True,type="primary"):
        with st.spinner("Processing and uploading..."):
            pb=st.progress(0)
            fba_df2=read_file(up_fba); pb.progress(10)
            rb_df2=read_file(up_rb);   pb.progress(18)
            fba_map2,_,_=build_fba_map(fba_df2); pb.progress(30)
            arch_l2,arch_r2=read_archive_dual(up_arch); pb.progress(48)
            rb_set2=set(rb_df2[rb_df2.columns[0]].str.strip().str.lower().dropna()); pb.progress(55)

            opt_maps2={}
            for i,(lbl,fobj) in enumerate(optional_files.items()):
                df_opt=read_file(fobj)
                omap,_=build_generic_map(df_opt)
                if omap: opt_maps2[lbl]=omap
                pb.progress(55+int(20*(i+1)/max(1,len(optional_files))))

            if connected:
                ok,err=push_to_db(fba_map2,arch_l2,arch_r2,rb_set2,opt_maps2); pb.progress(100)
                if ok:
                    st.success(f"✅ Database updated — FBA: {len(fba_map2):,} · Archive L: {len(arch_l2):,} · Archive R: {len(arch_r2):,} · Restricted: {len(rb_set2):,} · Optional files: {len(opt_maps2)}")
                    st.session_state.source_loaded=True
                else: st.error(f"Upload failed: {err}")
            else:
                st.session_state["_src"]={
                    "fba":fba_map2,"arch_l":arch_l2,"arch_r":arch_r2,
                    "rb":rb_set2,"opt":opt_maps2
                }
                st.session_state.source_loaded=True; pb.progress(100)
                st.success(f"✅ Loaded in session (add Supabase key to persist) — FBA: {len(fba_map2):,} · Archive: {len(arch_l2)+len(arch_r2):,} · Restricted: {len(rb_set2):,} · Optional: {len(opt_maps2)}")

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB — RUN ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_run:
    src_ready=db_connected() or st.session_state.source_loaded
    use_db=src_ready

    st.markdown('<div class="section-title">Upload Analysis File</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-box alert-blue">Upload your full analysis file as-is. The engine will find the <strong>Output ASIN</strong> column automatically, fill only the target columns, and return your file in the exact same format.</div>', unsafe_allow_html=True)

    ac1,ac2=st.columns([2,1],gap="large")
    with ac1:
        an_file=st.file_uploader("📊 Analysis file (full template)",type=["xlsx","xls","csv"],key="an")
    with ac2:
        vendor_name=st.text_input("Vendor / file label",placeholder="e.g. ALLWAY, 3M, Echo Park...")
        if not use_db:
            st.markdown('<div class="alert-box alert-amber">⚠️ No source data. Go to <strong>Update Database</strong> tab first.</div>', unsafe_allow_html=True)

        if not use_db:
            with st.expander("📁 Or upload source files manually"):
                fba_file=st.file_uploader("📦 FBA Inventory",type=["xlsx","xls","csv"],key="fba_m")
                rb_file=st.file_uploader("🚫 Restricted Brands",type=["xlsx","xls","csv"],key="rb_m")
                arch_file=st.file_uploader("🗃️ Archive Inventory",type=["xlsx","xls","csv"],key="arch_m")
                use_db=False
                src_ready_manual=all([fba_file,rb_file,arch_file]) if not use_db else True
        else:
            fba_file=rb_file=arch_file=None
            src_ready_manual=True

    # Pre-flight
    if an_file:
        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        an_prev=read_file(an_file); an_file.seek(0)
        if not an_prev.empty:
            ac_p,ap_p=detect_asin_col(an_prev)

            pc1,pc2,pc3=st.columns(3)
            with pc1:
                if ac_p:
                    samples=an_prev[ac_p].dropna().head(3).tolist()
                    st.markdown(f'<div class="alert-box alert-green">✅ ASIN column: <strong>"{ac_p}"</strong> ({ap_p}%)<br><code>{" · ".join(samples)}</code></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="alert-box alert-red">❌ No ASIN column found</div>', unsafe_allow_html=True)
            with pc2:
                target_found=[c for c in TARGET_COLS if any(c.lower() in col.lower() or col.lower() in c.lower() for col in an_prev.columns)]
                st.markdown(f'<div class="alert-box alert-green">✅ {len(target_found)}/{len(TARGET_COLS)} target columns found in file</div>', unsafe_allow_html=True)
            with pc3:
                st.markdown(f'<div class="alert-box alert-blue">📄 {len(an_prev):,} rows · {len(an_prev.columns)} columns · will return exact same format</div>', unsafe_allow_html=True)

    all_ready=bool(an_file and (use_db or src_ready_manual if not (db_connected() or st.session_state.source_loaded) else True))
    st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
    run_btn=st.button("⚡  Run VirVentures DataOps Engine",disabled=not all_ready,use_container_width=True,type="primary")

    if run_btn and all_ready:
        t0=time.time(); logs=[]
        def log(msg,kind="info"):
            cls={"ok":"lok","warn":"lwarn","err":"lerr","head":"lhead"}.get(kind,"linfo")
            logs.append(f'<span class="{cls}">{msg}</span>')

        prog=st.progress(0); status=st.empty()

        # Read analysis
        status.write("Reading analysis file...")
        an_df=read_file(an_file)
        if an_df.empty: st.error("Cannot read analysis file."); st.stop()

        # Detect ASIN col
        an_asin_col,an_asin_pct=detect_asin_col(an_df)
        if not an_asin_col:
            # try explicit name search
            for col in an_df.columns:
                if "output asin" in col.lower() or "input asin" in col.lower():
                    an_asin_col=col; an_asin_pct=100; break
        if not an_asin_col: st.error("❌ Cannot find ASIN column in analysis file."); st.stop()

        an_brand_col,_=smart_col(an_df,["Brand","brand","BRAND"])
        all_asins=[clean_asin(v) for v in an_df[an_asin_col] if is_asin(clean_asin(str(v)))]

        log(f"◆ ANALYSIS — {len(an_df):,} rows | ASIN col: '{an_asin_col}' ({an_asin_pct}%) | {len(all_asins):,} valid ASINs","head")
        prog.progress(12)

        # Get source data
        status.write("Loading source data...")
        if db_connected():
            fba_map,arch_left,arch_right,restricted_set,opt_maps=fetch_from_db(all_asins)
            log(f"◆ SOURCE FROM SUPABASE — FBA:{len(fba_map):,} | Arch:{len(arch_left)+len(arch_right):,} | RB:{len(restricted_set):,} | OptFiles:{len(opt_maps)}","head")
        elif st.session_state.source_loaded and "_src" in st.session_state:
            src=st.session_state["_src"]
            fba_map=src["fba"]; arch_left=src["arch_l"]; arch_right=src["arch_r"]
            restricted_set=src["rb"]; opt_maps=src["opt"]
            log(f"◆ SOURCE FROM SESSION — FBA:{len(fba_map):,} | Arch:{len(arch_left)+len(arch_right):,} | RB:{len(restricted_set):,}","head")
        else:
            fba_df2=read_file(fba_file); rb_df2=read_file(rb_file)
            fba_map,_,_=build_fba_map(fba_df2)
            arch_left,arch_right=read_archive_dual(arch_file)
            restricted_set=set(rb_df2[rb_df2.columns[0]].str.strip().str.lower().dropna())
            opt_maps={}
            log(f"◆ SOURCE FROM FILES — FBA:{len(fba_map):,} | Arch:{len(arch_left)+len(arch_right):,}","head")
        prog.progress(40)

        # Process rows
        status.write("Processing all rows...")
        out_rows=[]; anomalies=[]
        fba_hits=arch_hits=restr_count=filled=no_match=0
        n=len(an_df)

        for idx,row in an_df.iterrows():
            # Start with the COMPLETE original row — nothing dropped
            nr=row.to_dict()
            asin=clean_asin(str(row[an_asin_col]))
            brand=str(row.get(an_brand_col,"")).strip() if an_brand_col else ""

            if not is_asin(asin):
                # Still fill N/A for target cols that are blank
                for col in TARGET_COLS:
                    if col in nr and is_blank(str(nr.get(col,""))): nr[col]="N/A"
                out_rows.append(nr); continue

            fba_row  =fba_map.get(asin)
            arch_l_row=arch_left.get(asin)
            arch_r_row=arch_right.get(asin)

            if fba_row: fba_hits+=1
            if arch_l_row or arch_r_row: arch_hits+=1
            if not any([fba_row,arch_l_row,arch_r_row]): no_match+=1

            filled_vals,is_r=fill_row(asin,fba_row,arch_l_row,arch_r_row,brand,restricted_set,opt_maps)
            if is_r: restr_count+=1

            # Count fills — only where value changed from blank to real data
            for col,val in filled_vals.items():
                if col in nr and is_blank(str(nr.get(col,""))) and val not in ("N/A","0"):
                    filled+=1
                # Always apply fill to target cols
                nr[col]=val

            # Anomaly detection
            sv  =safe_float(nr.get("Stock","0"))
            s30 =safe_float(nr.get("Sales 30","0"))
            dos =safe_float(nr.get("Days of stock(30)","999") if str(nr.get("Days of stock(30)",""))!="N/A" else "999")
            lst =str(nr.get("Listing Status","")).lower()

            if sv==0 and s30>5:
                anomalies.append({"type":"🔴 Zero stock / high velocity","severity":"red","asin":asin,"brand":brand,"detail":f"0 stock | {s30:.0f} sold last 30d"})
            elif 0<dos<7:
                anomalies.append({"type":"🔴 Critical — under 7 days","severity":"red","asin":asin,"brand":brand,"detail":f"{dos} days remaining"})
            elif 7<=dos<14:
                anomalies.append({"type":"🟡 Low stock warning","severity":"amber","asin":asin,"brand":brand,"detail":f"{dos} days remaining"})
            if is_r and "listed" in lst:
                anomalies.append({"type":"🚫 Restricted + Active listing","severity":"red","asin":asin,"brand":brand,"detail":f"'{brand}' restricted but listed"})

            out_rows.append(nr)
            if idx%max(1,n//30)==0: prog.progress(40+int(50*idx/n))

        prog.progress(92)

        # Build output — EXACT SAME COLUMNS as input, in exact same order
        # Only difference: target cols are now filled
        original_cols=list(an_df.columns)
        out_df=pd.DataFrame(out_rows)

        # Add any target cols that weren't in original (new columns at end)
        new_cols=[c for c in TARGET_COLS if c not in original_cols]
        final_cols=original_cols+new_cols
        for c in final_cols:
            if c not in out_df.columns: out_df[c]="N/A"
        out_df=out_df[final_cols]  # exact original order + any new target cols appended

        # Write Excel
        status.write("Writing output...")
        buf=io.BytesIO()
        with pd.ExcelWriter(buf,engine="openpyxl") as writer:
            out_df.to_excel(writer,index=False,sheet_name="Analysis_Filled")
            if anomalies:
                pd.DataFrame(anomalies)[["type","asin","brand","detail"]].to_excel(writer,index=False,sheet_name="Anomaly_Alerts")
            # Audit trail — first 500 rows, only target cols
            audit=[{"Row":i+2,"ASIN":r.get(an_asin_col,""),"Column":col,"Value":r.get(col,"")}
                   for i,r in enumerate(out_rows[:500]) for col in TARGET_COLS]
            pd.DataFrame(audit).to_excel(writer,index=False,sheet_name="Audit_Trail")
        buf.seek(0); prog.progress(100); t1=time.time()
        status.empty(); prog.empty()

        match_rate=pct(fba_hits,n)
        log(f"◆ COMPLETE — {round(t1-t0,2)}s","head")
        log(f"  Total rows     : {n:,}","ok")
        log(f"  FBA matched    : {fba_hits:,} ({match_rate}%)","ok")
        log(f"  Archive matched: {arch_hits:,} ({pct(arch_hits,n)}%)","ok")
        log(f"  Unmatched ASINs: {no_match:,}","warn" if no_match else "ok")
        log(f"  Cells filled   : {filled:,}","ok")
        log(f"  Restricted     : {restr_count:,}","warn" if restr_count else "ok")
        log(f"  Anomalies      : {len(anomalies):,}","warn" if anomalies else "ok")
        log(f"  Output cols    : {len(final_cols)} (exact input format preserved)","ok")

        st.session_state.run_result={
            "out_df":out_df,"buf":buf.getvalue(),"n":n,
            "fba_hits":fba_hits,"arch_hits":arch_hits,
            "filled":filled,"restr_count":restr_count,
            "no_match":no_match,"anomalies":anomalies,
            "match_rate":match_rate,"logs":logs,
            "elapsed":round(t1-t0,2),
            "vendor":vendor_name or "Unknown",
            "run_date":str(date.today()),
        }
        if vendor_name:
            st.session_state.vendor_history.append({
                "vendor":vendor_name,"date":str(date.today()),
                "rows":n,"match_rate":match_rate,"filled":filled,
                "restricted":restr_count,"anomalies":len(anomalies),"unmatched":no_match
            })

    # Results
    if st.session_state.run_result:
        r=st.session_state.run_result
        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Run Report</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-row">
          <div class="metric-box orange"><div class="m-val orange">{r['n']:,}</div><div class="m-lbl">Rows Processed</div></div>
          <div class="metric-box navy"><div class="m-val navy">{r['fba_hits']:,}</div><div class="m-lbl">FBA Matched ({r['match_rate']}%)</div></div>
          <div class="metric-box green"><div class="m-val green">{r['filled']:,}</div><div class="m-lbl">Cells Auto-Filled</div></div>
          <div class="metric-box {'red' if r['no_match'] else 'green'}"><div class="m-val {'red' if r['no_match'] else 'green'}">{r['no_match']:,}</div><div class="m-lbl">Unmatched ASINs</div></div>
          <div class="metric-box {'red' if r['restr_count'] else 'green'}"><div class="m-val {'red' if r['restr_count'] else 'green'}">{r['restr_count']:,}</div><div class="m-lbl">Restricted Flagged</div></div>
        </div>
        <div style="font-size:0.7rem;color:#F47920;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin:0.8rem 0 0.2rem">FBA Match Accuracy — {r['match_rate']}%</div>
        <div class="prog-wrap"><div class="prog-fill" style="width:{r['match_rate']}%"></div></div>
        """, unsafe_allow_html=True)

        st.markdown(f'<div class="log-box">{"<br>".join(r["logs"])}</div>', unsafe_allow_html=True)

        if r['anomalies']:
            st.markdown(f'<div class="section-title">⚠️ Anomaly Alerts — {len(r["anomalies"])} found</div>', unsafe_allow_html=True)
            for a in r['anomalies'][:20]:
                cls="alert-red" if a['severity']=="red" else "alert-amber"
                st.markdown(f'<div class="alert-box {cls}"><strong>{a["type"]}</strong> &nbsp;|&nbsp; <code>{a["asin"]}</code> &nbsp;|&nbsp; {a["brand"]} &nbsp;|&nbsp; {a["detail"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-box alert-green">✅ No anomalies detected — all ASINs healthy</div>', unsafe_allow_html=True)

        fname=f"VirVentures_{r['vendor']}_{date.today()}.xlsx"
        st.download_button(
            label=f"⬇️  Download  {fname}",
            data=r['buf'],file_name=fname,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,type="primary"
        )
        st.markdown('<div class="alert-box alert-blue" style="margin-top:0.5rem">📋 File includes 3 sheets: <strong>Analysis_Filled</strong> (exact original format) · <strong>Anomaly_Alerts</strong> · <strong>Audit_Trail</strong></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
with tab_dash:
    if not st.session_state.run_result:
        st.markdown('<div class="alert-box alert-blue" style="margin-top:1rem">Run the engine first to see your dashboard.</div>', unsafe_allow_html=True)
    else:
        r=st.session_state.run_result; out_df=r['out_df']
        st.markdown(f'<div class="section-title">📊 Dashboard — {r["vendor"]}</div>', unsafe_allow_html=True)
        st.markdown(f"<div class='card-sub'>{r['run_date']} &nbsp;·&nbsp; {r['elapsed']}s &nbsp;·&nbsp; {r['n']:,} rows</div>", unsafe_allow_html=True)

        st.markdown("#### 🔻 Top 10 Lowest Stock ASINs")
        if "Stock" in out_df.columns:
            tmp=out_df[~out_df["Stock"].isin(["N/A",""])].copy()
            tmp["_s"]=tmp["Stock"].apply(safe_float)
            show=[c for c in ["Output ASIN","Brand","Stock","Days of stock(30)","Sales 30","Listing Status","Restricted"] if c in tmp.columns]
            st.dataframe(tmp.nsmallest(10,"_s")[show],use_container_width=True,hide_index=True)

        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown("#### 🚫 Restricted Brand Breakdown")
        if "Restricted" in out_df.columns:
            brand_col=[c for c in out_df.columns if "brand" in c.lower()]
            bc=brand_col[0] if brand_col else None
            restr=out_df[out_df["Restricted"].str.startswith("Yes",na=False)]
            if not restr.empty and bc:
                counts=restr[bc].value_counts().reset_index(); counts.columns=["Brand","Count"]
                st.dataframe(counts,use_container_width=True,hide_index=True)
                st.markdown(f'<div class="alert-box alert-red">🚫 {len(restr):,} restricted ASINs across {counts["Brand"].nunique()} brands</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-box alert-green">✅ No restricted brands found</div>', unsafe_allow_html=True)

        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        if r['anomalies']:
            adf=pd.DataFrame(r['anomalies'])[["type","asin","brand","detail"]]
            adf.columns=["Alert","ASIN","Brand","Detail"]
            st.dataframe(adf,use_container_width=True,hide_index=True)

        mr=r['match_rate']; color="#F47920" if mr>=80 else "#fbbf24" if mr>=50 else "#dc2626"
        st.markdown(f'<div style="text-align:center;padding:1.5rem;background:#fff;border-radius:16px;border:1px solid #E8EBF0;margin-top:1rem;box-shadow:0 2px 10px rgba(30,45,78,0.06)"><div style="font-family:Space Grotesk,sans-serif;font-size:3.5rem;font-weight:800;color:{color}">{mr}%</div><div style="color:#8A9BB5;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.1em;margin-top:0.5rem">FBA Match Rate &nbsp;·&nbsp; {r["fba_hits"]:,} of {r["n"]:,} ASINs</div><div class="prog-wrap" style="max-width:400px;margin:1rem auto"><div class="prog-fill" style="width:{mr}%"></div></div></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB — HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
with tab_history:
    st.markdown('<div class="section-title">📈 Vendor Run History</div>', unsafe_allow_html=True)
    history=st.session_state.vendor_history
    if not history:
        st.markdown('<div class="alert-box alert-blue" style="margin-top:1rem">No history yet. Enter a vendor name before running to track.</div>', unsafe_allow_html=True)
    else:
        hdf=pd.DataFrame(history)
        hdf.columns=["Vendor","Date","Rows","Match %","Cells Filled","Restricted","Anomalies","Unmatched"]
        st.dataframe(hdf,use_container_width=True,hide_index=True)
        st.markdown("<hr class='divhr'>", unsafe_allow_html=True)
        st.markdown("#### Per-vendor summary")
        s=hdf.groupby("Vendor").agg({"Rows":"sum","Match %":"mean","Cells Filled":"sum","Restricted":"sum","Anomalies":"sum","Unmatched":"sum"}).round(1).reset_index()
        st.dataframe(s,use_container_width=True,hide_index=True)
        if st.button("🗑  Clear history"): st.session_state.vendor_history=[]; st.rerun()
