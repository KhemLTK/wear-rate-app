# streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.title("📊 Wear Rate Analysis App")

uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    brush_numbers = list(range(1, 33))
    upper_rates, lower_rates = {n:{} for n in brush_numbers}, {n:{} for n in brush_numbers}

    for sheet in sheet_names:
        df_raw = xls.parse(sheet, header=None)
        try:
            hours = float(df_raw.iloc[0, 7])
        except:
            st.warning(f"❌ อ่านชั่วโมงไม่ได้จาก {sheet}")
            continue

        df = xls.parse(sheet, skiprows=1, header=None)
        lower_df = df.iloc[:, 0:3].dropna()
        lower_df.columns = ["No_Lower", "Lower_Previous", "Lower_Current"]
        lower_df = lower_df.apply(pd.to_numeric, errors='coerce')

        upper_df = df.iloc[:, 4:6].dropna()
        upper_df.columns = ["Upper_Current", "Upper_Previous"]
        upper_df["No_Upper"] = range(1, len(upper_df)+1)
        upper_df = upper_df.apply(pd.to_numeric, errors='coerce')

        for n in brush_numbers:
            u_row = upper_df[upper_df["No_Upper"] == n]
            if not u_row.empty:
                diff = u_row.iloc[0]["Upper_Current"] - u_row.iloc[0]["Upper_Previous"]
                rate = max(diff / hours, 0)
                upper_rates[n][sheet] = rate

            l_row = lower_df[lower_df["No_Lower"] == n]
            if not l_row.empty:
                diff = l_row.iloc[0]["Lower_Previous"] - l_row.iloc[0]["Lower_Current"]
                rate = max(diff / hours, 0)
                lower_rates[n][sheet] = rate

    df_upper = pd.DataFrame.from_dict(upper_rates, orient='index')
    df_lower = pd.DataFrame.from_dict(lower_rates, orient='index')
    df_upper["Avg Rate (Upper)"] = df_upper.replace(0, np.nan).mean(axis=1)
    df_lower["Avg Rate (Lower)"] = df_lower.replace(0, np.nan).mean(axis=1)

    x_vals = brush_numbers
    y_upper = df_upper["Avg Rate (Upper)"]
    y_lower = df_lower["Avg Rate (Lower)"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_vals, y=y_upper, name='Upper Avg Rate', mode='lines+markers', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=x_vals, y=y_lower, name='Lower Avg Rate', mode='lines+markers', line=dict(color='darkred')))
    fig.update_layout(title="Average Wear Rate per Brush", xaxis_title="Brush Number", yaxis_title="Rate (mm/hour)", template='plotly_white')

    st.plotly_chart(fig)
