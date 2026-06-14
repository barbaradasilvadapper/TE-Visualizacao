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
        "Demanda e Sobrecarga Técnica",
        "Movimentações e Permanência",
        "Indicadores e Atividades",
    ],
    label_visibility="collapsed",
)

# Dashboard 1 — Perguntas 1 e 2

if pagina == "Demanda e Sobrecarga Técnica":
    st.header("Demanda e Sobrecarga Técnica")
    st.markdown(
        "Este dashboard reúne as análises sobre evolução dos atendimentos técnicos, "
        "picos de sobrecarga e variação dos desdobramentos técnicos."
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

    mostrar_metricas_basicas(df_dash)

    st.subheader("Evolução da demanda e sobrecarga")
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
            df_q1.groupby(["data", "ano", "mes", "indicador_completo"], as_index=False)
            .agg(valor=("valor", "sum"))
            .sort_values("data")
        )

        fig = px.line(
            df_q1_linha,
            x="data",
            y="valor",
            facet_col="indicador_completo",
            facet_col_wrap=2,
            markers=True,
            title="Small multiples — evolução mensal dos atendimentos por indicador",
            labels={"data": "Período", "valor": "Quantidade", "indicador_completo": "Indicador"},
            hover_data={"ano": True, "mes": True, "valor": True, "indicador_completo": True},
        )
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig.update_layout(height=900, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns([1.2, 1])
        with c1:
            df_heat = (
                df_q1.groupby(["ano", "mes_numero", "mes"], as_index=False)
                .agg(total=("valor", "sum"))
                .sort_values(["ano", "mes_numero"])
            )
            fig_heat = px.density_heatmap(
                df_heat,
                x="mes",
                y="ano",
                z="total",
                category_orders={"mes": MESES_ORDEM},
                title="Heatmap de sobrecarga mensal",
                labels={"mes": "Mês", "ano": "Ano", "total": "Total"},
            )
            fig_heat.update_layout(height=500)
            st.plotly_chart(fig_heat, use_container_width=True)

        with c2:
            st.markdown("#### Meses com maior sobrecarga")
            ranking = df_heat.sort_values("total", ascending=False).head(10)
            st.dataframe(ranking[["ano", "mes", "total"]], use_container_width=True, hide_index=True)
    else:
        st.info("Selecione pelo menos um indicador para visualizar esta análise.")

    st.divider()

    st.subheader("Desdobramentos técnicos")
    df_desdobramentos = df.copy()
    df_desdobramentos["categoria_ajustada"] = df_desdobramentos["categoria"].fillna("DESDOBRAMENTOS TÉCNICOS")
    df_desdobramentos["categoria_ajustada"] = df_desdobramentos["categoria_ajustada"].replace({"": "DESDOBRAMENTOS TÉCNICOS", "nan": "DESDOBRAMENTOS TÉCNICOS"})
    df_desdobramentos = df_desdobramentos[df_desdobramentos["categoria_ajustada"] == "DESDOBRAMENTOS TÉCNICOS"].copy()
    df_desdobramentos = df_desdobramentos[df_desdobramentos["ano"].isin(anos_selecionados)].copy()

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

# Dashboard 2 — Perguntas 3 e 4

elif pagina == "Movimentações e Permanência":
    st.header("Movimentações e Permanência Institucional")
    st.markdown(
        "Este dashboard concentra os indicadores de entrada, saída, evasão, desligamento "
        "e estabilidade da permanência na instituição."
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

    mostrar_metricas_basicas(df_mov)

    st.subheader("Padrões sazonais e períodos críticos")
    if len(df_mov) > 0:
        df_q3_bar = (
            df_mov.groupby(["mes_numero", "mes", "movimentacao"], as_index=False)
            .agg(valor=("valor", "sum"))
            .sort_values("mes_numero")
        )
        fig_bar = px.bar(
            df_q3_bar,
            x="mes",
            y="valor",
            color="movimentacao",
            barmode="group",
            category_orders={"mes": MESES_ORDEM},
            title="Indicadores de movimentação por mês",
            labels={"mes": "Mês", "valor": "Quantidade", "movimentacao": "Indicador"},
            hover_data={"valor": True, "movimentacao": True},
        )
        fig_bar.update_layout(height=600)
        st.plotly_chart(fig_bar, use_container_width=True)

        df_q3_heat = (
            df_mov.groupby(["ano", "mes_numero", "mes"], as_index=False)
            .agg(total=("valor", "sum"))
            .sort_values(["ano", "mes_numero"])
        )
        fig_heat = px.density_heatmap(
            df_q3_heat,
            x="mes",
            y="ano",
            z="total",
            category_orders={"mes": MESES_ORDEM},
            title="Heatmap de períodos críticos de movimentação",
            labels={"mes": "Mês", "ano": "Ano", "total": "Total"},
        )
        fig_heat.update_layout(height=500)
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Nenhum indicador de movimentação encontrado para os filtros selecionados.")

    st.divider()

    st.subheader("Estabilidade da permanência")
    st.caption(
        "Observação: como a base é agregada, o fluxo representa volumes consolidados por ano, "
        "não trajetórias individuais de crianças ou adolescentes."
    )

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

        # Índice simples entre 0 e 1. Quanto mais próximo de 1, menor o peso relativo das saídas, evasões e desligamentos.
        # Essa fórmula evita o gráfico zerado quando a base não possui um indicador explícito de permanência.
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

# Dashboard 3 — Perguntas 5 e 6

else:
    st.header("Indicadores Institucionais e Atividades de 2025")
    st.markdown(
        "Este dashboard compara indicadores de saúde e educação com o número de acolhidos "
        "e analisa a distribuição das atividades realizadas em 2025."
    )

    st.subheader("Acolhidos x saúde e educação")
    df_q5 = df.copy()
    df_q5["grupo_analise"] = df_q5.apply(classificar_grupo_q5, axis=1)
    df_q5 = df_q5[df_q5["grupo_analise"].notna()].copy()
    st.markdown("### Filtros")
    df_q5, anos_q5 = aplicar_filtro_anos(df_q5, "Anos")

    grupos_disponiveis = sorted(df_q5["grupo_analise"].dropna().unique())
    grupos_selecionados = st.multiselect("Grupos de análise", grupos_disponiveis, default=grupos_disponiveis)
    df_q5 = df_q5[df_q5["grupo_analise"].isin(grupos_selecionados)].copy()

    mostrar_metricas_basicas(df_q5)

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
        fig_indice.update_xaxes(tickmode="array", tickvals=sorted(df_q5_indice["ano"].dropna().unique()), ticktext=[str(int(a)) for a in sorted(df_q5_indice["ano"].dropna().unique())])
        fig_indice.update_layout(height=550, hovermode="x unified")
        st.plotly_chart(fig_indice, use_container_width=True)
    else:
        st.info("Nenhum registro encontrado com os filtros atuais.")

    st.divider()

    st.subheader("Distribuição e alcance das atividades de 2025")
    df_q6 = df[df["ano"] == 2025].copy()
    df_q6["tipo_atividade"] = df_q6.apply(classificar_tipo_atividade_q6, axis=1)
    df_q6["metrica_q6"] = df_q6.apply(classificar_metrica_q6, axis=1)
    df_q6["atividade"] = df_q6["indicador_completo"].fillna(df_q6["indicador"]).astype(str)
    df_q6 = df_q6[df_q6["tipo_atividade"].notna()].copy()

    if len(df_q6) > 0:
        metricas_base = sorted(df_q6["metrica_q6"].dropna().unique())
        ordem_metricas = ["Número de Participantes", "Carga Horária Total", "Quantidade de Eventos Realizados"]
        metricas_disponiveis = [m for m in ordem_metricas if m in metricas_base]
        if not metricas_disponiveis:
            metricas_disponiveis = metricas_base

        metrica_q6 = st.radio("Métrica do treemap", metricas_disponiveis, index=0)

        tipos_q6 = sorted(df_q6["tipo_atividade"].dropna().unique())
        tipos_q6_selecionados = st.multiselect("Tipos de atividade", tipos_q6, default=tipos_q6)

        df_q6_filtrado = df_q6[
            (df_q6["metrica_q6"] == metrica_q6)
            & (df_q6["tipo_atividade"].isin(tipos_q6_selecionados))
        ].copy()

        df_treemap = (
            df_q6_filtrado.groupby(["tipo_atividade", "atividade"], as_index=False)
            .agg(valor=("valor", "sum"))
            .sort_values("valor", ascending=False)
        )
        df_treemap = df_treemap[df_treemap["valor"] > 0]

        if len(df_treemap) > 0:
            fig_tree = px.treemap(
                df_treemap,
                path=["tipo_atividade", "atividade"],
                values="valor",
                title=f"Treemap das atividades de 2025 — {metrica_q6}",
                hover_data={"valor": True},
            )
            fig_tree.update_layout(height=700)
            st.plotly_chart(fig_tree, use_container_width=True)
        else:
            st.info("Existem registros para 2025, mas todos os valores da métrica selecionada são zero.")

        df_q6_mes = (
            df_q6_filtrado.groupby(["mes_numero", "mes", "tipo_atividade"], as_index=False)
            .agg(valor=("valor", "sum"))
            .sort_values("mes_numero")
        )
        df_q6_mes = df_q6_mes[df_q6_mes["valor"] > 0]

        if len(df_q6_mes) > 0:
            fig_mes = px.bar(
                df_q6_mes,
                x="mes",
                y="valor",
                color="tipo_atividade",
                barmode="group",
                category_orders={"mes": MESES_ORDEM},
                title=f"Distribuição mensal das atividades de 2025 — {metrica_q6}",
                labels={"mes": "Mês", "valor": metrica_q6, "tipo_atividade": "Tipo de atividade"},
            )
            fig_mes.update_layout(height=600)
            st.plotly_chart(fig_mes, use_container_width=True)
    else:
        st.info("Nenhum registro de atividade encontrado para 2025 com as palavras-chave atuais.")

st.caption("Fonte: base tratada lem_consolidado_2021_2025.csv")
