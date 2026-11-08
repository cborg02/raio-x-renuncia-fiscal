"""Leitura dos agregados e formatação comum às páginas do painel."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

DADOS = Path(__file__).resolve().parent / "dados"

COR_PRINCIPAL = "#1f5f8b"
COR_IMPORTACAO = "#8fb8d6"
COR_DESTAQUE = "#c8553d"


def numero_br(v: float, casas: int = 1) -> str:
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def bi(v: float, casas: int = 1) -> str:
    return f"R$ {numero_br(v / 1e9, casas)} bi"


def inteiro(v) -> str:
    return f"{int(v):,}".replace(",", ".")


@st.cache_data
def kpis() -> dict:
    return json.loads((DADOS / "kpis.json").read_text(encoding="utf-8"))


@st.cache_data
def tabela(nome: str) -> pd.DataFrame:
    return pd.read_parquet(DADOS / f"{nome}.parquet")


def configurar(titulo: str) -> None:
    st.markdown(
        """<style>
        div[data-testid="stMetric"] {background: rgba(31,95,139,0.06); border-left: 4px solid #1f5f8b;
             padding: 0.8rem 1rem; border-radius: 6px;}
        div[data-testid="stMetricValue"] {font-size: 1.9rem;}
        .nota {font-size: 0.85rem; color: #5b6770;}
        @media (max-width: 640px) { h1 {font-size: 1.7rem !important; line-height: 1.25 !important;} }
        </style>""",
        unsafe_allow_html=True,
    )
    with st.sidebar:
        st.markdown("### Raio-X da Renúncia Fiscal Federal 2025")
        st.caption("MVP do Projeto Aplicado · Pós-graduação em Ciência de Dados (XP Educação)")
        st.caption("Versão da Sprint 1 · protótipo")


def rodape() -> None:
    k = kpis()
    st.divider()
    st.markdown(
        f"<p class='nota'>Fonte: Receita Federal, DIRBI 2025 (dados abertos), extração de {k['data_extracao']}; "
        f"tabelas geradas em {k['gerado_em']}. Valores autodeclarados e sujeitos a retificação. "
        "Usufruir de benefício fiscal é legal e não indica irregularidade.</p>",
        unsafe_allow_html=True,
    )
