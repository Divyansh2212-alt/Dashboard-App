import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# =========================
# DARK THEME
# =========================
st.markdown("""
<style>
body {background-color: #0B1F3A; color: white;}
.block-container {padding-top: 1rem;}
h1, h2, h3, h4 {color: white;}
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA FIRST (needed for date in LIVE badge)
# =========================
sheet_url = "https://docs.google.com/spreadsheets/d/1Fq3M3yXOb_7ZBYnyNoRLYpBps5Ra_FdGFoaVFNPPewI/export?format=csv"
df = pd.read_csv(sheet_url)

df['Date'] = pd.to_datetime(df['Date'])
max_date = df['Date'].max()

# =========================
# HEADER WITH LIVE BADGE
# =========================
col1, col2 = st.columns([8,2])

with col1:
    st.title("📊 SH Performance Report")

with col2:
    st.markdown(f"""
    <div style="
        background-color:#0f5132;
        color:#00ff9c;
        padding:8px 12px;
        border-radius:8px;
        text-align:center;
        font-weight:bold;
        font-size:13px;
    ">
        🟢 LIVE | {max_date.date()}
    </div>
    """, unsafe_allow_html=True)

# =========================
# KPI CARDS
# =========================
latest_df = df[df['Date'] == max_date]

col1, col2, col3 = st.columns(3)

col1.metric("Total SH", latest_df['SH'].nunique())
col2.metric("Total SZM", latest_df['SZM'].nunique())
col3.metric("Total Hubs", latest_df['Hub'].nunique())

# =========================
# DATE CATEGORY
# =========================
df['Date Category'] = (max_date - df['Date']).dt.days
df = df[(df['Date Category'] >= 0) & (df['Date Category'] <= 6)]
df['Date Category'] = "D-" + (df['Date Category'] + 1).astype(str)

order = ['D-1','D-2','D-3','D-4','D-5','D-6','D-7']

# =========================
# GROUP SH
# =========================
df_grouped = df.groupby(['SH', 'Date Category']).agg({
    'FASR Num':'sum',
    'FASR Den':'sum',
    'FPSR Num':'sum',
    'FPSR Den':'sum',
    'Total Shipments':'sum',
    'NC Marked':'sum',
    'NC Validated':'sum'
}).reset_index()

# =========================
# METRICS
# =========================
df_grouped['FASR %'] = df_grouped['FASR Num'] / df_grouped['FASR Den']
df_grouped['FPSR %'] = df_grouped['FPSR Num'] / df_grouped['FPSR Den']
df_grouped['NC %'] = df_grouped['NC Marked'] / df_grouped['Total Shipments']
df_grouped['Masking %'] = df_grouped['NC Validated'] / df_grouped['NC Marked']

# =========================
# DELTA ARROW
# =========================
def add_arrow(val):
    if pd.isna(val): return ""
    if val > 0: return f"↑ {val:.2%}"
    elif val < 0: return f"↓ {abs(val):.2%}"
    else: return f"{val:.2%}"

# =========================
# SH LEVEL
# =========================
st.subheader("SH Level Performance")

for metric in ['FASR %','FPSR %','Masking %','NC %']:
    
    st.write(f"### {metric}")
    
    pivot = df_grouped.pivot(index='SH', columns='Date Category', values=metric)
    pivot = pivot[order]

    pivot['Delta'] = pivot['D-1'] - pivot['D-2']
    pivot['Delta'] = pivot['Delta'].apply(add_arrow)

    for col in order:
        pivot[col] = (pivot[col]*100).round(2).astype(str) + "%"

    st.dataframe(pivot)

# =========================
# TOP / WORST
# =========================
st.subheader("🏆 Top / Worst Performers (FASR D-1)")

top_df = df_grouped[df_grouped['Date Category']=='D-1'].sort_values('FASR %', ascending=False)

col1, col2 = st.columns(2)

with col1:
    st.write("### 🟢 Top 5")
    top5 = top_df[['SH','FASR %']].head(5).copy()
    top5['FASR %'] = (top5['FASR %']*100).round(2).astype(str)+"%"
    st.dataframe(top5)

with col2:
    st.write("### 🔴 Bottom 5")
    bottom5 = top_df[['SH','FASR %']].tail(5).copy()
    bottom5['FASR %'] = (bottom5['FASR %']*100).round(2).astype(str)+"%"
    st.dataframe(bottom5)

# =========================
# SZM LEVEL
# =========================
st.subheader("SZM Level Performance")

sh_selected = st.selectbox("Select SH", df['SH'].unique())

df_szm = df[df['SH'] == sh_selected]

df_szm_group = df_szm.groupby(['SZM','Date Category']).agg({
    'FASR Num':'sum',
    'FASR Den':'sum',
    'FPSR Num':'sum',
    'FPSR Den':'sum',
    'Total Shipments':'sum',
    'NC Marked':'sum',
    'NC Validated':'sum'
}).reset_index()

df_szm_group['FASR %'] = df_szm_group['FASR Num'] / df_szm_group['FASR Den']
df_szm_group['FPSR %'] = df_szm_group['FPSR Num'] / df_szm_group['FPSR Den']
df_szm_group['NC %'] = df_szm_group['NC Marked'] / df_szm_group['Total Shipments']
df_szm_group['Masking %'] = df_szm_group['NC Validated'] / df_szm_group['NC Marked']

for metric in ['FASR %','FPSR %','Masking %','NC %']:
    
    st.write(f"### {metric}")
    
    pivot = df_szm_group.pivot(index='SZM', columns='Date Category', values=metric)
    pivot = pivot[order]

    pivot['Delta'] = pivot['D-1'] - pivot['D-2']
    pivot['Delta'] = pivot['Delta'].apply(add_arrow)

    for col in order:
        pivot[col] = (pivot[col]*100).round(2).astype(str) + "%"

    st.dataframe(pivot)