import re
import html
import math
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


st.set_page_config(
    page_title="Dashboard Fundação Pão dos Pobres",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --fp-bg: #FFFFFF;
        --fp-card: #FFFFFF;
        --fp-surface: #F8FAFF;
        --fp-ink: #1F2937;
        --fp-muted: #6B7280;
        --fp-line: #D7E3F4;
        --fp-accent: #2563EB;
        --fp-accent-soft: #DBEAFE;
        --fp-pink: #EC4899;
        --fp-pink-soft: #FCE7F3;
    }

    .stApp {
        background: var(--fp-bg);
        color: var(--fp-ink);
    }

    div.block-container {
        padding-top: 0.9rem;
        padding-bottom: 6rem;
    }

    h1, h2, h3, h4, p, label, span, div {
        color: var(--fp-ink);
    }

    header[data-testid="stHeader"] {
        background: #FFFFFF;
        border-bottom: 1px solid var(--fp-line);
        position: relative;
    }

    header[data-testid="stHeader"]::before {
        content: "";
        position: absolute;
        left: 1rem;
        top: 0.85rem;
        font-size: 1rem;
        font-weight: 700;
        color: var(--fp-ink);
    }

    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"] {
        background: #FFFFFF;
    }

    div[data-testid="stToolbar"] {
        display: none;
    }

    section[data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid var(--fp-line);
        overflow-y: auto;
    }

    section[data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 15.5rem !important;
        max-width: 15.5rem !important;
    }

    section[data-testid="stSidebar"][aria-expanded="false"] {
        min-width: 15.5rem !important;
        max-width: 15.5rem !important;
        transform: translateX(0) !important;
        margin-left: 0 !important;
    }

    section[data-testid="stSidebar"][aria-expanded="false"] > div {
        width: 15.5rem !important;
    }

    section[data-testid="stSidebar"] > div {
        background: #FFFFFF;
    }

    section[data-testid="stSidebar"] * {
        color: var(--fp-ink) !important;
    }

    section[data-testid="stSidebar"] .stRadio label {
        font-weight: 600;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        border-radius: 12px;
        padding: 0.45rem 0.65rem;
        border: 1px solid transparent;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background-color: var(--fp-pink-soft);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-selected="true"] {
        background: var(--fp-accent-soft);
        border-color: #93C5FD;
    }

    [data-testid="stWidgetLabel"] * {
        color: var(--fp-ink) !important;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"] > div,
    div[data-testid="stDateInput"] > div,
    div[data-testid="stDateInput"] [data-baseweb="input"] > div {
        background: #FFFFFF;
        border-color: var(--fp-line);
        color: var(--fp-ink);
        border-radius: 20px;
        min-height: 56px;
        box-shadow: inset 0 0 0 1px rgba(37, 99, 235, 0.04);
    }

    div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="base-input"] > div:focus-within,
    div[data-testid="stDateInput"] > div:focus-within,
    div[data-testid="stDateInput"] [data-baseweb="input"] > div:focus-within {
        border-color: #60A5FA;
        box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.16);
    }

    div[data-testid="stDateInput"] input,
    div[data-testid="stDateInput"] input:disabled,
    div[data-testid="stDateInput"] button,
    div[data-testid="stDateInput"] svg,
    div[data-testid="stDateInput"] path {
        color: var(--fp-ink) !important;
        fill: var(--fp-ink) !important;
        stroke: var(--fp-ink) !important;
        -webkit-text-fill-color: var(--fp-ink) !important;
        opacity: 1 !important;
    }

    .stMultiSelect div[data-baseweb="tag"],
    div[data-baseweb="tag"] {
        background: #FFFFFF !important;
        border: 1px solid #93C5FD !important;
        border-radius: 999px !important;
        padding: 0.28rem 0.72rem !important;
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.08);
    }

    .stMultiSelect div[data-baseweb="tag"] span,
    .stMultiSelect div[data-baseweb="tag"] svg,
    .stMultiSelect div[data-baseweb="tag"] path,
    .stMultiSelect div[data-baseweb="tag"] button,
    .stMultiSelect div[data-baseweb="tag"] button *,
    .stMultiSelect div[data-baseweb="tag"] p,
    .stMultiSelect div[data-baseweb="tag"] * ,
    div[data-baseweb="tag"] span,
    div[data-baseweb="tag"] svg,
    div[data-baseweb="tag"] path,
    div[data-baseweb="tag"] button,
    div[data-baseweb="tag"] button *,
    div[data-baseweb="tag"] p,
    div[data-baseweb="tag"] * {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
        stroke: #FFFFFF !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    .stMultiSelect input,
    .stMultiSelect textarea,
    .stMultiSelect [data-baseweb="select"] input,
    .stMultiSelect [data-baseweb="select"] textarea {
        color: #0F172A !important;
        fill: #0F172A !important;
        stroke: #0F172A !important;
        caret-color: #2563EB !important;
        -webkit-text-fill-color: #0F172A !important;
        background: transparent !important;
        opacity: 1 !important;
    }

    .stMultiSelect input::placeholder,
    .stMultiSelect textarea::placeholder,
    .stMultiSelect [data-baseweb="select"] input::placeholder,
    .stMultiSelect [data-baseweb="select"] textarea::placeholder {
        color: #64748B !important;
        -webkit-text-fill-color: #64748B !important;
        opacity: 1 !important;
    }

    .stMultiSelect [data-baseweb="select"] > div:focus-within {
        background: #F8FBFF !important;
    }

    div[data-baseweb="popover"] {
        background: #FFFFFF !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
    }

    div[data-baseweb="menu"],
    ul[role="listbox"],
    div[role="listbox"] {
        background: #FFFFFF !important;
        border: 1px solid #BFDBFE !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        padding: 0 !important;
        overflow: hidden !important;
    }

    .stMultiSelect [role="option"],
    .stMultiSelect [role="option"] *,
    div[data-baseweb="popover"] [role="option"],
    div[data-baseweb="popover"] [role="option"] *,
    div[data-baseweb="menu"] [role="option"],
    div[data-baseweb="menu"] [role="option"] *,
    ul[role="listbox"] [role="option"],
    ul[role="listbox"] [role="option"] *,
    div[role="listbox"] [role="option"],
    div[role="listbox"] [role="option"] * {
        color: #0F172A !important;
        fill: #0F172A !important;
        stroke: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        opacity: 1 !important;
    }

    div[data-baseweb="popover"] [role="option"],
    div[data-baseweb="menu"] [role="option"],
    ul[role="listbox"] [role="option"],
    div[role="listbox"] [role="option"] {
        background: #FFFFFF !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        min-height: auto !important;
        margin: 0 !important;
        padding: 0.7rem 0.9rem !important;
        line-height: 1.2 !important;
    }

    div[data-baseweb="popover"] [role="option"]:hover,
    div[data-baseweb="popover"] [role="option"][aria-selected="true"],
    div[data-baseweb="menu"] [role="option"]:hover,
    div[data-baseweb="menu"] [role="option"][aria-selected="true"],
    ul[role="listbox"] [role="option"]:hover,
    ul[role="listbox"] [role="option"][aria-selected="true"],
    div[role="listbox"] [role="option"]:hover,
    div[role="listbox"] [role="option"][aria-selected="true"] {
        background: #2563EB !important;
    }

    div[data-baseweb="popover"] [role="option"]:hover *,
    div[data-baseweb="popover"] [role="option"][aria-selected="true"] *,
    div[data-baseweb="menu"] [role="option"]:hover *,
    div[data-baseweb="menu"] [role="option"][aria-selected="true"] *,
    ul[role="listbox"] [role="option"]:hover *,
    ul[role="listbox"] [role="option"][aria-selected="true"] *,
    div[role="listbox"] [role="option"]:hover *,
    div[role="listbox"] [role="option"][aria-selected="true"] * {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
        stroke: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    div[data-baseweb="menu"] input,
    ul[role="listbox"] input,
    div[role="listbox"] input {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        background: #FFFFFF !important;
        border: none !important;
        box-shadow: none !important;
    }

    div[data-testid="stMetric"],
    div[data-testid="stDataFrame"],
    div[data-testid="stPlotlyChart"],
    div[data-testid="stTable"] {
        background: var(--fp-card);
        border: 1px solid var(--fp-line);
        border-radius: 18px;
        padding: 0.75rem;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.08);
    }

    div[data-testid="stPlotlyChart"] {
        overflow: hidden;
    }

    div[data-testid="stPlotlyChart"] .js-plotly-plot,
    div[data-testid="stPlotlyChart"] .plot-container,
    div[data-testid="stPlotlyChart"] .svg-container {
        max-width: 100% !important;
    }

    div[data-testid="stDataFrame"],
    div[data-testid="stTable"] {
        background: #FFFFFF;
        max-width: 460px;
        margin: 0 auto;
    }

    div[data-testid="stDataFrame"] * ,
    div[data-testid="stTable"] * {
        color: var(--fp-ink) !important;
        background: #FFFFFF !important;
    }

    div[data-testid="stDataFrame"] table,
    div[data-testid="stTable"] table {
        font-size: 0.9rem;
    }

    .fp-hero {
        background: var(--fp-card);
        border: 1px solid var(--fp-line);
        border-left: 8px solid var(--fp-accent);
        border-radius: 22px;
        padding: 1rem 1.35rem 0.95rem 1.35rem;
        margin: 0 0 1.2rem 0;
        box-shadow: 0 10px 22px rgba(37, 99, 235, 0.08);
    }

    .fp-hero h1 {
        color: var(--fp-accent) !important;
        margin: 0;
    }

    .fp-hero p {
        color: var(--fp-muted) !important;
        margin: 0.55rem 0 0 0;
        font-size: 1rem;
        line-height: 1.45;
        max-width: 78ch;
    }

    .fp-hero-kicker {
        color: var(--fp-pink) !important;
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }

    .fp-hero::after {
        content: "";
        display: block;
        width: 120px;
        height: 4px;
        border-radius: 999px;
        background: var(--fp-pink);
        margin-top: 0.7rem;
    }

    .fp-kpi {
        background: var(--fp-card);
        border: 1px solid var(--fp-line);
        border-left: 7px solid var(--fp-accent);
        border-radius: 18px;
        padding: 1rem 1rem 0.9rem 1rem;
        min-height: 118px;
        margin-bottom: 1.35rem;
        box-shadow: 0 10px 24px rgba(37, 99, 235, 0.08);
    }

    .fp-kpi-label {
        color: var(--fp-muted);
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }

    .fp-kpi-value {
        color: var(--fp-ink);
        font-size: 1.65rem;
        font-weight: 800;
        line-height: 1.15;
        margin-bottom: 0.35rem;
    }

    .fp-kpi-help {
        color: var(--fp-muted);
        font-size: 0.88rem;
        line-height: 1.25;
    }

    .fp-note {
        background: var(--fp-surface);
        border: 1px solid var(--fp-line);
        border-radius: 16px;
        padding: 0.9rem 1rem;
        margin: 0.7rem 0 1rem 0;
    }

    .fp-note strong {
        color: var(--fp-pink);
    }

    .fp-nav {
        background: #FFFFFF;
        border: 1px solid var(--fp-line);
        border-radius: 18px;
        padding: 0.8rem 1rem;
        margin: 0 0 1rem 0;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.06);
    }

    .fp-table-card {
        background: #FFFFFF;
        border: 1px solid var(--fp-line);
        border-radius: 22px;
        padding: 0.9rem 1rem;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.08);
    }

    .fp-section-title {
        color: var(--fp-ink);
        font-size: 1.12rem;
        font-weight: 800;
        line-height: 1.2;
        margin: 0 0 0.9rem 0;
    }

    .fp-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.95rem;
    }

    .fp-table thead th {
        text-align: left;
        color: var(--fp-accent);
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        padding: 0.8rem 0.7rem;
        border-bottom: 1px solid var(--fp-line);
        background: #EEF4FF;
    }

    .fp-table tbody td {
        padding: 0.78rem 0.7rem;
        border-bottom: 1px solid #EAF1FB;
        color: var(--fp-ink);
    }

    .fp-table tbody tr:last-child td {
        border-bottom: none;
    }

    .fp-table tbody tr:nth-child(even) td {
        background: #FBFDFF;
    }

    .fp-table-rank {
        width: 56px;
        text-align: center;
        font-weight: 700;
        color: var(--fp-pink);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

px.defaults.template = "plotly_white"

MESES_ORDEM = [
    "JAN", "FEV", "MAR", "ABR", "MAI", "JUN",
    "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"
]


PALETA_FUNDAÇÃO = ["#2563EB", "#EC4899", "#60A5FA", "#F472B6", "#1D4ED8", "#DB2777", "#93C5FD", "#F9A8D4"]
px.defaults.color_discrete_sequence = PALETA_FUNDAÇÃO


def formatar_numero(valor):
    try:
        return f"{float(valor):,.0f}".replace(",", ".")
    except Exception:
        return str(valor)


def formatar_decimal(valor, casas=1):
    try:
        return f"{float(valor):.{casas}f}".replace(".", ",")
    except Exception:
        return str(valor)


def kpi_card(label, valor, apoio=""):
    st.markdown(
        f"""
        <div class="fp-kpi">
            <div class="fp-kpi-label">{label}</div>
            <div class="fp-kpi-value">{valor}</div>
            <div class="fp-kpi-help">{apoio}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def aplicar_layout_figura(fig, altura=None):
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#1F2937", family="Arial"),
        title=dict(font=dict(size=20, color="#1F2937")),
        legend=dict(
            bgcolor="rgba(255,255,255,0)",
            title_font=dict(color="#1F2937"),
            font=dict(color="#1F2937"),
        ),
        margin=dict(l=32, r=24, t=74, b=48),
    )
    fig.update_xaxes(
        gridcolor="#E5EEF9",
        zerolinecolor="#D7E3F4",
        tickfont=dict(color="#1F2937"),
        title_font=dict(color="#1F2937"),
        automargin=True,
    )
    fig.update_yaxes(
        gridcolor="#E5EEF9",
        zerolinecolor="#D7E3F4",
        tickfont=dict(color="#1F2937"),
        title_font=dict(color="#1F2937"),
        automargin=True,
    )
    fig.update_annotations(font=dict(color="#1F2937"))
    try:
        fig.update_coloraxes(
            colorbar=dict(
                bgcolor="#FFFFFF",
                tickfont=dict(color="#1F2937"),
                title=dict(font=dict(color="#1F2937")),
            )
        )
    except Exception:
        pass
    for trace in fig.data:
        try:
            trace.update(
                colorbar=dict(
                    bgcolor="#FFFFFF",
                    tickfont=dict(color="#1F2937"),
                    title=dict(font=dict(color="#1F2937")),
                )
            )
        except Exception:
            pass
        if getattr(trace, "type", "") == "treemap":
            trace.update(textfont=dict(color="#1F2937", size=13))
        if getattr(trace, "type", "") == "sankey":
            trace.update(textfont=dict(color="#1F2937", size=13))
    if altura is not None:
        fig.update_layout(height=altura)
    return fig

CAMINHOS_DADOS = [
    Path("dados_tratados/lem_consolidado_2021_2025.csv"),
    Path("lem_consolidado_2021_2025.csv"),
    Path("../dados_tratados/lem_consolidado_2021_2025.csv"),
    Path("../lem_consolidado_2021_2025.csv"),
]


def normalizar_texto(valor):
    return str(valor).lower().strip()


@st.cache_data
def carregar_dados():
    caminho_encontrado = None
    for caminho in CAMINHOS_DADOS:
        if caminho.exists():
            caminho_encontrado = caminho
            break

    if caminho_encontrado is None:
        st.error(
            "Arquivo de dados não encontrado. Coloque o CSV em "
            "dados_tratados/lem_consolidado_2021_2025.csv ou na mesma pasta do app.py."
        )
        st.stop()

    df = pd.read_csv(caminho_encontrado)

    colunas_obrigatorias = ["ano", "mes", "valor"]
    colunas_faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
    if colunas_faltantes:
        st.error(f"Colunas obrigatórias ausentes no CSV: {colunas_faltantes}")
        st.stop()

    for coluna in ["categoria", "subcategoria", "indicador", "indicador_completo"]:
        if coluna not in df.columns:
            df[coluna] = ""

    if "mes_numero" not in df.columns:
        mapa_meses = {mes: i + 1 for i, mes in enumerate(MESES_ORDEM)}
        df["mes_numero"] = df["mes"].astype(str).str.upper().map(mapa_meses)

    if "data" not in df.columns:
        df["data"] = pd.to_datetime(
            df["ano"].astype(str) + "-" + df["mes_numero"].astype(int).astype(str) + "-01",
            errors="coerce"
        )
    else:
        df["data"] = pd.to_datetime(df["data"], errors="coerce")

    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
    df["mes"] = df["mes"].astype(str).str.upper().str.strip()
    df["indicador_completo"] = df["indicador_completo"].fillna(df["indicador"]).astype(str)

    return df


def texto_linha(linha):
    return " ".join([
        str(linha.get("categoria", "")),
        str(linha.get("subcategoria", "")),
        str(linha.get("indicador", "")),
        str(linha.get("indicador_completo", "")),
    ]).lower()


def contem_palavras(linha, palavras):
    texto = texto_linha(linha)
    return any(palavra in texto for palavra in palavras)


def aplicar_filtro_anos(df, label="Anos"):
    anos = sorted([int(a) for a in df["ano"].dropna().unique()])
    if not anos:
        return df, []
    anos_selecionados = st.multiselect(label, anos, default=anos)
    if not anos_selecionados:
        return df.iloc[0:0].copy(), []
    return df[df["ano"].isin(anos_selecionados)].copy(), anos_selecionados


def aplicar_filtro_periodo_mensal(df):
    if df["data"].dropna().empty:
        return df

    data_min = df["data"].min().date()
    data_max = df["data"].max().date()

    return df




def criar_heatmap_mensal(df_mensal, titulo):
    anos = sorted([int(a) for a in df_mensal["ano"].dropna().unique()], reverse=True)

    grade = pd.MultiIndex.from_product(
        [anos, range(1, 13)],
        names=["ano", "mes_numero"]
    ).to_frame(index=False)
    grade["mes"] = grade["mes_numero"].map({i + 1: mes for i, mes in enumerate(MESES_ORDEM)})

    completo = grade.merge(
        df_mensal[["ano", "mes_numero", "total"]],
        on=["ano", "mes_numero"],
        how="left"
    ).fillna({"total": 0})

    matriz = completo.pivot(index="ano", columns="mes", values="total").reindex(
        index=anos,
        columns=MESES_ORDEM,
    )

    fig = go.Figure(
        data=go.Heatmap(
            z=matriz.values,
            x=MESES_ORDEM,
            y=[str(a) for a in anos],
            colorscale=[
                [0.0, "#0B4F9E"],
                [0.5, "#4C9BE8"],
                [1.0, "#E6F2FF"],
            ],
            colorbar=dict(title="Registros", thickness=18, bgcolor="#FFFFFF"),
            hovertemplate="Ano: %{y}<br>Mês: %{x}<br>Registros: %{z}<extra></extra>",
        )
    )
    fig.update_layout(
        title=titulo,
        height=max(420, 90 * len(anos)),
        xaxis_title="Mês",
        yaxis_title="Ano",
    )
    fig.update_xaxes(type="category", categoryorder="array", categoryarray=MESES_ORDEM)
    fig.update_yaxes(type="category", categoryorder="array", categoryarray=[str(a) for a in anos])
    return fig


def escapar_texto_css(texto):
    return str(texto).replace("\\", "\\\\").replace('"', '\\"')


def atualizar_titulo_topo(titulo):
    st.markdown(
        f"""
        <style>
        header[data-testid="stHeader"]::before {{
            content: "{escapar_texto_css(titulo)}";
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def quebrar_titulo(texto, limite=30):
    palavras = str(texto).split()
    if not palavras:
        return str(texto)

    linhas = []
    linha_atual = palavras[0]
    for palavra in palavras[1:]:
        candidato = f"{linha_atual} {palavra}"
        if len(candidato) <= limite:
            linha_atual = candidato
        else:
            linhas.append(linha_atual)
            linha_atual = palavra
    linhas.append(linha_atual)
    return "<br>".join(linhas)


def formatar_rotulo_pagina(chave):
    return PAGINAS_INFO[chave]["titulo"]


def renderizar_cabecalho_pagina(titulo):
    st.markdown(
        f"""
        <div class="fp-hero">
            <h1>{html.escape(titulo)}</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )


def renderizar_tabela_ranking(df_tabela, titulo="Meses com maior sobrecarga"):
    if df_tabela.empty:
        st.info("Nenhum registro encontrado para os filtros atuais.")
        return

    linhas = []
    for posicao, (_, linha) in enumerate(df_tabela.iterrows(), start=1):
        linhas.append(
            (
                f'<tr>'
                f'<td class="fp-table-rank">{posicao}</td>'
                f'<td>{html.escape(str(int(linha["ano"])))}</td>'
                f'<td>{html.escape(str(linha["mes"]))}</td>'
                f'<td>{formatar_numero(linha["total"])}</td>'
                f'</tr>'
            )
        )

    tabela_html = (
        '<div class="fp-table-card">'
        f'<div class="fp-section-title">{html.escape(titulo)}</div>'
        '<table class="fp-table">'
        '<thead><tr>'
        '<th class="fp-table-rank">#</th>'
        '<th>Ano</th>'
        '<th>Mês</th>'
        '<th>Registros</th>'
        '</tr></thead>'
        f'<tbody>{"".join(linhas)}</tbody>'
        '</table>'
        '</div>'
    )
    st.markdown(tabela_html, unsafe_allow_html=True)

def mostrar_metricas_basicas(df):
    total = int(df["valor"].sum()) if len(df) > 0 else 0
    qtd_indicadores = df["indicador_completo"].nunique() if "indicador_completo" in df.columns else 0
    anos = df["ano"].nunique() if "ano" in df.columns else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Volume total", f"{total:,.0f}".replace(",", "."))
    c2.metric("Indicadores", qtd_indicadores)
    c3.metric("Anos no filtro", anos)



def mostrar_metricas_demanda(df):
    total = int(df["valor"].sum()) if len(df) > 0 else 0
    indicador_top = "Sem dados"
    mes_pico = "Sem dados"
    media_mensal = 0

    if len(df) > 0:
        por_indicador = df.groupby("indicador_completo")["valor"].sum().sort_values(ascending=False)
        if not por_indicador.empty:
            indicador_top = por_indicador.index[0]

        por_mes = (
            df.groupby(["ano", "mes_numero", "mes"], as_index=False)
            .agg(total=("valor", "sum"))
            .sort_values("total", ascending=False)
        )
        if len(por_mes) > 0:
            pico = por_mes.iloc[0]
            mes_pico = f"{pico['mes']} de {int(pico['ano'])}"
            media_mensal = por_mes["total"].mean()

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Atendimentos registrados", formatar_numero(total), "Soma dos valores dos indicadores filtrados.")
    with c2:
        kpi_card("Mês de maior sobrecarga", mes_pico, f"Média mensal filtrada: {formatar_numero(media_mensal)} registros.")
    with c3:
        kpi_card("Indicador mais demandado", indicador_top, "Maior volume acumulado no recorte atual.")



def mostrar_metricas_desdobramentos(df, anos):
    total = int(df["valor"].sum()) if len(df) > 0 else 0
    principal = "Sem dados"
    pico = "Sem dados"
    concentracao = "Sem dados"

    if len(df) > 0:
        por_tipo = df.groupby("indicador_completo")["valor"].sum().sort_values(ascending=False)
        if not por_tipo.empty:
            principal = por_tipo.index[0]
            concentracao = f"{formatar_decimal((por_tipo.iloc[0] / total) * 100, 1)}% do total" if total > 0 else "Sem volume"

        por_mes = (
            df.groupby(["ano", "mes_numero", "mes"], as_index=False)
            .agg(total=("valor", "sum"))
            .sort_values("total", ascending=False)
        )
        if len(por_mes) > 0:
            top = por_mes.iloc[0]
            pico = f"{top['mes']} de {int(top['ano'])}"

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Registros técnicos", formatar_numero(total), "Volume acumulado dos desdobramentos selecionados.")
    with c2:
        kpi_card("Principal encaminhamento", principal, concentracao)
    with c3:
        kpi_card("Pico de demanda técnica", pico, "Mês com maior soma de registros técnicos.")



def mostrar_metricas_movimentacao(df):
    total = int(df["valor"].sum()) if len(df) > 0 else 0
    top_mov = "Sem dados"
    top_periodo = "Sem dados"
    if len(df) > 0:
        totais_mov = df.groupby("movimentacao")["valor"].sum()
        if not totais_mov.empty:
            top_mov = totais_mov.idxmax()
        totais_periodo = (
            df.groupby(["ano", "mes_numero", "mes"], as_index=False)
            .agg(total=("valor", "sum"))
            .sort_values("total", ascending=False)
        )
        if len(totais_periodo) > 0:
            top = totais_periodo.iloc[0]
            top_periodo = f"{top['mes']} de {int(top['ano'])}"

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Registros de movimentação", formatar_numero(total), "Entradas, permanências, saídas, evasões e desligamentos.")
    with c2:
        kpi_card("Movimento predominante", top_mov, "Tipo com maior volume no recorte atual.")
    with c3:
        kpi_card("Período crítico", top_periodo, "Mês com maior concentração de movimentações.")



def mostrar_metricas_estabilidade(df):
    permanencias = 0
    saidas_criticas = 0
    ano_maior_saida = "Sem dados"

    if len(df) > 0:
        totais = df.groupby("movimentacao")["valor"].sum()
        permanencias = int(totais.get("Permanência", 0))
        saidas_criticas = int(totais.get("Saída", 0) + totais.get("Evasão", 0) + totais.get("Desligamento", 0))

        anual = (
            df[df["movimentacao"].isin(["Saída", "Evasão", "Desligamento"])]
            .groupby("ano", as_index=False)
            .agg(total=("valor", "sum"))
            .sort_values("total", ascending=False)
        )
        if len(anual) > 0:
            ano_maior_saida = str(int(anual.iloc[0]["ano"]))

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Permanências registradas", formatar_numero(permanencias), "Registros ligados à continuidade no acolhimento.")
    with c2:
        kpi_card("Saídas críticas", formatar_numero(saidas_criticas), "Soma de saídas, evasões e desligamentos.")
    with c3:
        kpi_card("Ano com maior saída", ano_maior_saida, "Ano com maior volume de saídas críticas.")



def mostrar_metricas_q5(df):
    efetivos = int(df[df["grupo_analise"] == "Número de acolhidos"]["valor"].sum() if len(df) > 0 else 0)
    saude = int(df[df["grupo_analise"].isin(["Saúde mental", "Saúde clínica"])] ["valor"].sum() if len(df) > 0 else 0)
    educacao = int(df[df["grupo_analise"] == "Educação"]["valor"].sum() if len(df) > 0 else 0)

    taxa_saude = (saude / efetivos * 100) if efetivos > 0 else np.nan
    taxa_educacao = (educacao / efetivos * 100) if efetivos > 0 else np.nan

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Efetivos na casa", formatar_numero(efetivos), "Referência usada como proxy do volume de acolhidos.")
    with c2:
        apoio = f"{formatar_decimal(taxa_saude, 1)} registros a cada 100 efetivos" if not np.isnan(taxa_saude) else "Sem base de efetivos."
        kpi_card("Registros de saúde", formatar_numero(saude), apoio)
    with c3:
        apoio = f"{formatar_decimal(taxa_educacao, 1)} registros a cada 100 efetivos" if not np.isnan(taxa_educacao) else "Sem base de efetivos."
        kpi_card("Registros de educação", formatar_numero(educacao), apoio)



def mostrar_metricas_atividades(df, metrica):
    total = int(df["valor"].sum()) if len(df) > 0 else 0
    atividades = df["atividade"].nunique() if "atividade" in df.columns else 0
    principal = "Sem dados"
    if len(df) > 0:
        principal = df.groupby("atividade")["valor"].sum().idxmax()

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Eventos realizados", formatar_numero(total), "Soma dos eventos registrados em 2025.")
    with c2:
        kpi_card("Atividades distintas", atividades, "Número de eventos diferentes encontrados.")
    with c3:
        kpi_card("Evento mais recorrente", principal, "Atividade com maior volume acumulado.")



def classificar_desdobramento_tecnico(linha):
    texto = texto_linha(linha)

    # Evita misturar os indicadores de fluxo de acolhimento com os encaminhamentos técnicos.
    termos_movimentacao = [
        "efetivos na casa", "evas", "deslig", "novos ingressos", "transferências", "transferencias",
        "saída", "saida", "saídas", "saidas", "perman", "ativos"
    ]
    if any(t in texto for t in termos_movimentacao):
        return None

    termos_tecnicos = [
        "atendimento familiar", "atendimentos individual", "atendimento individual",
        "interface com judiciário", "interface com judiciario", "interface com educação",
        "interface com educacao", "interface com saúde", "interface com saude",
        "interface com rede socioassistencial", "documentação civil", "documentacao civil",
        "pias", "relatórios", "relatorios", "visitas domiciliares", "visita domiciliar",
        "reunião de equipe", "reuniao de equipe", "apadrinhamento afetivo",
        "família substituta", "familia substituta"
    ]
    if any(t in texto for t in termos_tecnicos):
        return linha.get("indicador_completo", "Desdobramento técnico")

    # Registros sem categoria que não forem movimento tendem a representar acompanhamento técnico na base.
    categoria = str(linha.get("categoria", "")).strip().lower()
    if categoria in ["", "nan", "none"]:
        return linha.get("indicador_completo", "Desdobramento técnico")

    return None

def classificar_movimentacao(linha):
    texto = texto_linha(linha)
    if any(p in texto for p in ["evas", "evad"]):
        return "Evasão"
    if any(p in texto for p in ["deslig"]):
        return "Desligamento"
    if any(p in texto for p in ["saída", "saida", "saidas", "saídas"]):
        return "Saída"
    if any(p in texto for p in ["entrada", "ingresso", "acolhido", "acolhidos", "acolhida"]):
        return "Entrada"
    if any(p in texto for p in ["perman", "permane", "efetivos na casa", "efetivo na casa", "continuidade"]):
        return "Permanência"
    return None


def classificar_grupo_q5(linha):
    texto = texto_linha(linha)
    if any(p in texto for p in [
        "efetivos na casa",
        "efetivo na casa",
    ]):
        return "Número de acolhidos"

    if any(p in texto for p in [
        "saúde mental",
        "saude mental",
    ]):
        return "Saúde mental"

    if any(p in texto for p in [
        "saúde clínica",
        "saude clinica",
        "saúde clinica",
        "saude clínica",
    ]):
        return "Saúde clínica"

    if any(p in texto for p in [
        "ensino eja",
        "ensino infantil",
        "ensino regular",
        "scfv",
        "educação",
        "educacao",
        "escola",
        "escolar",
        "matriculados",
        "matriculado",
        "aguardando vaga",
        "reforço escolar",
        "reforco escolar",
        "psicopedagoga",
        "trabalho educativo",
    ]):
        return "Educação"

    return None


def classificar_tipo_atividade_q6(linha):
    texto = texto_linha(linha)
    if any(p in texto for p in ["cultura", "cultural", "oficina", "passeio", "evento cultural"]):
        return "Atividades culturais"
    if any(p in texto for p in ["capacitação", "capacitacao", "formação", "formacao", "treinamento", "curso"]):
        return "Capacitações"
    if any(p in texto for p in ["ação institucional", "acao institucional", "ações institucionais", "acoes institucionais", "institucional"]):
        return "Ações institucionais"
    return None


def classificar_metrica_q6(linha):
    texto = texto_linha(linha)
    if any(p in texto for p in ["participante", "participantes", "público", "publico", "pessoas"]):
        return "Número de Participantes"
    if any(p in texto for p in ["carga horária", "carga horaria", "horas", "hora"]):
        return "Carga Horária Total"
    if any(p in texto for p in ["evento", "eventos", "realizado", "realizados", "encaminhados", "inseridos", "curso", "oficina"]):
        return "Quantidade de Eventos Realizados"
    return "Quantidade de Eventos Realizados"


# geral

df = carregar_dados()

PAGINAS_INFO = {
    "1. Evolução da demanda e sobrecarga": {
        "titulo": "Evolução da demanda e sobrecarga",
        "subtitulo": "Acompanhe a evolução mensal dos atendimentos e identifique os momentos de maior concentração de demanda.",
    },
    "2. Desdobramentos técnicos": {
        "titulo": "Desdobramentos técnicos",
        "subtitulo": "Veja quais encaminhamentos e interfaces técnicas concentram mais registros ao longo do período analisado.",
    },
    "3. Padrões sazonais e movimentação": {
        "titulo": "Padrões sazonais e movimentação",
        "subtitulo": "Analise entradas, saídas, evasões, desligamentos e permanências para destacar períodos mais críticos.",
    },
    "4. Estabilidade da permanência": {
        "titulo": "Estabilidade da permanência",
        "subtitulo": "Observe a composição das movimentações institucionais e o peso relativo de permanência, entradas e saídas críticas.",
    },
    "5. Acolhidos, saúde e educação": {
        "titulo": "Acolhidos, saúde e educação",
        "subtitulo": "Compare o volume de efetivos na casa com os registros de saúde e educação para enxergar a pressão de atendimento.",
    },
    "6. Eventos realizados em 2025": {
        "titulo": "Eventos realizados em 2025",
        "subtitulo": "Entenda quais eventos foram mais realizados em 2025 e como eles se distribuíram ao longo dos meses.",
    },
}

st.sidebar.markdown("### Dashboards")
pagina = st.sidebar.radio(
    "Dashboard",
    list(PAGINAS_INFO.keys()),
    format_func=formatar_rotulo_pagina,
    label_visibility="collapsed",
)

pagina_info = PAGINAS_INFO[pagina]
atualizar_titulo_topo("Dashboard Fundação Pão dos Pobres")
renderizar_cabecalho_pagina(pagina_info["titulo"])

# Dashboard 1 — Pergunta 1

if pagina == "1. Evolução da demanda e sobrecarga":
    st.markdown("### Filtros")
    df_dash, anos_selecionados = aplicar_filtro_anos(df, "Anos")

    categorias = sorted(df_dash["categoria"].dropna().astype(str).unique())
    categorias = [c for c in categorias if c not in ["", "None", "nan"]]
    categorias_selecionadas = st.multiselect(
        "Categorias",
        categorias,
        default=categorias,
    )
    if categorias_selecionadas:
        df_dash = df_dash[df_dash["categoria"].astype(str).isin(categorias_selecionadas)].copy()

    mostrar_metricas_demanda(df_dash)

    indicadores_disponiveis = sorted(df_dash["indicador_completo"].dropna().unique())
    indicadores_padrao = indicadores_disponiveis[:8]
    indicadores_selecionados = st.multiselect(
        "Indicadores",
        indicadores_disponiveis,
        default=indicadores_padrao,
    )

    df_q1 = df_dash[df_dash["indicador_completo"].isin(indicadores_selecionados)].copy()

    if len(df_q1) > 0:
        df_q1_linha = (
            df_q1.groupby(["ano", "mes_numero", "mes", "indicador_completo"], as_index=False)
            .agg(valor=("valor", "sum"))
            .sort_values(["indicador_completo", "ano", "mes_numero"])
        )

        ordem_meses = [
            "JAN", "FEV", "MAR", "ABR", "MAI", "JUN",
            "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"
        ]

        indicadores_ordenados = sorted(df_q1_linha["indicador_completo"].dropna().unique())
        anos_ordenados = sorted(df_q1_linha["ano"].dropna().unique())
        grade_completa = pd.MultiIndex.from_product(
            [indicadores_ordenados, anos_ordenados, range(1, 13)],
            names=["indicador_completo", "ano", "mes_numero"],
        ).to_frame(index=False)
        grade_completa["mes"] = grade_completa["mes_numero"].map({i + 1: mes for i, mes in enumerate(ordem_meses)})

        df_q1_linha = (
            grade_completa.merge(
                df_q1_linha[["ano", "mes_numero", "mes", "indicador_completo", "valor"]],
                on=["indicador_completo", "ano", "mes_numero", "mes"],
                how="left",
            )
            .fillna({"valor": 0})
            .sort_values(["indicador_completo", "ano", "mes_numero"])
        )
        df_q1_linha["ano_label"] = df_q1_linha["ano"].astype(int).astype(str)

        fig = px.line(
            df_q1_linha,
            x="mes",
            y="valor",
            color="ano_label",
            facet_col="indicador_completo",
            facet_col_wrap=2,
            facet_col_spacing=0.08,
            facet_row_spacing=0.09,
            markers=True,
            title="Evolução mensal dos atendimentos por indicador",
            labels={
                "mes": "Mês",
                "valor": "Registros de atendimento",
                "ano_label": "Ano",
                "indicador_completo": "Indicador",
            },
            hover_data={
                "ano": True,
                "mes": True,
                "valor": True,
                "indicador_completo": True,
            },
            category_orders={
                "mes": ordem_meses,
                "ano_label": [str(int(a)) for a in anos_ordenados],
                "indicador_completo": indicadores_ordenados,
            },
        )

        fig.for_each_annotation(
            lambda a: a.update(
                text=quebrar_titulo(a.text.split("=")[-1], 34),
                font=dict(size=14, color="#1F2937"),
                yshift=-4,
            )
        )

        fig.update_xaxes(
            categoryorder="array",
            categoryarray=ordem_meses,
            tickmode="array",
            tickvals=ordem_meses,
            ticktext=ordem_meses,
            showticklabels=True,
            matches=None,
            type="category",
            tickangle=0,
        )

        fig.update_yaxes(title_text="Registros de atendimento", rangemode="tozero")

        linhas_facetas = max(1, math.ceil(len(indicadores_ordenados) / 2))
        altura_figura = 260 + (linhas_facetas * 290)

        fig.update_layout(
            height=altura_figura,
            legend_title_text="",
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.12,
                xanchor="center",
                x=0.5,
            ),
            title=dict(
                x=0.01,
                y=0.995,
                yanchor="top",
                pad=dict(b=0),
            ),
            margin=dict(t=72, b=86),
        )
        aplicar_layout_figura(fig)
        fig.update_layout(
            margin=dict(t=72, b=86),
            title=dict(
                x=0.01,
                y=0.995,
                yanchor="top",
                pad=dict(b=0),
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns([1.45, 1.05])
        with c1:
            df_heat = (
                df_q1.groupby(["ano", "mes_numero", "mes"], as_index=False)
                .agg(total=("valor", "sum"))
                .sort_values(["ano", "mes_numero"])
            )
            fig_heat = criar_heatmap_mensal(df_heat, "Heatmap de sobrecarga mensal")
            aplicar_layout_figura(fig_heat)
            st.plotly_chart(fig_heat, use_container_width=True)

        with c2:
            ranking = df_heat.sort_values("total", ascending=False).head(10)
            renderizar_tabela_ranking(ranking[["ano", "mes", "total"]], "Meses com maior sobrecarga")
    else:
        st.info("Selecione pelo menos um indicador para visualizar esta análise.")

# Dashboard 2 — Pergunta 2

elif pagina == "2. Desdobramentos técnicos":
    st.markdown("### Filtros")
    df_filtrado, anos_selecionados = aplicar_filtro_anos(df, "Anos")

    df_desdobramentos = df_filtrado.copy()
    df_desdobramentos["desdobramento_tecnico"] = df_desdobramentos.apply(classificar_desdobramento_tecnico, axis=1)
    df_desdobramentos = df_desdobramentos[df_desdobramentos["desdobramento_tecnico"].notna()].copy()
    df_desdobramentos["indicador_completo"] = df_desdobramentos["desdobramento_tecnico"].astype(str)

    tipos = sorted(df_desdobramentos["indicador_completo"].dropna().unique())
    top_tipos = (
        df_desdobramentos.groupby("indicador_completo", as_index=False)
        .agg(total=("valor", "sum"))
        .sort_values("total", ascending=False)
        .head(8)["indicador_completo"]
        .tolist()
    )
    tipos_selecionados = st.multiselect("Tipos de desdobramento", tipos, default=top_tipos)
    df_q2 = df_desdobramentos[df_desdobramentos["indicador_completo"].isin(tipos_selecionados)].copy()

    mostrar_metricas_desdobramentos(df_q2, anos_selecionados)

    if len(df_q2) > 0:
        df_q2_linha = (
            df_q2.groupby(["data", "ano", "mes", "indicador_completo"], as_index=False)
            .agg(valor=("valor", "sum"))
            .sort_values("data")
        )
        fig = px.line(
            df_q2_linha,
            x="data",
            y="valor",
            color="indicador_completo",
            markers=True,
            title="Evolução dos tipos de desdobramentos técnicos",
            labels={"data": "Período", "valor": "Registros técnicos", "indicador_completo": "Tipo de desdobramento"},
            hover_data={"ano": True, "mes": True, "valor": True},
        )
        fig.update_layout(xaxis_title="Ano")
        fig.update_xaxes(tickformat="%Y", dtick="M12")
        fig.update_layout(height=600, hovermode="x unified")
        aplicar_layout_figura(fig)
        st.plotly_chart(fig, use_container_width=True)

        anual_heat = (
            df_q2.groupby(["ano", "indicador_completo"], as_index=False)
            .agg(registros_tecnicos=("valor", "sum"))
        )

        if len(anual_heat) > 0:
            ordem_tipos = (
                anual_heat.groupby("indicador_completo")["registros_tecnicos"]
                .sum()
                .sort_values(ascending=True)
                .index
                .tolist()
            )
            fig_heat_tecnico = px.density_heatmap(
                anual_heat,
                x="ano",
                y="indicador_completo",
                z="registros_tecnicos",
                histfunc="sum",
                color_continuous_scale=[
                    [0.0, "#DBEAFE"],
                    [0.45, "#60A5FA"],
                    [0.75, "#2563EB"],
                    [1.0, "#EC4899"],
                ],
                title="Mapa de concentração dos desdobramentos por ano",
                labels={
                    "ano": "Ano",
                    "indicador_completo": "Tipo de desdobramento",
                    "registros_tecnicos": "Registros técnicos",
                },
                category_orders={"indicador_completo": ordem_tipos},
            )
            fig_heat_tecnico.update_xaxes(
                tickmode="array",
                tickvals=sorted(anual_heat["ano"].dropna().unique()),
                ticktext=[str(int(a)) for a in sorted(anual_heat["ano"].dropna().unique())],
            )
            fig_heat_tecnico.update_coloraxes(
                colorbar=dict(title="Registros técnicos")
            )
            aplicar_layout_figura(fig_heat_tecnico, 620)
            st.plotly_chart(fig_heat_tecnico, use_container_width=True)

        top_acumulado = (
            df_q2.groupby("indicador_completo", as_index=False)
            .agg(registros_tecnicos=("valor", "sum"))
            .sort_values("registros_tecnicos", ascending=False)
            .head(10)
        )
        fig_top_tecnico = px.bar(
            top_acumulado,
            x="registros_tecnicos",
            y="indicador_completo",
            orientation="h",
            title="Desdobramentos técnicos mais recorrentes no período",
            labels={"registros_tecnicos": "Registros técnicos", "indicador_completo": "Tipo de desdobramento"},
        )
        fig_top_tecnico.update_layout(yaxis={"categoryorder": "total ascending"})
        aplicar_layout_figura(fig_top_tecnico, 560)
        st.plotly_chart(fig_top_tecnico, use_container_width=True)
    else:
        st.info("Nenhum desdobramento técnico encontrado para os filtros selecionados.")

# Dashboard 3 — Pergunta 3

elif pagina == "3. Padrões sazonais e movimentação":
    df_mov = df.copy()
    df_mov["movimentacao"] = df_mov.apply(classificar_movimentacao, axis=1)
    df_mov = df_mov[df_mov["movimentacao"].notna()].copy()

    st.markdown("### Filtros")
    df_mov = aplicar_filtro_periodo_mensal(df_mov)
    df_mov, anos_selecionados = aplicar_filtro_anos(df_mov, "Anos")

    movimentos = sorted(df_mov["movimentacao"].dropna().unique())
    movimentos_selecionados = st.multiselect("Indicadores de movimentação", movimentos, default=movimentos)
    df_mov = df_mov[df_mov["movimentacao"].isin(movimentos_selecionados)].copy()

    mostrar_metricas_movimentacao(df_mov)

    if len(df_mov) > 0:
        df_q3_bar = (
            df_mov.groupby(["ano", "mes_numero", "mes", "movimentacao"], as_index=False)
            .agg(valor=("valor", "sum"))
            .sort_values(["ano", "mes_numero"])
        )
        fig_bar = px.bar(
            df_q3_bar,
            x="mes",
            y="valor",
            color="movimentacao",
            facet_col="ano",
            facet_col_wrap=2,
            barmode="group",
            category_orders={"mes": MESES_ORDEM},
            title="Indicadores de movimentação por mês",
            labels={"mes": "Mês", "valor": "Registros de movimentação", "movimentacao": "Indicador", "ano": "Ano"},
            hover_data={"ano": True, "valor": True, "movimentacao": True},
        )
        fig_bar.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig_bar.update_layout(height=650, legend_title_text="Indicador de movimentação")
        aplicar_layout_figura(fig_bar)
        st.plotly_chart(fig_bar, use_container_width=True)

        df_q3_heat = (
            df_mov.groupby(["ano", "mes_numero", "mes"], as_index=False)
            .agg(total=("valor", "sum"))
            .sort_values(["ano", "mes_numero"])
        )
        fig_heat = criar_heatmap_mensal(df_q3_heat, "Heatmap de períodos críticos de movimentação")
        aplicar_layout_figura(fig_heat)
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Nenhum indicador de movimentação encontrado para os filtros selecionados.")

# Dashboard 4 — Pergunta 4

elif pagina == "4. Estabilidade da permanência":
    st.caption(
        "Observação: como a base é agregada, o fluxo representa volumes consolidados por ano, "
        "não trajetórias individuais de crianças ou adolescentes."
    )

    df_mov = df.copy()
    df_mov["movimentacao"] = df_mov.apply(classificar_movimentacao, axis=1)
    df_mov = df_mov[df_mov["movimentacao"].notna()].copy()

    st.markdown("### Filtros")
    df_mov = aplicar_filtro_periodo_mensal(df_mov)
    df_mov, anos_selecionados = aplicar_filtro_anos(df_mov, "Anos")

    movimentos = sorted(df_mov["movimentacao"].dropna().unique())
    movimentos_selecionados = st.multiselect("Indicadores de movimentação", movimentos, default=movimentos)
    df_mov = df_mov[df_mov["movimentacao"].isin(movimentos_selecionados)].copy()

    mostrar_metricas_estabilidade(df_mov)

    if len(df_mov) > 0:
        no_isolado = st.selectbox(
            "Isolar fluxo por nó",
            ["Todos"] + movimentos,
            index=0,
        )

        df_q4 = df_mov.copy()
        if no_isolado != "Todos":
            df_q4 = df_q4[df_q4["movimentacao"] == no_isolado].copy()

        fluxo = (
            df_q4.groupby(["ano", "movimentacao"], as_index=False)
            .agg(valor=("valor", "sum"))
        )
        anos_labels = [str(int(a)) for a in sorted(fluxo["ano"].dropna().unique())]
        mov_labels = sorted(fluxo["movimentacao"].dropna().unique())
        labels = anos_labels + mov_labels
        idx = {label: i for i, label in enumerate(labels)}

        sources, targets, values = [], [], []
        for _, row in fluxo.iterrows():
            ano_label = str(int(row["ano"]))
            mov_label = row["movimentacao"]
            if row["valor"] > 0 and ano_label in idx and mov_label in idx:
                sources.append(idx[ano_label])
                targets.append(idx[mov_label])
                values.append(row["valor"])

        if values:
            fig_sankey = go.Figure(data=[go.Sankey(
                arrangement="snap",
                node=dict(
                    label=labels,
                    pad=18,
                    thickness=18,
                    color="#DBEAFE",
                    line=dict(color="#93C5FD", width=1),
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                    color="rgba(37, 99, 235, 0.20)",
                ),
            )])
            fig_sankey.update_layout(
                title="Diagrama de fluxo das movimentações institucionais",
                height=620,
            )
            aplicar_layout_figura(fig_sankey)
            st.plotly_chart(fig_sankey, use_container_width=True)

        df_composicao = (
            df_mov.groupby(["ano", "movimentacao"], as_index=False)
            .agg(registros_movimentacao=("valor", "sum"))
            .sort_values(["ano", "movimentacao"])
        )

        fig_comp = px.bar(
            df_composicao,
            x="ano",
            y="registros_movimentacao",
            color="movimentacao",
            barmode="stack",
            title="Composição anual das movimentações",
            labels={
                "ano": "Ano",
                "registros_movimentacao": "Registros de movimentação",
                "movimentacao": "Tipo de movimentação",
            },
        )
        fig_comp.update_xaxes(
            tickmode="array",
            tickvals=sorted(df_composicao["ano"].dropna().unique()),
            ticktext=[str(int(a)) for a in sorted(df_composicao["ano"].dropna().unique())],
        )
        aplicar_layout_figura(fig_comp, 560)
        st.plotly_chart(fig_comp, use_container_width=True)

        df_saida = df_mov[df_mov["movimentacao"].isin(["Saída", "Evasão", "Desligamento"])].copy()
        if len(df_saida) > 0:
            df_saida_mes = (
                df_saida.groupby(["ano", "mes_numero", "mes", "movimentacao"], as_index=False)
                .agg(registros_movimentacao=("valor", "sum"))
                .sort_values(["ano", "mes_numero"])
            )
            fig_saida = px.line(
                df_saida_mes,
                x="mes",
                y="registros_movimentacao",
                color="movimentacao",
                facet_col="ano",
                facet_col_wrap=2,
                markers=True,
                category_orders={"mes": MESES_ORDEM},
                title="Meses de maior pressão de saída",
                labels={
                    "mes": "Mês",
                    "registros_movimentacao": "Registros de saída crítica",
                    "movimentacao": "Tipo",
                    "ano": "Ano",
                },
            )
            fig_saida.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            aplicar_layout_figura(fig_saida, 640)
            st.plotly_chart(fig_saida, use_container_width=True)
    else:
        st.info("Não há dados suficientes para montar o fluxo desta análise.")

# Dashboard 5 — Pergunta 5

elif pagina == "5. Acolhidos, saúde e educação":
    st.markdown(
        """
        <div class="fp-note">
        <strong>Como ler:</strong> “Efetivos na casa” funciona como a base de comparação dos acolhidos. 
        Saúde mental, saúde clínica e educação são registros acumulados de acompanhamento. 
        Quando os registros crescem mais do que os efetivos, isso sugere maior intensidade de atendimento por acolhido.
        </div>
        """,
        unsafe_allow_html=True,
    )

    df_q5 = df.copy()
    df_q5["grupo_analise"] = df_q5.apply(classificar_grupo_q5, axis=1)
    df_q5 = df_q5[df_q5["grupo_analise"].notna()].copy()

    st.markdown("### Filtros")
    df_q5, anos_q5 = aplicar_filtro_anos(df_q5, "Anos")

    grupos_disponiveis = sorted(df_q5["grupo_analise"].dropna().unique())
    grupos_selecionados = st.multiselect(
        "Grupos de análise",
        grupos_disponiveis,
        default=grupos_disponiveis,
    )

    # Mantém uma cópia antes do filtro de grupos.
    # Assim a KPI de efetivos na casa não vira 0 se o grupo for desmarcado no filtro.
    df_q5_metricas = df_q5.copy()

    df_q5 = df_q5[df_q5["grupo_analise"].isin(grupos_selecionados)].copy()

    mostrar_metricas_q5(df_q5_metricas)

    if len(df_q5) > 0:
        df_q5_anual = (
            df_q5.groupby(["ano", "grupo_analise"], as_index=False)
            .agg(valor=("valor", "sum"))
            .sort_values(["ano", "grupo_analise"])
        )

        df_q5_pivot = df_q5_anual.pivot_table(
            index="ano",
            columns="grupo_analise",
            values="valor",
            aggfunc="sum",
            fill_value=0,
        ).reset_index()

        fig_combo = make_subplots(specs=[[{"secondary_y": True}]])

        if "Número de acolhidos" in df_q5_pivot.columns:
            fig_combo.add_trace(
                go.Bar(
                    x=df_q5_pivot["ano"],
                    y=df_q5_pivot["Número de acolhidos"],
                    name="Efetivos na casa",
                ),
                secondary_y=False,
            )

        for grupo in ["Saúde mental", "Saúde clínica", "Educação"]:
            if grupo in df_q5_pivot.columns:
                fig_combo.add_trace(
                    go.Scatter(
                        x=df_q5_pivot["ano"],
                        y=df_q5_pivot[grupo],
                        mode="lines+markers",
                        name=grupo,
                    ),
                    secondary_y=True,
                )

        fig_combo.update_layout(
            title="Efetivos na casa x indicadores de saúde e educação",
            height=600,
            hovermode="x unified",
        )
        aplicar_layout_figura(fig_combo)

        fig_combo.update_xaxes(
            tickmode="array",
            tickvals=df_q5_pivot["ano"],
            ticktext=df_q5_pivot["ano"].astype(int).astype(str),
            title_text="Ano",
        )

        fig_combo.update_yaxes(
            title_text="Efetivos na casa",
            secondary_y=False,
        )

        fig_combo.update_yaxes(
            title_text="Registros de saúde e educação",
            secondary_y=True,
        )

        st.plotly_chart(fig_combo, use_container_width=True)

        if "Número de acolhidos" in df_q5_pivot.columns:
            df_taxa = df_q5_pivot.copy()
            grupos_taxa = [g for g in ["Saúde mental", "Saúde clínica", "Educação"] if g in df_taxa.columns]
            for grupo in grupos_taxa:
                df_taxa[grupo] = np.where(
                    df_taxa["Número de acolhidos"] > 0,
                    (df_taxa[grupo] / df_taxa["Número de acolhidos"]) * 100,
                    np.nan,
                )
            if grupos_taxa:
                df_taxa_long = df_taxa.melt(
                    id_vars="ano",
                    value_vars=grupos_taxa,
                    var_name="grupo_analise",
                    value_name="registros_por_100_efetivos",
                ).dropna(subset=["registros_por_100_efetivos"])

                fig_taxa = px.bar(
                    df_taxa_long,
                    x="ano",
                    y="registros_por_100_efetivos",
                    color="grupo_analise",
                    barmode="group",
                    title="Intensidade dos registros por 100 efetivos na casa",
                    labels={
                        "ano": "Ano",
                        "registros_por_100_efetivos": "Registros por 100 efetivos",
                        "grupo_analise": "Área de acompanhamento",
                    },
                )
                fig_taxa.update_xaxes(
                    tickmode="array",
                    tickvals=df_taxa_long["ano"].dropna().unique(),
                    ticktext=[str(int(a)) for a in df_taxa_long["ano"].dropna().unique()],
                )
                aplicar_layout_figura(fig_taxa, 540)
                st.plotly_chart(fig_taxa, use_container_width=True)

        df_q5_indice = df_q5_anual.copy()

        df_q5_indice["grupo_label"] = df_q5_indice["grupo_analise"].replace({
            "Número de acolhidos": "Efetivos na casa"
        })

        df_q5_indice["valor_base"] = df_q5_indice.groupby("grupo_analise")["valor"].transform("first")

        df_q5_indice["indice_base_100"] = np.where(
            df_q5_indice["valor_base"] != 0,
            (df_q5_indice["valor"] / df_q5_indice["valor_base"]) * 100,
            np.nan,
        )

        fig_indice = px.line(
            df_q5_indice,
            x="ano",
            y="indice_base_100",
            color="grupo_label",
            markers=True,
            title="Evolução proporcional — índice base 100",
            labels={
                "ano": "Ano",
                "indice_base_100": "Índice base 100",
                "grupo_label": "Grupo",
            },
            hover_data={"valor": True},
        )

        anos_indice = sorted(df_q5_indice["ano"].dropna().unique())

        fig_indice.update_xaxes(
            tickmode="array",
            tickvals=anos_indice,
            ticktext=[str(int(a)) for a in anos_indice],
            title_text="Ano",
        )

        fig_indice.update_yaxes(title_text="Índice base 100")

        fig_indice.update_layout(
            height=550,
            hovermode="x unified",
        )
        aplicar_layout_figura(fig_indice)

        st.plotly_chart(fig_indice, use_container_width=True)

    else:
        st.info("Nenhum registro encontrado com os filtros atuais.")

# Dashboard 6 — Pergunta 6

else:
    df_q6 = df[df["ano"] == 2025].copy()
    df_q6["metrica_q6"] = df_q6.apply(classificar_metrica_q6, axis=1)
    df_q6["atividade"] = df_q6["indicador_completo"].fillna(df_q6["indicador"]).astype(str)
    df_q6 = df_q6[df_q6["atividade"].notna()].copy()

    if len(df_q6) > 0:
        metrica_q6 = "Quantidade de eventos realizados"
        df_q6_filtrado = df_q6[df_q6["metrica_q6"] == "Quantidade de Eventos Realizados"].copy()

        mostrar_metricas_atividades(df_q6_filtrado, metrica_q6)

        df_treemap = (
            df_q6_filtrado.groupby(["atividade"], as_index=False)
            .agg(valor=("valor", "sum"))
            .sort_values("valor", ascending=False)
        )
        df_treemap = df_treemap[df_treemap["valor"] > 0]

        if len(df_treemap) > 0:
            fig_tree = px.treemap(
                df_treemap,
                path=["atividade"],
                values="valor",
                title="Distribuição dos eventos realizados em 2025",
                hover_data={"valor": True},
            )
            fig_tree.update_layout(height=700)
            aplicar_layout_figura(fig_tree)
            st.plotly_chart(fig_tree, use_container_width=True)

            df_top_atividades = df_treemap.head(10).copy()
            fig_top = px.bar(
                df_top_atividades,
                x="valor",
                y="atividade",
                orientation="h",
                title="Top 10 eventos mais realizados em 2025",
                labels={"valor": "Quantidade de eventos", "atividade": "Evento"},
            )
            fig_top.update_layout(height=600, yaxis={"categoryorder": "total ascending"})
            aplicar_layout_figura(fig_top)
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.info("Existem registros para 2025, mas todos os valores de eventos realizados são zero.")

        df_q6_mes = (
            df_q6_filtrado.groupby(["mes_numero", "mes"], as_index=False)
            .agg(valor=("valor", "sum"))
            .sort_values("mes_numero")
        )
        df_q6_mes = df_q6_mes[df_q6_mes["valor"] > 0]

        if len(df_q6_mes) > 0:
            fig_mes = px.bar(
                df_q6_mes,
                x="mes",
                y="valor",
                category_orders={"mes": MESES_ORDEM},
                title="Distribuição mensal dos eventos realizados em 2025",
                labels={"mes": "Mês", "valor": "Quantidade de eventos"},
            )
            fig_mes.update_layout(height=600)
            aplicar_layout_figura(fig_mes)
            st.plotly_chart(fig_mes, use_container_width=True)
    else:
        st.info("Nenhum registro de evento encontrado para 2025 com as palavras-chave atuais.")

st.caption("Fonte: base tratada lem_consolidado_2021_2025.csv")
