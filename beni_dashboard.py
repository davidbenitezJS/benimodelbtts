import streamlit as st
import pandas as pd
import os
import plotly.express as px

pd.options.display.float_format = "{:.2f}".format

st.set_page_config(page_title="BENI Football Model", layout="wide")

st.markdown(
    '<h1 class="center-title">⚽ BENI Football Model Dashboard</h1>',
    unsafe_allow_html=True
)

st.divider()
st.divider()

# -----------------------------
# FUNCIONES
# -----------------------------

def calcular_prob_beni(xg_home,xg_away,xga_home,xga_away,btts_home,btts_away):

    base = (
        (xg_home + xg_away) * 12 +
        (xga_home + xga_away) * 8 +
        (btts_home + btts_away) * 0.25
    )

    return min(base,95)

def calcular_categoria(xg_proj,xga_home,xga_away,btts_home,btts_away):

    if xg_proj>=3.5 and xga_home>=1.5 and xga_away>=1.5 and btts_home>=75 and btts_away>=75:
        return "SUPER BTTS"

    elif xg_proj>=3.2 and xga_home>=1.4 and xga_away>=1.4 and btts_home>=70 and btts_away>=70:
        return "PREMIUM BTTS BENI"

    elif xg_proj>=2.9 and xga_home>=1.3 and xga_away>=1.3 and btts_home>=63 and btts_away>=63:
        return "S+ BTTS"

    else:
        return "DESCARTADO"


# -----------------------------
# ANALIZADOR
# -----------------------------

st.header("Analizador BTTS")

col1,col2,col3 = st.columns(3)

with col1:
    axg_home = st.number_input("xG Home",step=0.01)

with col2:
    axg_away = st.number_input("xG Away",step=0.01)

with col3:
    acuota = st.number_input("Cuota",step=0.01)

col4,col5 = st.columns(2)

with col4:
    axga_home = st.number_input("xGA Home",step=0.01)

with col5:
    axga_away = st.number_input("xGA Away",step=0.01)

col6,col7 = st.columns(2)

with col6:
    abtts_home = st.number_input("BTTS Home %",step=1.0)

with col7:
    abtts_away = st.number_input("BTTS Away %",step=1.0)

if st.button("Analizar"):

    if acuota == 0 or axg_home == 0 or axg_away == 0 or axga_home == 0 or axga_away == 0 or abtts_home == 0 or abtts_away == 0:
        st.warning("Debes completar todos los campos antes de analizar.")

    else:

        xg_proj = ((axg_home + axga_away)/2 + (axg_away + axga_home)/2)

        prob_beni = calcular_prob_beni(
            axg_home,axg_away,
            axga_home,axga_away,
            abtts_home,abtts_away
        )

        prob_implicita = (1/acuota)*100
        edge = prob_beni - prob_implicita

        categoria = calcular_categoria(
            xg_proj,
            axga_home,axga_away,
            abtts_home,abtts_away
        )

        c1,c2,c3,c4 = st.columns(4)

        c1.metric("xG Proyectado",round(xg_proj,2))
        c2.metric("Prob BENI",f"{prob_beni:.1f}%")
        c3.metric("Prob Implícita",f"{prob_implicita:.1f}%")
        c4.metric("EDGE",f"{edge:.2f}%")

        st.success(f"Categoría: {categoria}")

    st.divider()
    st.divider()


# -----------------------------
# HISTORIAL DEL MODELO
# -----------------------------

st.header("BENI MODEL BTTS")

archivo = "beni_data.xlsx"

if os.path.exists(archivo):

    df_hist = pd.read_excel(archivo)

    df_hist = df_hist.sort_values("Fecha", ascending=False)

    df_hist["Partido"] = df_hist["Home"]+" vs "+df_hist["Away"]

    df_hist["Resultado"] = (
        df_hist["Home Goals"].astype(str)
        + "-"
        + df_hist["Away Goals"].astype(str)
    )

    df_hist["BTTS"] = df_hist.apply(
        lambda row:"🟢" if row["Home Goals"]>0 and row["Away Goals"]>0 else "🔴",
        axis=1
    )

    df_hist["xG Proyectado"] = (
        (df_hist["xG Home"]+df_hist["xGA Away"])/2 +
        (df_hist["xG Away"]+df_hist["xGA Home"])/2
    ).round(2)

    df_hist["Prob Implícita"] = (1/df_hist["Cuota"]*100).round(1)

    df_hist["Prob BENI"] = (
        df_hist["Prob Implícita"] + (df_hist["EDGE"]*100)
    ).round(1)

    df_hist["EDGE"] = (df_hist["EDGE"]*100).round(2)

    df_hist["Cuota"] = df_hist["Cuota"].round(2)

    ultimos = df_hist

    hits = (ultimos["BTTS"]=="🟢").sum()
    total = len(ultimos)

    porcentaje = (hits/total)*100

    tabla = ultimos[
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

    tabla["Cuota"] = tabla["Cuota"].map(lambda x: f"{x:.2f}")
    tabla["xG Proyectado"] = tabla["xG Proyectado"].map(lambda x: f"{x:.2f}")
    tabla["Prob Implícita"] = tabla["Prob Implícita"].map(lambda x: f"{x:.1f}%")
    tabla["Prob BENI"] = tabla["Prob BENI"].map(lambda x: f"{x:.1f}%")
    tabla["EDGE"] = tabla["EDGE"].map(lambda x: f"{x:.2f}%")

    st.dataframe(tabla, use_container_width=True, height=800)

    st.divider()

# -----------------------------
# MODEL METRICS
# -----------------------------

# -----------------------------
# MODEL METRICS
# -----------------------------

st.markdown(
"""
<style>
.center-title {
    text-align: center;
}
</style>
""",
unsafe_allow_html=True
)

st.markdown(
"<h3 class='center-title'>Model Metrics</h3>",
unsafe_allow_html=True
)

# -----------------------------
# CALCULOS MODELO
# -----------------------------

# -----------------------------
# CALCULOS MODELO
# -----------------------------

wins = (df_hist["BTTS"] == "🟢").sum()
losses = (df_hist["BTTS"] == "🔴").sum()

total_matches = wins + losses

porcentaje = (wins / total_matches) * 100 if total_matches > 0 else 0

model_gap = porcentaje - df_hist["Prob BENI"].mean()


spacer1, center, spacer2 = st.columns([1,4,1])

with center:

    m1, m2, m3, m4, m5, m6 = st.columns(6)

    with m1:
        st.markdown(f"""
        <div style="
            background-color:#111827;
            padding:20px;
            border-radius:12px;
            text-align:center;
            border:1px solid #1f2937;">
            <div style="font-size:14px;color:#9ca3af;">Matches Analyzed</div>
            <div style="font-size:34px;font-weight:700;">{total_matches}</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div style="
            background-color:#111827;
            padding:20px;
            border-radius:12px;
            text-align:center;
            border:1px solid #1f2937;">
            <div style="font-size:14px;color:#9ca3af;">BTTS Win Rate</div>
            <div style="font-size:34px;font-weight:700;">{porcentaje:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div style="
            background-color:#111827;
            padding:20px;
            border-radius:12px;
            text-align:center;
            border:1px solid #1f2937;">
            <div style="font-size:14px;color:#9ca3af;">Average Odds</div>
            <div style="font-size:34px;font-weight:700;">{df_hist['Cuota'].mean():.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div style="
            background-color:#111827;
            padding:20px;
            border-radius:12px;
            text-align:center;
            border:1px solid #1f2937;">
            <div style="font-size:14px;color:#9ca3af;">Average Prob BENI</div>
            <div style="font-size:34px;font-weight:700;">{df_hist['Prob BENI'].mean():.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with m5:
        st.markdown(f"""
        <div style="
            background-color:#111827;
            padding:20px;
            border-radius:12px;
            text-align:center;
            border:1px solid #1f2937;">
            <div style="font-size:14px;color:#9ca3af;">Average EDGE</div>
            <div style="font-size:34px;font-weight:700;">{df_hist['EDGE'].mean():.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with m6:
        st.markdown(f"""
        <div style="
            background-color:#111827;
            padding:20px;
            border-radius:12px;
            text-align:center;
            border:1px solid #1f2937;">
            <div style="font-size:14px;color:#9ca3af;">Model Calibration</div>
            <div style="font-size:34px;font-weight:700;">{model_gap:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)


    st.divider()


    # -----------------------------
    # ANALISIS POR LIGA
    # -----------------------------

    st.header("Rendimiento de Ligas")

    liga_stats = df_hist.groupby("Liga").agg(
        BTTS_hits=("BTTS", lambda x: (x=="🟢").sum()),
        Partidos=("BTTS","count"),
        Cuota_promedio=("Cuota","mean"),
        ProbBENI_prom=("Prob BENI","mean"),
        Edge_prom=("EDGE","mean")
    ).reset_index()

    liga_stats["BTTS %"] = (liga_stats["BTTS_hits"] / liga_stats["Partidos"] * 100).round(1)

    liga_stats = liga_stats.sort_values("BTTS %", ascending=False)

    fig_liga = px.bar(
        liga_stats,
        x="Liga",
        y="BTTS %",
        text="BTTS %",

    )

    fig_liga.update_layout(
    xaxis_title="LIGAS ANALIZADAS",
    yaxis_title="BTTS %",
    
    xaxis_title_font=dict(size=20),
    yaxis_title_font=dict(size=20),

    font=dict(size=25),

)

    st.plotly_chart(fig_liga, use_container_width=True)

    # -----------------------------
    # TABLA POR LIGA
    # -----------------------------

    st.subheader("Analisis completo por Liga")

    tabla_ligas = liga_stats[
    ["Liga","BTTS %","Partidos","Cuota_promedio","ProbBENI_prom","Edge_prom"]
    ]

    tabla_ligas = tabla_ligas.rename(columns={
    "Cuota_promedio": "Cuota promedio",
    "ProbBENI_prom": "BENI BTTS promedio",
    "Edge_prom": "Edge promedio"
    })

    tabla_ligas["BTTS %"] = tabla_ligas["BTTS %"].map(lambda x: f"{x:.1f}%")
    tabla_ligas["BENI BTTS promedio"] = tabla_ligas["BENI BTTS promedio"].map(lambda x: f"{x:.1f}%")
    tabla_ligas["Edge promedio"] = tabla_ligas["Edge promedio"].map(lambda x: f"{x:.2f}%")

    st.dataframe(tabla_ligas, use_container_width=True)


    st.divider()
    st.divider()


# -----------------------------
# MODEL CALIBRATION
# -----------------------------

st.header("Model Calibration")

df_cal = df_hist.copy()

df_cal["BTTS_real"] = df_cal["BTTS"].apply(lambda x: 1 if x == "🟢" else 0)

df_cal["prob_bin"] = pd.cut(df_cal["Prob BENI"], bins=5).astype(str)

calibration = df_cal.groupby("prob_bin").agg(
    Predicted=("Prob BENI","mean"),
    Real=("BTTS_real","mean")
).reset_index()

calibration["Real"] = calibration["Real"] * 100

fig_cal = px.scatter(
    calibration,
    x="Predicted",
    y="Real",
    text="prob_bin"
)

fig_cal.update_traces(textposition="top center")

fig_cal.update_layout(
    xaxis_title="Predicted Probability BENI (%)",
    yaxis_title="Real BTTS %",
    font=dict(size=16)
)

st.plotly_chart(fig_cal, use_container_width=True)



# -----------------------------
# RESULTADOS MAS COMUNES
# -----------------------------

st.markdown(
"<h3 class='center-title'>Resultados comunes</h3>",
unsafe_allow_html=True
)

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

fig_result.update_layout(
    xaxis_title="Frequency",
    yaxis_title="Scoreline",
    xaxis_title_font=dict(size=20),
    yaxis_title_font=dict(size=20),
    font=dict(size=16),
    height=400
)

st.plotly_chart(fig_result, use_container_width=True)