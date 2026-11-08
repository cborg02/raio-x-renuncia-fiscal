"""R04 - Dicionário de dados da base analítica e notas metodológicas.

Combina a descrição de cada campo (origem e transformação) com estatísticas medidas
na base tratada (tipo, % preenchido, valores distintos, exemplo). Gera docs/dicionario_dados.md.
"""
from __future__ import annotations

import duckdb

from comum import conectar, DOCS, TRATADOS, agora, inteiro, pct, titulo

# campo: (descrição, origem, transformação)
CAMPOS = {
    "cnpj": ("CNPJ do estabelecimento declarante (14 dígitos)", "DIRBI - CNPJ", "Texto; removida pontuação; 222 registros mascarados pela RFB mantidos"),
    "cnpj_raiz": ("Raiz do CNPJ (8 dígitos) - identifica a empresa", "Derivado de cnpj", "8 primeiros caracteres; nulo quando mascarado"),
    "cnpj_mascarado": ("Indica CNPJ ocultado pela própria RFB", "Derivado de cnpj", "Verdadeiro se contém '*'"),
    "matriz": ("Indica estabelecimento matriz (ordem 0001)", "Derivado de cnpj", "Posições 9-12 = '0001'"),
    "nome": ("Razão social do declarante", "DIRBI - Nome", "Sem alteração; 'CNPJ não divulgado' quando mascarado"),
    "municipio": ("Município da sede declarante, como publicado", "DIRBI - Município", "Sem alteração"),
    "municipio_norm": ("Município normalizado para junção", "Derivado de municipio", "Caixa alta, sem acento, só letras e números"),
    "cod_municipio_ibge": ("Código IBGE do município (7 dígitos)", "IBGE - Localidades", "Junção por municipio_norm + UF"),
    "uf": ("UF da sede declarante (não indica onde a atividade ocorreu)", "DIRBI - UF", "Caixa alta"),
    "uf_nome": ("Nome da UF", "IBGE - Localidades", "Junção por UF"),
    "regiao": ("Grande região", "IBGE - Localidades", "Junção por UF"),
    "cnae": ("CNAE principal - subclasse (7 dígitos)", "DIRBI - Cnae", "Texto; LPAD 7 com zeros"),
    "cnae_subclasse_desc": ("Descrição da subclasse CNAE", "IBGE/Concla - CNAE 2.3", "Junção por cnae"),
    "cnae_divisao": ("Divisão CNAE (2 dígitos)", "IBGE/Concla - CNAE 2.3", "Junção por cnae"),
    "cnae_divisao_desc": ("Descrição da divisão CNAE", "IBGE/Concla - CNAE 2.3", "Junção por cnae"),
    "cnae_secao": ("Seção CNAE (letra A-U)", "IBGE/Concla - CNAE 2.3", "Junção por cnae"),
    "cnae_secao_desc": ("Descrição da seção CNAE", "IBGE/Concla - CNAE 2.3", "Junção por cnae"),
    "ano": ("Ano de apuração", "DIRBI - Ano", "Inteiro"),
    "mes": ("Mês de apuração (1-12)", "DIRBI - Mês", "Inteiro (o dicionário da RFB indica dd/mm/aaaa, mas o arquivo traz 1-12)"),
    "competencia": ("Primeiro dia do mês de apuração", "Derivado de ano e mes", "make_date(ano, mes, 1)"),
    "codigo_beneficio": ("Item do Anexo Único da IN RFB nº 2.198/2024", "DIRBI - Código_IN", "Inteiro"),
    "beneficio": ("Nome do benefício fiscal", "Tabela de benefícios (IN RFB nº 2.241/2024)", "Junção por código; 'Não identificado' se ausente"),
    "tributo": ("Tributo desonerado, como publicado", "DIRBI - Tributo", "Sem alteração"),
    "tributo_grupo": ("Tributo sem a distinção '- Importação'", "Derivado de tributo", "Usado só na comparação com o DGT (R13)"),
    "tributo_importacao": ("Indica tributo incidente na importação", "Derivado de tributo", "Verdadeiro se contém 'Importação'"),
    "valor": ("Valor do benefício usufruído no mês (R$)", "DIRBI - Valor", "Texto com vírgula decimal convertido para DECIMAL(18,2)"),
}

NOTAS = [
    "**Unidade de análise:** cada registro é a combinação CNPJ × mês × código de benefício × tributo (chave única verificada no R02).",
    "**Empresa = raiz do CNPJ.** Contagens e concentração usam os 8 primeiros dígitos; filiais (0,35% dos registros) são somadas à empresa.",
    "**CNPJ mascarado pela RFB:** mantido em todos os totais como \"CNPJ não divulgado\" e excluído de rankings e medidas de concentração.",
    "**Localização pela sede (restrição R5):** UF e município são os do CNPJ declarante. Ex.: Vale e Salobo aparecem no RJ, embora o benefício "
    "Sudam/Sudene (código 20, redução de 75% do IRPJ) esteja ligado a operações nas regiões Norte e Nordeste.",
    "**Cobertura (restrição R4):** a DIRBI recebe apenas declarações de pessoas jurídicas; não inclui Simples Nacional, MEI, pessoas físicas nem benefícios fora do Anexo Único. "
    "Por isso o total (~R$ 366,5 bi) corresponde a cerca de 67% do DGT 2025 (R$ 543,6 bi); a razão é diferença de cobertura, não erro.",
    "**Lista de benefícios (restrição R6):** em 2025 vigorou o Anexo Único com 88 itens (IN RFB nº 2.241/2024). A ampliação para 173 itens "
    "(IN RFB nº 2.294/2025) vale para períodos de apuração a partir de janeiro de 2026 (art. 3º). Ainda assim, 7 códigos da nova lista "
    "(92, 105, 115, 116, 117, 118 e 128) aparecem em 2025, com 303 registros e R$ 2,2 milhões (valor residual).",
    "**Sazonalidade de IRPJ e CSLL:** concentram-se em março, junho, setembro e, sobretudo, dezembro (apuração trimestral/anual); "
    "não é mudança de política. A série mensal (R14) separa ou anota esses tributos.",
    "**Fim do Perse:** o encerramento do benefício (código 1) foi anunciado a partir de abril de 2025, mas o código aparece nos 12 meses; a evolução mensal é analisada no R14.",
    "**Natureza dos dados (R7):** valores autodeclarados e sujeitos a retificação; a análise refere-se à extração registrada no manifesto.",
    "**Ética (R8):** usufruir de benefício fiscal é legal e não indica irregularidade.",
    "**População e PIB:** último ano disponível no IBGE (ver colunas ano_populacao e ano_pib em ref_uf); a diferença de ano-base é declarada no painel (premissa P5).",
]


def main() -> None:
    titulo("R04 - Dicionário de dados")
    con = conectar()
    con.execute(f"CREATE VIEW t AS SELECT * FROM read_parquet('{(TRATADOS / 'dirbi_2025_tratada.parquet').as_posix()}')")
    info = con.execute("DESCRIBE t").fetchall()
    n = con.execute("SELECT COUNT(*) FROM t").fetchone()[0]
    L = ["# Dicionário de dados - base analítica DIRBI 2025 (R04)", "",
         f"Gerado em {agora()} por `pipeline/p04_dicionario.py`. Base: `dados/tratados/dirbi_2025_tratada.parquet` "
         f"({inteiro(n)} registros, {len(info)} campos).", "",
         "| # | Campo | Tipo | Descrição | Origem | Transformação | % preenchido | Distintos | Exemplo |",
         "|---|---|---|---|---|---|---|---|---|"]
    sem_desc = []
    for i, (col, tipo, *_r) in enumerate(info, 1):
        preench, dist = con.execute(f'SELECT COUNT("{col}"), COUNT(DISTINCT "{col}") FROM t').fetchone()
        ex = con.execute(f'SELECT "{col}" FROM t WHERE "{col}" IS NOT NULL AND NOT COALESCE(cnpj_mascarado, false) LIMIT 1').fetchone()
        ex = "" if ex is None else str(ex[0])[:40]
        d, o, tr = CAMPOS.get(col, ("(sem descrição)", "", ""))
        if col not in CAMPOS:
            sem_desc.append(col)
        L.append(f"| {i} | `{col}` | {tipo} | {d} | {o} | {tr} | {pct(preench/n, 2)} | {inteiro(dist)} | {ex} |")
    L += ["", "## Notas metodológicas", ""] + [f"{i}. {t}" for i, t in enumerate(NOTAS, 1)]
    L += ["", "## Tabelas pré-agregadas do painel (`app/dados/`)", "",
          "| Arquivo | Granularidade | Uso |", "|---|---|---|",
          "| `kpis.json` | Ano | Cartões da visão geral (R05) |",
          "| `agg_tributo.parquet` | Tributo | Participação por tributo (R05/H6) |",
          "| `agg_mes_tributo.parquet` | Mês × tributo | Série mensal (R14) |",
          "| `agg_beneficio.parquet` | Código de benefício | Ranking e Pareto (R12), LC 224 (R08/R15) |",
          "| `agg_uf.parquet` | UF | Mapa e normalização (R10) |",
          "| `agg_cnae_divisao.parquet` | Seção × divisão CNAE | Visão setorial (R11) |",
          "| `agg_empresa.parquet` | Raiz do CNPJ (sem mascarados) | Concentração (R09) |"]
    (DOCS / "dicionario_dados.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{len(info)} campos documentados ({len(info) - len(sem_desc)} com descrição completa). Sem descrição: {sem_desc or 'nenhum'}")
    print("Dicionário gravado em docs/dicionario_dados.md")
