import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("📊 SH Performance Dashboard")

# ✅ READ GOOGLE SHEET (CSV FORMAT - FIXED)
sheet_url = "https://docs.google.com/spreadsheets/d/1Fq3M3yXOb_7ZBYnyNoRLYpBps5Ra_FdGFoaVFNPPewI/export?format=csv"
df = pd.read_csv(sheet_url)

# ✅ Convert Date
df['Date'] = pd.to_datetime(df['Date'])

# ✅ Get latest date (D-1 = MAX DATE)
max_date = df['Date'].max()

# ✅ Create Date Category (D-1 to D-7)
df['Date Category'] = (max_date - df['Date']).dt.days
df = df[(df['Date Category'] >= 0) & (df['Date Category'] <= 6)]

df['Date Category'] = "D-" + (df['Date Category'] + 1).astype(str)

# ✅ GROUP DATA (SH LEVEL)
df_grouped = df.groupby(['SH', 'Date Category']).agg({
    'FASR Num':'sum',
    'FASR Den':'sum',
    'FPSR Num':'sum',
    'FPSR Den':'sum',
    'Total Shipments':'sum',
    'NC Marked':'sum',
    'NC Validated':'sum'
}).reset_index()

# ✅ METRICS
df_grouped['FASR %'] = df_grouped['FASR Num'] / df_grouped['FASR Den']
df_grouped['FPSR %'] = df_grouped['FPSR Num'] / df_grouped['FPSR Den']
df_grouped['NC %'] = df_grouped['NC Marked'] / df_grouped['Total Shipments']
df_grouped['Masking %'] = df_grouped['NC Validated'] / df_grouped['NC Marked']

st.subheader("SH Level Performance")

# ✅ SORT ORDER FIX (D-1 to D-7)
order = ['D-1','D-2','D-3','D-4','D-5','D-6','D-7']

for metric in ['FASR %','FPSR %','NC %','Masking %']:
    st.write(f"### {metric}")
    
    pivot = df_grouped.pivot(index='SH', columns='Date Category', values=metric)
    pivot = pivot[order]

    # ✅ DELTA (D-1 - D-2)
    pivot['Delta'] = pivot['D-1'] - pivot['D-2']

    st.dataframe(pivot.style.format("{:.2%}"))

# =========================
# SZM LEVEL
# =========================

st.subheader("SZM Level")

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

for metric in ['FASR %','FPSR %','NC %','Masking %']:
    st.write(f"### {metric}")
    
    pivot = df_szm_group.pivot(index='SZM', columns='Date Category', values=metric)
    pivot = pivot[order]

    # ✅ DELTA
    pivot['Delta'] = pivot['D-1'] - pivot['D-2']

    st.dataframe(pivot.style.format("{:.2%}"))