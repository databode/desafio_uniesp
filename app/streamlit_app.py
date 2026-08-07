from __future__ import annotations

import os
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def db_path() -> Path:
    return Path(os.getenv("DATA_ROOT", "./data")) / "semantic" / "uniesp.duckdb"


@st.cache_data(ttl=30)
def query(sql: str) -> pd.DataFrame:
    path = db_path()
    if not path.exists():
        return pd.DataFrame()
    with duckdb.connect(str(path), read_only=True) as con:
        return con.execute(sql).fetchdf()


def money(value) -> str:
    if pd.isna(value):
        return "-"
    return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main() -> None:
    st.set_page_config(page_title="UNIESP Mini Data Platform", layout="wide")
    st.title("UNIESP MBA — Mini Data Platform")
    st.caption("Streamlit consome somente views da Semantic Layer em DuckDB.")

    if not db_path().exists():
        st.warning("Semantic database not found. Run the Dagster full refresh or `python scripts/run_pipeline.py` first.")
        st.code("python scripts/run_pipeline.py")
        return

    tabs = st.tabs(["Overview", "Municípios", "Unidades Gestoras", "Cargos", "Data Quality", "About / Architecture"])

    with tabs[0]:
        overview = query("SELECT * FROM semantic.vw_overview")
        if overview.empty:
            st.error("semantic.vw_overview returned no rows.")
        else:
            row = overview.iloc[0]
            cols = st.columns(6)
            cols[0].metric("Registros", f"{int(row.quantidade_registros):,}".replace(",", "."))
            cols[1].metric("Municípios", int(row.municipios_distintos))
            cols[2].metric("Unidades", int(row.unidades_gestoras_distintas))
            cols[3].metric("Matrículas distintas", int(row.matriculas_distintas))
            cols[4].metric("Valor vantagem total", money(row.valor_vantagem_total))
            cols[5].metric("Última competência", row.ultima_competencia)
            st.caption("Matrículas distintas não significa pessoas distintas; nenhuma chave natural de pessoa foi confirmada.")
        evolucao = query("SELECT * FROM semantic.vw_evolucao_mensal")
        if not evolucao.empty:
            st.subheader("Comparação entre competências")
            st.bar_chart(evolucao.set_index("ano_mes")["valor_vantagem_total"])

    with tabs[1]:
        st.subheader("Agregação por município")
        municipios = query("SELECT * FROM semantic.vw_municipios ORDER BY valor_vantagem_total DESC")
        if not municipios.empty:
            st.dataframe(municipios.head(30), use_container_width=True)
            st.bar_chart(municipios.head(15).set_index("nome_municipio")["valor_vantagem_total"])

    with tabs[2]:
        st.subheader("Unidades Gestoras")
        unidades = query("SELECT * FROM semantic.vw_unidades_gestoras ORDER BY valor_vantagem_total DESC")
        if not unidades.empty:
            municipios = ["Todos"] + sorted(unidades["nome_municipio"].dropna().unique().tolist())
            selected = st.selectbox("Filtrar município", municipios)
            shown = unidades if selected == "Todos" else unidades[unidades["nome_municipio"] == selected]
            st.dataframe(shown.head(50), use_container_width=True)

    with tabs[3]:
        st.subheader("Cargos e tipos de cargo")
        cargos = query("SELECT * FROM semantic.vw_cargos ORDER BY quantidade_registros DESC")
        if not cargos.empty:
            by_tipo = cargos.groupby("tipo_cargo", as_index=False).agg({"quantidade_registros": "sum", "valor_vantagem_total": "sum"})
            st.bar_chart(by_tipo.set_index("tipo_cargo")["quantidade_registros"])
            st.dataframe(cargos.head(50), use_container_width=True)

    with tabs[4]:
        st.subheader("Data Quality")
        dq = query("SELECT * FROM semantic.vw_data_quality")
        if dq.empty:
            st.warning("No DQ report available.")
        else:
            st.dataframe(dq, use_container_width=True)
            st.caption("Datas futuras são tratadas como warning para discussão em sala, não como erro fatal.")

    with tabs[5]:
        st.subheader("Arquitetura")
        st.code("SOURCE → RAW → BRONZE → SILVER → GOLD → SEMANTIC → CONSUMPTION")
        st.code("DAGSTER = orchestration + observability over the assets")
        st.markdown(
            """
- **Raw** preserva o arquivo recebido.
- **Bronze** cria Parquet técnico e metadados.
- **Silver** limpa, tipa e gera relatório de qualidade.
- **Gold** organiza fatos, dimensões e marts.
- **Semantic Layer** expõe views estáveis no DuckDB.
- **Streamlit** consulta somente a Semantic Layer.
- **Dagster** não é uma camada de dados; ele coordena execução, dependências e observabilidade.
            """
        )


if __name__ == "__main__":
    main()
