import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

st.title("📊 SH Performance Dashboard")

# =========================
# LOAD DATA
# =========================

sheet_url = "https://docs.google.com/spreadsheets/d/1Fq3M3yXOb_7ZBYnyNoRLYpBps5Ra_FdGFoaVFNPPewI/export?format=xlsx"

df = pd.read_excel(sheet_url)

# =========================
# DATE LOGIC (FIXED)
# =========================

df['Date'] = pd.to_datetime(df['Date'])

# D-1 = YESTERDAY (NOT max date in data)
reference_date = datetime.today() - timedelta(days=1)

df['Date Category'] = (reference_date - df['Date']).dt.days

# Keep only D-1 to D-7
df = df[(df['Date Category'] >= 1) & (df['Date Category'] <= 7)]

df['Date Category'] = "D-" + df['Date Category'].astype(str)

# =========================
# SH LEVEL
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

# Metrics
df_grouped['FASR %'] = df_grouped['FASR Num'] / df_grouped['FASR Den']
df_grouped['FPSR %'] = df_grouped['FPSR Num'] / df_grouped['FPSR Den']
df_grouped['NC %'] = df_grouped['NC Marked'] / df_grouped['Total Shipments']
df_grouped['Masking %'] = df_grouped['NC Validated'] / df_grouped['NC Marked']

st.subheader("SH Level Performance")

for metric in ['FASR %','FPSR %','NC %','Masking %']:
    
    st.write(f"### {metric}")
    
    pivot = df_grouped.pivot(index='SH', columns='Date Category', values=metric)
    
    # Ensure correct order D-1 → D-7
    ordered_cols = [f"D-{i}" for i in range(1,8)]
    pivot = pivot.reindex(columns=ordered_cols)
    
    # DELTA (D-1 - D-2)
    if 'D-1' in pivot.columns and 'D-2' in pivot.columns:
        pivot['Delta'] = pivot['D-1'] - pivot['D-2']
    
    st.dataframe(
        pivot.style
        .format("{:.2%}")
        .background_gradient(cmap="RdYlGn")
    )

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

# Metrics
df_szm_group['FASR %'] = df_szm_group['FASR Num'] / df_szm_group['FASR Den']
df_szm_group['FPSR %'] = df_szm_group['FPSR Num'] / df_szm_group['FPSR Den']
df_szm_group['NC %'] = df_szm_group['NC Marked'] / df_szm_group['Total Shipments']
df_szm_group['Masking %'] = df_szm_group['NC Validated'] / df_szm_group['NC Marked']

for metric in ['FASR %','FPSR %','NC %','Masking %']:
    
    st.write(f"### {metric}")
    
    pivot = df_szm_group.pivot(index='SZM', columns='Date Category', values=metric)
    
    # Ensure correct order
    ordered_cols = [f"D-{i}" for i in range(1,8)]
    pivot = pivot.reindex(columns=ordered_cols)
    
    # DELTA
    if 'D-1' in pivot.columns and 'D-2' in pivot.columns:
        pivot['Delta'] = pivot['D-1'] - pivot['D-2']
    
    st.dataframe(
        pivot.style
        .format("{:.2%}")
        .background_gradient(cmap="RdYlGn")
    )