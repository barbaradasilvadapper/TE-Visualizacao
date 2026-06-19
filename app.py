import re
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
)

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] .stRadio label {
        font-weight: 500;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background-color: rgba(128, 128, 128, 0.12);
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

MESES_ORDEM = [
    "JAN", "FEV", "MAR", "ABR", "MAI", "JUN",
    "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"
]

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
    return df[df["ano"].isin(anos_selecionados)].copy(), anos_selecionados


def aplicar_filtro_periodo_mensal(df):
    if df["data"].dropna().empty:
        return df

    data_min = df["data"].min().date()
    data_max = df["data"].max().date()
    periodo = st.date_input(
        "Período mensal",
        value=(data_min, data_max),
        min_value=data_min,
        max_value=data_max,
    )

    if isinstance(periodo, tuple) and len(periodo) == 2:
        inicio, fim = pd.to_datetime(periodo[0]), pd.to_datetime(periodo[1])
        return df[(df["data"] >= inicio) & (df["data"] <= fim)].copy()

    return df


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
    indicadores = df["indicador_completo"].nunique() if "indicador_completo" in df.columns else 0
    anos = sorted(df["ano"].dropna().unique())
    periodo = (
        f"{int(anos[0])} – {int(anos[-1])}"
        if len(anos) >= 1
        else "Sem período válido"
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Atendimentos totais", f"{total:,.0f}".replace(",", "."))
    c2.metric("Indicadores técnicos", indicadores)
    c3.metric("Período analisado", periodo)


def mostrar_metricas_desdobramentos(df, anos):
    total = int(df["valor"].sum()) if len(df) > 0 else 0
    tipos = df["indicador_completo"].nunique() if "indicador_completo" in df.columns else 0
    variacao_texto = "Sem comparação entre anos"
    if len(anos) >= 2:
        primeiro_ano = min(anos)
        ultimo_ano = max(anos)
        anual = df.groupby(["ano", "indicador_completo"], as_index=False).agg(total=("valor", "sum"))
        inicio = anual[anual["ano"] == primeiro_ano][["indicador_completo", "total"]].rename(columns={"total": "total_inicio"})
        fim = anual[anual["ano"] == ultimo_ano][["indicador_completo", "total"]].rename(columns={"total": "total_fim"})
        variacao = inicio.merge(fim, on="indicador_completo", how="outer").fillna(0)
        variacao["variacao_absoluta"] = variacao["total_fim"] - variacao["total_inicio"]
        maior = variacao.loc[variacao["variacao_absoluta"].idxmax()]
        variacao_texto = (
            f"{maior['indicador_completo']} ({str(int(maior['variacao_absoluta']))})"
            if len(variacao) > 0
            else "Sem variação detectada"
        )

    c1, c2, c3 = st.columns(3)
    c1.metric("Total de desdobramentos", f"{total:,.0f}".replace(",", "."))
    c2.metric("Tipos de desdobramento", tipos)


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
    c1.metric("Total de movimentações", f"{total:,.0f}".replace(",", "."))
    c2.metric("Indicador mais frequente", top_mov)
    c3.metric("Período crítico", top_periodo)


def mostrar_metricas_estabilidade(df):
    total = int(df["valor"].sum()) if len(df) > 0 else 0
    indice_ultimo = "Sem dados"
    ano_maior = "Sem dados"
    if len(df) > 0:
        est = (
            df.groupby(["ano", "movimentacao"], as_index=False)
            .agg(valor=("valor", "sum"))
            .pivot_table(index="ano", columns="movimentacao", values="valor", aggfunc="sum", fill_value=0)
            .reset_index()
        )
        for col in ["Entrada", "Permanência", "Saída", "Evasão", "Desligamento"]:
            if col not in est.columns:
                est[col] = 0
        base = est["Entrada"] + est["Permanência"] + est["Saída"] + est["Evasão"] + est["Desligamento"]
        est["indice_estabilidade"] = np.where(base > 0, 1 - ((est["Saída"] + est["Evasão"] + est["Desligamento"]) / base), np.nan)
        est_valid = est.dropna(subset=["indice_estabilidade"])
        if len(est_valid) > 0:
            ano_maior = str(int(est_valid.loc[est_valid["indice_estabilidade"].idxmax(), "ano"]))
            ultimo = est_valid.iloc[-1]
            indice_ultimo = f"{ultimo['indice_estabilidade']:.2f}"

    c1, c2, c3 = st.columns(3)
    c1.metric("Total de movimentações", f"{total:,.0f}".replace(",", "."))
    c2.metric("Ano de maior estabilidade", ano_maior)
    c3.metric("Índice de estabilidade último ano", indice_ultimo)


def mostrar_metricas_q5(df):
    total_acolhidos = int(df[df["grupo_analise"] == "Número de acolhidos"]["valor"].sum() if len(df) > 0 else 0)
    grupos = df["grupo_analise"].nunique()
    maior_crescimento = "Sem dados"
    if len(df) > 0:
        anual = df.groupby(["ano", "grupo_analise"], as_index=False).agg(valor=("valor", "sum"))
        base = (
            anual.sort_values("ano")
            .groupby("grupo_analise", as_index=False)
            .first()[["grupo_analise", "valor"]]
            .rename(columns={"valor": "base"})
        )
        fim = (
            anual.sort_values("ano")
            .groupby("grupo_analise", as_index=False)
            .last()[["grupo_analise", "valor"]]
            .rename(columns={"valor": "fim"})
        )
        comparacao = base.merge(fim, on="grupo_analise", how="inner")
        comparacao["crescimento_pct"] = np.where(comparacao["base"] != 0, (comparacao["fim"] / comparacao["base"] - 1) * 100, np.nan)
        comparacao = comparacao.dropna(subset=["crescimento_pct"])
        if len(comparacao) > 0:
            maior_crescimento = comparacao.loc[comparacao["crescimento_pct"].idxmax(), "grupo_analise"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Acolhidos contabilizados", f"{total_acolhidos:,.0f}".replace(",", "."))
    c2.metric("Indicadores de saúde/educação", grupos)
    c3.metric("Maior crescimento proporcional", maior_crescimento)


def mostrar_metricas_atividades(df, metrica):
    total = int(df["valor"].sum()) if len(df) > 0 else 0
    atividades = df["atividade"].nunique() if "atividade" in df.columns else 0
    principal = "Sem dados"
    if len(df) > 0:
        principal = df.groupby("atividade")["valor"].sum().idxmax()

    c1, c2, c3 = st.columns(3)
    c1.metric("Valor total selecionado", f"{total:,.0f}".replace(",", "."))
    c2.metric("Atividades distintas", atividades)
    c3.metric("Atividade com maior alcance", principal)


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
    if any(p in texto for p in ["perman", "ativos", "atendidos"]):
        return "Permanência"
    return None


def classificar_grupo_q5(linha):
    if contem_palavras(linha, ["acolhido", "acolhidos", "acolhida", "acolhidas", "acolhimento"]):
        return "Número de acolhidos"
    if contem_palavras(linha, ["saúde mental", "saude mental", "psicol", "psiquiatr", "terapia"]):
        return "Saúde mental"
    if contem_palavras(linha, ["saúde clínica", "saude clinica", "saúde clinica", "saude clínica", "clínica", "clinica", "médic", "medic", "consulta", "enferm"]):
        return "Saúde clínica"
    if contem_palavras(linha, ["educação", "educacao", "escola", "escolar", "pedag", "ensino"]):
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

st.title("Dashboard Fundação Pão dos Pobres")

pagina = st.sidebar.radio(
    "Dashboard",
    [
        "1. Evolução da demanda e sobrecarga",
        "2. Desdobramentos técnicos",
        "3. Padrões sazonais e movimentação",
        "4. Estabilidade da permanência",
        "5. Acolhidos, saúde e educação",
        "6. Distribuição e alcance das atividades de 2025",
    ],
    label_visibility="collapsed",
)

# Dashboard 1 — Pergunta 1

if pagina == "1. Evolução da demanda e sobrecarga":
    st.header("Evolução da demanda e sobrecarga")
    st.markdown(
        "Este dashboard apresenta a evolução mensal dos atendimentos por indicador "
        "e destaca os meses com maior concentração de demanda técnica."
    )

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
            df_q1.groupby(["ano", "indicador_completo"], as_index=False)
            .agg(valor=("valor", "sum"))
            .sort_values(["ano"])
        )

        fig = px.line(
            df_q1_linha,
            x="ano",
            y="valor",
            facet_col="indicador_completo",
            facet_col_wrap=2,
            markers=True,
            title="Evolução anual dos atendimentos por indicador",
            labels={"ano": "Ano", "valor": "Quantidade", "indicador_completo": "Indicador"},
            hover_data={"ano": True, "valor": True, "indicador_completo": True},
        )
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig.update_xaxes(title_text="Ano", tickmode="array", tickvals=sorted(df_q1_linha["ano"].dropna().unique()), ticktext=[str(int(a)) for a in sorted(df_q1_linha["ano"].dropna().unique())])
        fig.update_layout(height=900, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns([1.2, 1])
        with c1:
            df_heat = (
                df_q1.groupby(["ano", "mes_numero", "mes"], as_index=False)
                .agg(total=("valor", "sum"))
                .sort_values(["ano", "mes_numero"])
            )
            anos_heat = sorted([int(a) for a in df_heat["ano"].dropna().unique()])
            df_heat["ano_label"] = df_heat["ano"].dropna().astype(int).astype(str)
            fig_heat = px.density_heatmap(
                df_heat,
                x="mes",
                y="ano_label",
                z="total",
                category_orders={"mes": MESES_ORDEM, "ano_label": [str(a) for a in anos_heat]},
                title="Heatmap de sobrecarga mensal",
                labels={"mes": "Mês", "ano_label": "Ano", "total": "Total"},
            )
            fig_heat.update_yaxes(tickmode="array", tickvals=[str(a) for a in anos_heat], ticktext=[str(a) for a in anos_heat])
            fig_heat.update_layout(height=500)
            st.plotly_chart(fig_heat, use_container_width=True)

        with c2:
            st.markdown("#### Meses com maior sobrecarga")
            ranking = df_heat.sort_values("total", ascending=False).head(10)
            st.dataframe(ranking[["ano", "mes", "total"]], use_container_width=True, hide_index=True)
    else:
        st.info("Selecione pelo menos um indicador para visualizar esta análise.")

# Dashboard 2 — Pergunta 2

elif pagina == "2. Desdobramentos técnicos":
    st.header("Desdobramentos técnicos")
    st.markdown(
        "Este dashboard mostra a evolução dos tipos de desdobramentos técnicos "
        "e a variação entre o primeiro e o último ano selecionado."
    )

    st.markdown("### Filtros")
    df_filtrado, anos_selecionados = aplicar_filtro_anos(df, "Anos")

    df_desdobramentos = df_filtrado.copy()
    df_desdobramentos["categoria_ajustada"] = df_desdobramentos["categoria"].fillna("DESDOBRAMENTOS TÉCNICOS")
    df_desdobramentos["categoria_ajustada"] = df_desdobramentos["categoria_ajustada"].replace({"": "DESDOBRAMENTOS TÉCNICOS", "nan": "DESDOBRAMENTOS TÉCNICOS"})
    df_desdobramentos = df_desdobramentos[df_desdobramentos["categoria_ajustada"] == "DESDOBRAMENTOS TÉCNICOS"].copy()

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
            labels={"data": "Período", "valor": "Quantidade", "indicador_completo": "Tipo de desdobramento"},
            hover_data={"ano": True, "mes": True, "valor": True},
        )
        fig.update_layout(xaxis_title="Ano")
        fig.update_xaxes(tickformat="%Y", dtick="M12")
        fig.update_layout(height=600, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        if len(anos_selecionados) >= 2:
            primeiro_ano = min(anos_selecionados)
            ultimo_ano = max(anos_selecionados)
            anual = df_q2.groupby(["ano", "indicador_completo"], as_index=False).agg(total=("valor", "sum"))
            inicio = anual[anual["ano"] == primeiro_ano][["indicador_completo", "total"]].rename(columns={"total": "total_inicio"})
            fim = anual[anual["ano"] == ultimo_ano][["indicador_completo", "total"]].rename(columns={"total": "total_fim"})
            variacao = inicio.merge(fim, on="indicador_completo", how="outer").fillna(0)
            variacao["variacao_absoluta"] = variacao["total_fim"] - variacao["total_inicio"]
            variacao = variacao.sort_values("variacao_absoluta", ascending=False).head(15)

            fig_var = px.bar(
                variacao,
                x="variacao_absoluta",
                y="indicador_completo",
                orientation="h",
                title=f"Variação dos desdobramentos entre {primeiro_ano} e {ultimo_ano}",
                labels={"variacao_absoluta": "Variação absoluta", "indicador_completo": "Tipo"},
            )
            fig_var.update_layout(height=600, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_var, use_container_width=True)
    else:
        st.info("Nenhum desdobramento técnico encontrado para os filtros selecionados.")

# Dashboard 3 — Pergunta 3

elif pagina == "3. Padrões sazonais e movimentação":
    st.header("Padrões sazonais e períodos críticos")
    st.markdown(
        "Este dashboard analisa entradas, saídas, evasões, desligamentos e permanência "
        "para identificar sazonalidade e períodos críticos."
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
            labels={"mes": "Mês", "valor": "Quantidade", "movimentacao": "Indicador", "ano": "Ano"},
            hover_data={"ano": True, "valor": True, "movimentacao": True},
        )
        fig_bar.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig_bar.update_layout(height=650, legend_title_text="Indicador de movimentação")
        st.plotly_chart(fig_bar, use_container_width=True)

        df_q3_heat = (
            df_mov.groupby(["ano", "mes_numero", "mes"], as_index=False)
            .agg(total=("valor", "sum"))
            .sort_values(["ano", "mes_numero"])
        )
        anos_heat = sorted([int(a) for a in df_q3_heat["ano"].dropna().unique()])
        df_q3_heat["ano_label"] = df_q3_heat["ano"].dropna().astype(int).astype(str)
        fig_heat = px.density_heatmap(
            df_q3_heat,
            x="mes",
            y="ano_label",
            z="total",
            category_orders={"mes": MESES_ORDEM, "ano_label": [str(a) for a in anos_heat]},
            title="Heatmap de períodos críticos de movimentação",
            labels={"mes": "Mês", "ano_label": "Ano", "total": "Total"},
        )
        fig_heat.update_yaxes(tickmode="array", tickvals=[str(a) for a in anos_heat], ticktext=[str(a) for a in anos_heat])
        fig_heat.update_layout(height=500)
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Nenhum indicador de movimentação encontrado para os filtros selecionados.")

# Dashboard 4 — Pergunta 4

elif pagina == "4. Estabilidade da permanência":
    st.header("Estabilidade da permanência")
    st.markdown(
        "Este dashboard apresenta o fluxo das movimentações institucionais e um índice simples "
        "de estabilidade por ano."
    )
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
                node=dict(label=labels, pad=18, thickness=18),
                link=dict(source=sources, target=targets, value=values),
            )])
            fig_sankey.update_layout(title="Diagrama de fluxo das movimentações institucionais", height=650)
            st.plotly_chart(fig_sankey, use_container_width=True)

        df_estabilidade = (
            df_mov.groupby(["ano", "movimentacao"], as_index=False)
            .agg(valor=("valor", "sum"))
            .pivot_table(index="ano", columns="movimentacao", values="valor", aggfunc="sum", fill_value=0)
            .reset_index()
        )
        for col in ["Entrada", "Permanência", "Saída", "Evasão", "Desligamento"]:
            if col not in df_estabilidade.columns:
                df_estabilidade[col] = 0

        saidas_total = df_estabilidade["Saída"] + df_estabilidade["Evasão"] + df_estabilidade["Desligamento"]
        entradas_total = df_estabilidade["Entrada"]
        permanencia_total = df_estabilidade["Permanência"]
        base_movimentacao = entradas_total + permanencia_total + saidas_total

        df_estabilidade["indice_estabilidade"] = np.where(
            base_movimentacao > 0,
            1 - (saidas_total / base_movimentacao),
            np.nan,
        )

        fig_est = px.line(
            df_estabilidade,
            x="ano",
            y="indice_estabilidade",
            markers=True,
            title="Índice simples de estabilidade por ano",
            labels={"ano": "Ano", "indice_estabilidade": "Índice de estabilidade"},
        )
        fig_est.update_xaxes(tickmode="array", tickvals=df_estabilidade["ano"], ticktext=df_estabilidade["ano"].astype(str))
        fig_est.update_yaxes(range=[0, 1])
        fig_est.update_layout(height=500)
        st.plotly_chart(fig_est, use_container_width=True)
    else:
        st.info("Não há dados suficientes para montar o fluxo desta análise.")

# Dashboard 5 — Pergunta 5

elif pagina == "5. Acolhidos, saúde e educação":
    st.header("Acolhidos x saúde e educação")
    st.markdown(
        "Este dashboard compara indicadores de saúde e educação com o número de acolhidos "
        "ao longo dos anos."
    )

    df_q5 = df.copy()
    df_q5["grupo_analise"] = df_q5.apply(classificar_grupo_q5, axis=1)
    df_q5 = df_q5[df_q5["grupo_analise"].notna()].copy()

    st.markdown("### Filtros")
    df_q5, anos_q5 = aplicar_filtro_anos(df_q5, "Anos")

    grupos_disponiveis = sorted(df_q5["grupo_analise"].dropna().unique())
    grupos_selecionados = st.multiselect("Grupos de análise", grupos_disponiveis, default=grupos_disponiveis)
    df_q5 = df_q5[df_q5["grupo_analise"].isin(grupos_selecionados)].copy()

    mostrar_metricas_q5(df_q5)

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
                go.Bar(x=df_q5_pivot["ano"], y=df_q5_pivot["Número de acolhidos"], name="Número de acolhidos"),
                secondary_y=False,
            )
        for grupo in ["Saúde mental", "Saúde clínica", "Educação"]:
            if grupo in df_q5_pivot.columns:
                fig_combo.add_trace(
                    go.Scatter(x=df_q5_pivot["ano"], y=df_q5_pivot[grupo], mode="lines+markers", name=grupo),
                    secondary_y=True,
                )
        fig_combo.update_layout(title="Acolhidos x indicadores de saúde e educação", height=600, hovermode="x unified")
        fig_combo.update_xaxes(tickmode="array", tickvals=df_q5_pivot["ano"], ticktext=df_q5_pivot["ano"].astype(str))
        fig_combo.update_yaxes(title_text="Número de acolhidos", secondary_y=False)
        fig_combo.update_yaxes(title_text="Indicadores", secondary_y=True)
        st.plotly_chart(fig_combo, use_container_width=True)

        df_q5_indice = df_q5_anual.copy()
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
            color="grupo_analise",
            markers=True,
            title="Evolução proporcional — índice base 100",
            labels={"ano": "Ano", "indice_base_100": "Índice base 100", "grupo_analise": "Grupo"},
            hover_data={"valor": True},
        )
        anos_indice = sorted(df_q5_indice["ano"].dropna().unique())
        fig_indice.update_xaxes(tickmode="array", tickvals=anos_indice, ticktext=[str(int(a)) for a in anos_indice])
        fig_indice.update_layout(height=550, hovermode="x unified")
        st.plotly_chart(fig_indice, use_container_width=True)
    else:
        st.info("Nenhum registro encontrado com os filtros atuais.")

# Dashboard 6 — Pergunta 6

else:
    st.header("Atividades de 2025")
    st.markdown(
        "Este dashboard analisa as atividades registradas em 2025 a partir da coluna de atividade/indicador completo, "
        "mostrando alcance e distribuição dos principais registros do ano."
    )

    df_q6 = df[df["ano"] == 2025].copy()
    df_q6["metrica_q6"] = df_q6.apply(classificar_metrica_q6, axis=1)
    df_q6["atividade"] = df_q6["indicador_completo"].fillna(df_q6["indicador"]).astype(str)
    df_q6 = df_q6[df_q6["atividade"].notna()].copy()

    if len(df_q6) > 0:
        metricas_base = sorted(df_q6["metrica_q6"].dropna().unique())
        ordem_metricas = ["Número de Participantes", "Carga Horária Total", "Quantidade de Eventos Realizados"]
        metricas_disponiveis = [m for m in ordem_metricas if m in metricas_base]
        if not metricas_disponiveis:
            metricas_disponiveis = metricas_base
        metrica_q6 = metricas_disponiveis[0]

        metrica_q6 = st.selectbox("Métrica", metricas_disponiveis, index=0)
        df_q6_filtrado = df_q6[df_q6["metrica_q6"] == metrica_q6].copy()

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
                title=f"Treemap das atividades de 2025 por {metrica_q6}",
                hover_data={"valor": True},
            )
            fig_tree.update_layout(height=700)
            st.plotly_chart(fig_tree, use_container_width=True)

            df_top_atividades = df_treemap.head(10).copy()
            fig_top = px.bar(
                df_top_atividades,
                x="valor",
                y="atividade",
                orientation="h",
                title=f"Top 10 atividades de 2025 por {metrica_q6}",
                labels={"valor": metrica_q6, "atividade": "Atividade"},
            )
            fig_top.update_layout(height=600, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.info("Existem registros para 2025, mas todos os valores da métrica selecionada são zero.")

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
                title=f"Distribuição mensal das atividades de 2025 por {metrica_q6}",
                labels={"mes": "Mês", "valor": metrica_q6},
            )
            fig_mes.update_layout(height=600)
            st.plotly_chart(fig_mes, use_container_width=True)
    else:
        st.info("Nenhum registro de atividade encontrado para 2025 com as palavras-chave atuais.")

st.caption("Fonte: base tratada lem_consolidado_2021_2025.csv")
