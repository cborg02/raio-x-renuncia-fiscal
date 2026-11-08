"""Executa o pipeline da Sprint 1 (R01 a R05 e insumo do R08) e grava o log.

Uso (PowerShell, na pasta do repositório):
    python pipeline\\executar_sprint1.py --csv "C:\\caminho\\para\\2025.csv" --data-extracao 30/10/2026

Ao final, é criado o arquivo entrega_sprint1.zip (somente documentos, logs e agregados pequenos).
"""
from __future__ import annotations

import argparse
import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from comum import APP_DADOS, BRUTOS, DOCS, LOGS, RAIZ, agora  # noqa: E402


class Tee:
    def __init__(self, *s):
        self.s = s

    def write(self, x):
        for s in self.s:
            s.write(x)
            s.flush()

    def flush(self):
        for s in self.s:
            s.flush()


def main() -> None:
    ap = argparse.ArgumentParser(description="Pipeline da Sprint 1 - Raio-X da Renúncia Fiscal Federal 2025")
    ap.add_argument("--csv", required=True, help="caminho do 2025.csv da DIRBI")
    ap.add_argument("--data-extracao", default="30/10/2026", help="data em que o arquivo foi baixado da RFB")
    a = ap.parse_args()

    log = open(LOGS / "sprint1_execucao.log", "w", encoding="utf-8")
    sys.stdout = Tee(sys.__stdout__, log)
    t0 = time.time()
    print(f"Raio-X da Renúncia Fiscal Federal 2025 - pipeline da Sprint 1 | início {agora()}")
    print(f"Python {sys.version.split()[0]} | pasta {RAIZ}")
    import duckdb
    import pandas
    print(f"duckdb {duckdb.__version__} | pandas {pandas.__version__}")

    import p01_coleta, p02_perfil, p03_tratamento, p04_dicionario, p05_agregados  # noqa: E401
    etapas = {}
    for nome, f in [("R01 coleta", lambda: p01_coleta.main(a.csv, a.data_extracao)),
                    ("R02 perfil", lambda: p02_perfil.main(str(Path(a.csv).expanduser().resolve()))),
                    ("R03 tratamento", p03_tratamento.main),
                    ("R04 dicionário", p04_dicionario.main),
                    ("R05/R08 agregados", lambda: p05_agregados.main(a.data_extracao))]:
        t = time.time()
        f()
        etapas[nome] = time.time() - t

    print("\n" + "=" * 78)
    print("RESUMO DA EXECUÇÃO")
    for n, s in etapas.items():
        print(f"  {n:<20} {s:7.1f} s")
    print(f"  {'TOTAL':<20} {time.time()-t0:7.1f} s | fim {agora()}")
    sys.stdout = sys.__stdout__
    log.close()

    zp = RAIZ / "entrega_sprint1.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for pasta in (DOCS, APP_DADOS, LOGS):
            for p in pasta.rglob("*"):
                if p.is_file():
                    z.write(p, p.relative_to(RAIZ))
        z.write(BRUTOS / "manifesto_coleta.csv", "dados/brutos/manifesto_coleta.csv")
    print(f"\nPronto. Envie no chat o arquivo: {zp}  ({zp.stat().st_size/1024/1024:.1f} MB)")


if __name__ == "__main__":
    main()
