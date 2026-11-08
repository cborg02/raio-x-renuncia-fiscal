"""Ponto de entrada do painel Raio-X da Renúncia Fiscal Federal 2025 (Streamlit)."""
import streamlit as st

st.set_page_config(page_title="Raio-X da Renúncia Fiscal 2025", page_icon="📊", layout="wide")
nav = st.navigation([
    st.Page("paginas/visao_geral.py", title="Visão geral", icon=":material/dashboard:", default=True),
    st.Page("paginas/entenda.py", title="Entenda a renúncia fiscal", icon=":material/menu_book:"),
])
nav.run()
