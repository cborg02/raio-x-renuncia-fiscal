"""Funções e caminhos comuns ao pipeline da Sprint 1 (Raio-X da Renúncia Fiscal Federal 2025)."""
from __future__ import annotations

import datetime as dt
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BRUTOS = RAIZ / "dados" / "brutos"          # fora do Git (ver .gitignore)
TRATADOS = RAIZ / "dados" / "tratados"      # fora do Git
APP_DADOS = RAIZ / "app" / "dados"          # agregados pequenos, versionados
DOCS = RAIZ / "docs"
REFS = RAIZ / "referencias"
LOGS = RAIZ / "logs"
for p in (BRUTOS, TRATADOS, APP_DADOS, DOCS, LOGS):
    p.mkdir(parents=True, exist_ok=True)

# nomes padronizados, na ordem das colunas do arquivo da RFB
COLUNAS = ["cnpj", "nome", "municipio", "uf", "cnae", "mes", "ano", "codigo_in", "tributo", "valor"]

TOTAL_PERFIL_30OUT = 366.5e9   # total encontrado no perfilamento de 30/10/2026 (R$)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def agora() -> str:
    return dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def titulo(txt: str) -> None:
    print("\n" + "=" * 78)
    print(f"[{agora()}] {txt}")
    print("=" * 78)


def normaliza_nome(s: str | None) -> str | None:
    """Caixa alta, sem acento, só letras/números e espaços simples (para juntar municípios)."""
    if s is None:
        return None
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    s = "".join(ch if ch.isalnum() else " " for ch in s.upper())
    return " ".join(s.split())


def brl(v: float) -> str:
    """Formata em reais no padrão brasileiro."""
    v = float(v)
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def bi(v: float) -> str:
    v = float(v)
    return f"R$ {v/1e9:,.1f} bi".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(v: float, casas: int = 1) -> str:
    v = float(v)
    return f"{v*100:.{casas}f}%".replace(".", ",")


def inteiro(v) -> str:
    return f"{int(v):,}".replace(",", ".")


def conectar():
    """Conexão DuckDB econômica em memória RAM: limite fixo, poucas threads e temporários no drive do projeto.

    O limite pode ser ajustado pela variável de ambiente DUCKDB_MEMORIA (ex.: 1GB, 3GB).
    """
    import os
    import duckdb
    tmp = TRATADOS / "tmp_duckdb"
    tmp.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"SET temp_directory = '{tmp.as_posix()}'")
    con.execute(f"SET memory_limit = '{os.environ.get('DUCKDB_MEMORIA', '2GB')}'")
    con.execute("SET threads = 2")
    con.execute("SET enable_progress_bar = false")
    con.execute("SET preserve_insertion_order = false")
    return con
