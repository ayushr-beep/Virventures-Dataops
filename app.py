import streamlit as st
import pandas as pd
import io
from datetime import date

st.set_page_config(page_title="Buying Team — Analysis Auto-Fill", page_icon="📦", layout="wide")

st.title("📦 Buying Team — Analysis Auto-Fill")
st.markdown("Upload your 3 daily source files + analysis file. The tool matches on **ASIN** and fills all missing columns instantly.")

st.divider()

# ── helpers ──────────────────────────────────────────────────────────────────

def read_uploaded(file):
    name = file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(file, dtype=str).fillna("")
    else:
        return pd.read_excel(file, dtype=str).fillna("")

def find_col(df, candidates):
    cols_lower = {c.lower().strip(): c for c in df.columns}
    for cand in candidates:
        for col_low, col_orig in cols_lower.items():
            if cand.lower() in col_low:
                return col_orig
    return None

def is_empty(val):
    return str(val).strip() in ("", "N/A", "#N/A", "0", "nan", "NaN")

# ── upload section ────────────────────────────────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    st.subheader("Step 1 — Source Files")
    fba_file   = st.file_uploader("FBA Inventory file",       type=["xlsx","xls","csv"], key="fba")
    rb_file    = st.file_uploader("Restricted Brands file",   type=["xlsx","xls","csv"], key="rb")
    arch_file  = st.file_uploader("Archive Inventory file",   type=["xlsx","xls","csv"], key="arch")

with col2:
    st.subheader("Step 2 — Analysis File")
    an_file    = st.file_uploader("Analysis file (with blank / N/A columns)", type=["xlsx","xls","csv"], key="an")

st.divider()

# ── process ───────────────────────────────────────────────────────────────────

all_ready = fba_file and rb_file and arch_file and an_file

if not all_ready:
    st.info("Upload all 4 files above to enable processing.")
else:
    if st.button("⚡ Match & Fill All Columns", type="primary", use_container_width=True):

        with st.spinner("Reading files..."):
            fba_df  = read_uploaded(fba_file)
            rb_df   = read_uploaded(rb_file)
            arch_df = read_uploaded(arch_file)
            an_df   = read_uploaded(an_file)

        logs = []

        # ── restricted brands set ────────────────────────────────────────────
        rb_col = find_col(rb_df, ["brand","restricted","name"]) or rb_df.columns[0]
        restricted_set = set(rb_df[rb_col].str.strip().str.lower().dropna())
        logs.append(f"✅ Restricted brands loaded: {len(restricted_set)} brands")

        # ── FBA map  (ASIN → row dict) ───────────────────────────────────────
        fba_asin_col = find_col(fba_df, ["asin"]) or "asin"
        fba_map = {}
        if fba_asin_col in fba_df.columns:
            for _, row in fba_df.iterrows():
                asin = str(row[fba_asin_col]).strip().upper()
                if asin:
                    fba_map[asin] = row.to_dict()
        logs.append(f"✅ FBA map built: {len(fba_map)} ASINs")

        # ── Archive map ──────────────────────────────────────────────────────
        arch_asin_col = find_col(arch_df, ["asin"]) or "asin"
        arch_map = {}
        if arch_asin_col in arch_df.columns:
            for _, row in arch_df.iterrows():
                asin = str(row[arch_asin_col]).strip().upper()
                if asin:
                    arch_map[asin] = row.to_dict()
        logs.append(f"✅ Archive map built: {len(arch_map)} ASINs")

        # ── process analysis rows ────────────────────────────────────────────
        an_asin_col   = find_col(an_df, ["asin"])
        an_brand_col  = find_col(an_df, ["brand"])
        an_stock_col  = find_col(an_df, ["stock"])
        an_reserve_col= find_col(an_df, ["reserve"])
        an_inbound_col= find_col(an_df, ["inbound"])
        an_price_col  = find_col(an_df, ["net price","netprice","price"])
        an_total_col  = find_col(an_df, ["total(st","total"])
        an_restr_col  = find_col(an_df, ["restrict"])

        output_rows = []
        matched = 0
        restricted_count = 0

        for _, row in an_df.iterrows():
            new_row = row.to_dict()
            asin = str(row[an_asin_col]).strip().upper() if an_asin_col else ""
            brand = str(row[an_brand_col]).strip().lower() if an_brand_col else ""

            row_matched = False

            # fill from FBA
            if asin and asin in fba_map:
                row_matched = True
                fba = fba_map[asin]
                fba_stock   = find_col(fba_df, ["stock","afn-fulfillable","fulfillable"])
                fba_reserve = find_col(fba_df, ["reserve","afn-reserve"])
                fba_inbound = find_col(fba_df, ["inbound","afn-inbound"])
                fba_price   = find_col(fba_df, ["your-price","price"])
                fba_total   = find_col(fba_df, ["afn-total","total"])

                pairs = [
                    (an_stock_col,   fba_stock),
                    (an_reserve_col, fba_reserve),
                    (an_inbound_col, fba_inbound),
                    (an_price_col,   fba_price),
                    (an_total_col,   fba_total),
                ]
                for an_c, fb_c in pairs:
                    if an_c and fb_c and is_empty(new_row.get(an_c, "")):
                        new_row[an_c] = fba.get(fb_c, "")

                # append extra FBA columns not already in analysis
                existing_low = {k.lower() for k in new_row}
                for fk, fv in fba.items():
                    fk_low = fk.lower()
                    if "asin" in fk_low or "sku" in fk_low:
                        continue
                    if fk_low not in existing_low:
                        new_row["FBA_" + fk] = fv
                        existing_low.add("fba_" + fk_low)

            # fill from Archive
            if asin and asin in arch_map:
                row_matched = True
                arch = arch_map[asin]
                existing_low = {k.lower() for k in new_row}
                for ak, av in arch.items():
                    ak_low = ak.lower()
                    if "asin" in ak_low or "sku" in ak_low:
                        continue
                    if ak_low not in existing_low and ("fba_" + ak_low) not in existing_low:
                        new_row["ARCH_" + ak] = av
                        existing_low.add("arch_" + ak_low)

            if row_matched:
                matched += 1

            # restricted brand flag
            is_restricted = brand and brand in restricted_set
            if is_restricted:
                restricted_count += 1
            flag_val = "Yes — Restricted" if is_restricted else "No"
            if an_restr_col:
                new_row[an_restr_col] = flag_val
            else:
                new_row["Restricted_Brand"] = flag_val

            output_rows.append(new_row)

        output_df = pd.DataFrame(output_rows)
        logs.append(f"✅ Matched {matched} of {len(an_df)} ASINs")
        logs.append(f"✅ Restricted brand flags: {restricted_count} flagged")
        logs.append("✅ Done! Download your file below.")

        # show logs
        for l in logs:
            st.write(l)

        # metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows processed", len(an_df))
        c2.metric("ASINs matched",  matched)
        c3.metric("Restricted brands flagged", restricted_count)

        # download
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            output_df.to_excel(writer, index=False, sheet_name="Analysis_Filled")
        buf.seek(0)

        fname = f"Analysis_Filled_{date.today()}.xlsx"
        st.download_button(
            label="⬇️ Download filled analysis file",
            data=buf,
            file_name=fname,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )

        st.success(f"File ready: **{fname}**")
