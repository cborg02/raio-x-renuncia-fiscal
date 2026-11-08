"""R01 - Coleta e registro das bases (DIRBI 2025 + bases complementares).

- Registra o arquivo anual da DIRBI 2025 (tamanho, SHA-256, data de extração), sem copiá-lo para o repositório.
- Baixa as bases complementares do IBGE (CNAE 2.3, municípios, população, PIB) e o DGT 2025 da RFB.
- Registra as referências normativas montadas pelo autor (tabela de benefícios e classificação LC 224/2025).
- Grava o manifesto em dados/brutos/manifesto_coleta.csv e docs/manifesto_coleta.md.
"""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import time
from pathlib import Path

from comum import BRUTOS, DOCS, REFS, agora, inteiro, titulo

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

URLS = {
    "cnae_subclasses.json": "https://servicodados.ibge.gov.br/api/v2/cnae/subclasses",
    "municipios_ibge.json": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios?view=nivelado",
    "populacao_uf_sidra6579.json": "https://apisidra.ibge.gov.br/values/t/6579/n3/all/v/9324/p/last%201",
    "populacao_municipio_sidra6579.json": "https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/last%201",
    "pib_uf_sidra5938.json": "https://apisidra.ibge.gov.br/values/t/5938/n3/all/v/37/p/last%201",
    "dgt_2025.pdf": "https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/relatorios/renuncia/gastos-tributarios-ploa/dgt-previsao-ploa-2025-base-conceitual.pdf",
    "dgt_2025_quadros.xlsx": "https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/relatorios/renuncia/gastos-tributarios-ploa/dgt-previsao-ploa-2025-quadros.xlsx",
}

DESCRICAO = {
    "cnae_subclasses.json": ("Estrutura da CNAE 2.3 (subclasse > classe > grupo > divisão > seção)", "IBGE/Concla - API de serviços de dados"),
    "municipios_ibge.json": ("Cadastro de municípios (código, nome, UF)", "IBGE - API de localidades"),
    "populacao_uf_sidra6579.json": ("População residente estimada por UF (último ano)", "IBGE/SIDRA - Tabela 6579"),
    "populacao_municipio_sidra6579.json": ("População residente estimada por município (último ano)", "IBGE/SIDRA - Tabela 6579"),
    "pib_uf_sidra5938.json": ("PIB a preços correntes por UF (último ano, mil R$)", "IBGE/SIDRA - Tabela 5938 (Contas Regionais)"),
    "dgt_2025.pdf": ("Demonstrativo dos Gastos Tributários - PLOA 2025 (relatório)", "Receita Federal"),
    "dgt_2025_quadros.xlsx": ("Demonstrativo dos Gastos Tributários - PLOA 2025 (quadros por tributo e função)", "Receita Federal"),
    "tabela_beneficios_dirbi.csv": ("Tabela de benefícios da DIRBI (código, nome, tributos)", "IN RFB nº 2.198/2024, Anexo Único (IN RFB nº 2.241/2024)"),
    "lc224_classificacao_preliminar.csv": ("Classificação preliminar dos benefícios pela LC nº 224/2025", "LC nº 224/2025 (elaborada pelo autor)"),
}


def sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


def baixar(nome: str, url: str) -> tuple[str, str]:
    destino = BRUTOS / nome
    if destino.exists() and destino.stat().st_size > 0:
        return "já existia", f"{destino.stat().st_size:,} bytes"
    if requests is None:
        return "FALHOU", "instale 'requests'"
    for tentativa in range(1, 4):
        try:
            r = requests.get(url, timeout=120, headers={"User-Agent": "raio-x-renuncia-fiscal/1.0"})
            r.raise_for_status()
            if nome.endswith(".json"):
                json.loads(r.content.decode("utf-8"))  # valida o JSON
            elif nome.endswith(".pdf") and not r.content.startswith(b"%PDF"):
                raise ValueError("o conteúdo baixado não é um PDF")
            elif nome.endswith(".xlsx") and not r.content.startswith(b"PK"):
                raise ValueError("o conteúdo baixado não é uma planilha .xlsx")
            destino.write_bytes(r.content)
            return "baixado", f"{len(r.content):,} bytes"
        except Exception as e:  # noqa: BLE001
            erro = str(e)[:150]
            time.sleep(3 * tentativa)
    return "FALHOU", erro


def main(csv_dirbi: str, data_extracao: str) -> list[dict]:
    titulo("R01 - Coleta e registro das bases")
    manifesto: list[dict] = []

    arq = Path(csv_dirbi).expanduser().resolve()
    if not arq.exists():
        raise SystemExit(f"ERRO: arquivo da DIRBI não encontrado: {arq}")
    print(f"DIRBI 2025: {arq}")
    print("Calculando SHA-256 (pode levar alguns segundos)...")
    tam = arq.stat().st_size
    manifesto.append({
        "base": "DIRBI 2025 - renúncia por regime (arquivo anual, 12 meses)",
        "arquivo": arq.name, "fonte": "Receita Federal - Dados Abertos",
        "status": "registrado (fora do repositório)", "tamanho": f"{tam/1024/1024:,.1f} MB",
        "sha256": sha256(arq), "data_extracao": data_extracao, "registrado_em": agora(),
    })
    print(f"  tamanho: {tam/1024/1024:,.1f} MB | sha256: {manifesto[-1]['sha256'][:16]}...")

    for nome, url in URLS.items():
        status, info = baixar(nome, url)
        desc, fonte = DESCRICAO[nome]
        p = BRUTOS / nome
        manifesto.append({
            "base": desc, "arquivo": nome, "fonte": f"{fonte} - {url}", "status": status,
            "tamanho": info, "sha256": sha256(p) if p.exists() else "",
            "data_extracao": agora()[:10] if status == "baixado" else (data_extracao if status == "já existia" else ""),
            "registrado_em": agora(),
        })
        print(f"  [{status:^10}] {nome:<38} {info}")
        if status == "FALHOU":
            print(f"      -> baixe manualmente em {url} e salve como dados/brutos/{nome}")

    for nome in ("tabela_beneficios_dirbi.csv", "lc224_classificacao_preliminar.csv"):
        shutil.copy2(REFS / nome, BRUTOS / nome)
        desc, fonte = DESCRICAO[nome]
        with open(REFS / nome, encoding="utf-8") as f:
            n = sum(1 for _ in f) - 1
        manifesto.append({
            "base": desc, "arquivo": nome, "fonte": fonte, "status": "versionado em referencias/",
            "tamanho": f"{inteiro(n)} linhas", "sha256": sha256(REFS / nome),
            "data_extracao": "07/11/2026", "registrado_em": agora(),
        })
        print(f"  [versionado] {nome:<38} {n} linhas")

    campos = list(manifesto[0].keys())
    with open(BRUTOS / "manifesto_coleta.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(manifesto)

    linhas = ["# Manifesto de coleta (R01)", "", f"Gerado em {agora()} por `pipeline/p01_coleta.py`.", "",
              "| Base | Arquivo | Status | Tamanho | Data de extração | SHA-256 (início) |",
              "|---|---|---|---|---|---|"]
    for m in manifesto:
        linhas.append(f"| {m['base']} | `{m['arquivo']}` | {m['status']} | {m['tamanho']} | {m['data_extracao']} | `{m['sha256'][:12]}` |")
    linhas += ["", "Fontes:", ""] + [f"- `{m['arquivo']}`: {m['fonte']}" for m in manifesto]
    (DOCS / "manifesto_coleta.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")

    falhas = [m["arquivo"] for m in manifesto if m["status"] == "FALHOU"]
    ok = len(manifesto) - len(falhas)
    print(f"\nResumo R01: {ok}/{len(manifesto)} bases registradas" + (f" | FALHAS: {falhas}" if falhas else ""))
    return manifesto
