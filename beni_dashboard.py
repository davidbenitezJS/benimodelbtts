import streamlit as st
import pandas as pd
import os
import plotly.express as px

pd.options.display.float_format = "{:.2f}".format

st.set_page_config(page_title="BENI Football Model", layout="wide")

# -----------------------------
# ESTILO GENERAL
# -----------------------------

st.markdown(
"""
<style>

section.main > div {
padding-top: 2rem;
}

.metric-card {
background-color:#111827;
padding:20px;
border-radius:14px;
border:1px solid #1f2937;
text-align:center;
}

.metric-title {
font-size:14px;
color:#9ca3af;
}

.metric-value {
font-size:34px;
font-weight:700;
}

</style>
""",
unsafe_allow_html=True
)

# -----------------------------
# TITULO
# -----------------------------

st.markdown(
"<h1 style='text-align:center'>⚽ BENI Football Model Dashboard</h1>",
unsafe_allow_html=True
)

st.divider()

# -----------------------------
# DESCRIPCION MODELO
# -----------------------------

st.markdown(
"""
<div style="
background-color:#111827;
padding:20px;
border-radius:14px;
border:1px solid #1f2937;
margin-bottom:25px">

<b>BENI BTTS Prediction Model</b><br><br>

This model estimates the probability that both teams score in a football match
using expected goals metrics and historical scoring patterns.

<b>Inputs</b><br>
• Expected Goals (xG)<br>
• Expected Goals Against (xGA)<br>
• Historical BTTS frequency<br>
• Market implied probability<br><br>

<b>Outputs</b><br>
• Predicted BTTS probability<br>
• Model advantage vs market expectation<br>
• Historical model evaluation

</div>
""",
unsafe_allow_html=True
)

# -----------------------------
# CARGAR DATA
# -----------------------------

archivo = "beni_data.xlsx"

if os.path.exists(archivo):
    df_hist = pd.read_excel(archivo)
else:
    st.error("No se encontró beni_data.xlsx")
    st.stop()

df_hist = df_hist.copy()

# -----------------------------
# LIMPIEZA
# -----------------------------

df_hist = df_hist[df_hist["Mercado"] == "BTTS"]

df_hist["Fecha"] = pd.to_datetime(df_hist["Fecha"])
df_hist = df_hist.sort_values("Fecha", ascending=False).reset_index(drop=True)

df_hist["Fecha"] = df_hist["Fecha"].dt.strftime("%d-%m-%Y")

df_hist["Home Goals"] = pd.to_numeric(df_hist["Home Goals"], errors="coerce").fillna(0).astype(int)
df_hist["Away Goals"] = pd.to_numeric(df_hist["Away Goals"], errors="coerce").fillna(0).astype(int)

df_hist["Partido"] = df_hist["Home"] + " vs " + df_hist["Away"]

df_hist["Resultado"] = (
df_hist["Home Goals"].astype(str) + "-" +
df_hist["Away Goals"].astype(str)
)

df_hist["BTTS"] = df_hist.apply(
lambda row: "🟢" if row["Home Goals"]>0 and row["Away Goals"]>0 else "🔴",
axis=1
)

df_hist["xG Proyectado"] = (
(df_hist["xG Home"] + df_hist["xGA Away"]) / 2 +
(df_hist["xG Away"] + df_hist["xGA Home"]) / 2
).round(2)

df_hist["Prob Implícita"] = (1/df_hist["Cuota"]*100).round(1)

df_hist["Prob BENI"] = (
df_hist["Prob Implícita"] + (df_hist["EDGE"]*100)
).round(1)

df_hist["EDGE"] = (df_hist["EDGE"]*100).round(2)

df_hist["Cuota"] = df_hist["Cuota"].round(2)

# -----------------------------
# CALCULOS MODELO
# -----------------------------

wins = (df_hist["BTTS"]=="🟢").sum()
losses = (df_hist["BTTS"]=="🔴").sum()

total_matches = wins + losses

win_rate = (wins/total_matches)*100 if total_matches>0 else 0

model_gap = win_rate - df_hist["Prob BENI"].mean()

# -----------------------------
# MODEL METRICS
# -----------------------------

# -----------------------------
# MODEL OVERVIEW
# -----------------------------

st.markdown("<h3 style='text-align:center'>Model Overview</h3>", unsafe_allow_html=True)

sp1,center,sp2 = st.columns([1,6,1])

with center:

    c1,c2,c3,c4,c5,c6,c7,c8,c9 = st.columns(9)

    c1.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">Matches</div>
    <div class="metric-value">{total_matches}</div>
    </div>
    """,unsafe_allow_html=True)

    c2.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">BTTS Win Rate</div>
    <div class="metric-value">{win_rate:.1f}%</div>
    </div>
    """,unsafe_allow_html=True)

    c3.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">Average Odds</div>
    <div class="metric-value">{df_hist['Cuota'].mean():.2f}</div>
    </div>
    """,unsafe_allow_html=True)

    c4.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">Avg Prob BENI</div>
    <div class="metric-value">{df_hist['Prob BENI'].mean():.1f}%</div>
    </div>
    """,unsafe_allow_html=True)

    c5.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">Average Edge</div>
    <div class="metric-value">{df_hist['EDGE'].mean():.2f}%</div>
    </div>
    """,unsafe_allow_html=True)

    c6.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">Calibration</div>
    <div class="metric-value">{model_gap:.2f}%</div>
    </div>
    """,unsafe_allow_html=True)

    c7.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">Leagues</div>
    <div class="metric-value">{df_hist['Liga'].nunique()}</div>
    </div>
    """,unsafe_allow_html=True)

    c8.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">Avg Goals</div>
    <div class="metric-value">{(df_hist['Home Goals']+df_hist['Away Goals']).mean():.2f}</div>
    </div>
    """,unsafe_allow_html=True)

    c9.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">Avg xG Projection</div>
    <div class="metric-value">{df_hist['xG Proyectado'].mean():.2f}</div>
    </div>
    """,unsafe_allow_html=True)

st.divider()

# -----------------------------
# HISTORIAL MODELO
# -----------------------------

st.header("BENI Model Dataset")

tabla = df_hist[
[
"Fecha",
"Liga",
"Partido",
"Resultado",
"Cuota",
"xG Proyectado",
"Prob Implícita",
"Prob BENI",
"EDGE",
"BTTS"
]
]

tabla["Cuota"] = tabla["Cuota"].map(lambda x:f"{x:.2f}")
tabla["xG Proyectado"] = tabla["xG Proyectado"].map(lambda x:f"{x:.2f}")
tabla["Prob Implícita"] = tabla["Prob Implícita"].map(lambda x:f"{x:.1f}%")
tabla["Prob BENI"] = tabla["Prob BENI"].map(lambda x:f"{x:.1f}%")
tabla["EDGE"] = tabla["EDGE"].map(lambda x:f"{x:.2f}%")

st.dataframe(tabla,use_container_width=True,height=700)

st.divider()

# -----------------------------
# LIGA PERFORMANCE
# -----------------------------

st.header("League Performance")

liga_stats = df_hist.groupby("Liga").agg(
BTTS_hits=("BTTS",lambda x:(x=="🟢").sum()),
Partidos=("BTTS","count")
).reset_index()

liga_stats["BTTS %"] = (liga_stats["BTTS_hits"]/liga_stats["Partidos"]*100).round(1)

fig_liga = px.bar(
liga_stats,
x="Liga",
y="BTTS %",
text="BTTS %"
)

st.plotly_chart(fig_liga,use_container_width=True)

st.divider()

# -----------------------------
# MODEL CALIBRATION
# -----------------------------

st.header("Model Calibration")

df_cal = df_hist.copy()

df_cal["BTTS_real"] = df_cal["BTTS"].apply(lambda x:1 if x=="🟢" else 0)

df_cal["prob_bin"] = pd.cut(df_cal["Prob BENI"],bins=5).astype(str)

calibration = df_cal.groupby("prob_bin").agg(
Predicted=("Prob BENI","mean"),
Real=("BTTS_real","mean")
).reset_index()

calibration["Real"] = calibration["Real"]*100

fig_cal = px.scatter(
calibration,
x="Predicted",
y="Real",
text="prob_bin"
)

fig_cal.update_traces(textposition="top center")

st.plotly_chart(fig_cal,use_container_width=True)

st.divider()

# -----------------------------
# ROLLING PERFORMANCE
# -----------------------------

st.header("Rolling Model Performance")

df_roll = df_hist.copy()

df_roll["BTTS_real"] = df_roll["BTTS"].apply(lambda x:1 if x=="🟢" else 0)

df_roll["Rolling Accuracy"] = df_roll["BTTS_real"].rolling(10).mean()*100

fig_roll = px.line(
df_roll,
y="Rolling Accuracy",
title="Rolling Prediction Accuracy (10 matches)"
)

st.plotly_chart(fig_roll,use_container_width=True)

st.divider()

# -----------------------------
# RESULTADOS COMUNES
# -----------------------------

st.header("Most Common Scorelines")

resultados = df_hist["Resultado"].value_counts().head(8)

df_resultados = resultados.reset_index()
df_resultados.columns = ["Resultado","Count"]

fig_result = px.bar(
df_resultados,
x="Count",
y="Resultado",
orientation="h",
text="Count"
)

st.plotly_chart(fig_result,use_container_width=True)