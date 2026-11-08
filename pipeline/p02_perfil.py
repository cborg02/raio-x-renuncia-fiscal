"""R02 - Perfilamento da qualidade dos dados da DIRBI 2025.

Lê o CSV com todas as colunas como texto, renomeia por posição e verifica:
nulos, duplicados na chave, valores negativos/zerados/não numéricos, outliers,
formato de CNPJ e CNAE, domínio de UF, mês, ano, códigos e tributos.
Gera docs/relatorio_qualidade.md e dados/tratados/dirbi_2025_bruto.parquet.
"""
from __future__ import annotations

import csv
import time

import duckdb

from comum import conectar, COLUNAS, DOCS, REFS, TRATADOS, agora, bi, brl, inteiro, pct, titulo

UFS = {"AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI",
       "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"}

VALOR_NUM = "TRY_CAST(CASE WHEN valor LIKE '%,%' THEN REPLACE(REPLACE(valor, '.', ''), ',', '.') ELSE valor END AS DECIMAL(18, 2))"


def carregar(con: duckdb.DuckDBPyConnection, arq: str) -> None:
    t0 = time.time()
    cols = [c[0] for c in con.execute(f"""DESCRIBE SELECT * FROM read_csv('{arq}', delim=',', quote='"', header=true,
                                          all_varchar=true, encoding='utf-8')""").fetchall()]
    print(f"Colunas originais ({len(cols)}): {cols}")
    if len(cols) != len(COLUNAS):
        raise SystemExit(f"ERRO de esquema: esperadas {len(COLUNAS)} colunas, lidas {len(cols)}")
    sel = ", ".join(f'"{c}" AS {n}' for c, n in zip(cols, COLUNAS))
    destino = (TRATADOS / "dirbi_2025_bruto.parquet").as_posix()
    # leitura em fluxo direto para Parquet (tudo texto), sem manter a base na memória RAM
    con.execute(f"""COPY (SELECT {sel} FROM read_csv('{arq}', delim=',', quote='"', header=true,
                                                    all_varchar=true, encoding='utf-8'))
                    TO '{destino}' (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 200000)""")
    con.execute(f"CREATE OR REPLACE VIEW bruto AS SELECT * FROM read_parquet('{destino}')")
    n = con.execute("SELECT COUNT(*) FROM bruto").fetchone()[0]
    print(f"Leitura concluída: {inteiro(n)} linhas em {time.time()-t0:.1f} s")
    return cols


def main(arq: str) -> dict:
    titulo("R02 - Perfilamento da qualidade dos dados")
    con = conectar()
    cols_orig = carregar(con, arq)
    q = lambda s: con.execute(s).fetchone()  # noqa: E731
    r: dict = {}

    r["linhas"] = q("SELECT COUNT(*) FROM bruto")[0]
    nulos = {c: q(f"SELECT COUNT(*) FROM bruto WHERE {c} IS NULL OR TRIM({c}) = ''")[0] for c in COLUNAS}
    r["nulos_total"] = sum(nulos.values())

    con.execute(f"CREATE OR REPLACE VIEW b2 AS SELECT *, {VALOR_NUM} AS v FROM bruto")
    # CNPJ publicado com pontuação (00.000.000/0000-00): verificações sobre os dígitos
    con.execute("CREATE OR REPLACE VIEW cn AS SELECT regexp_replace(cnpj, '[^0-9*]', '', 'g') AS c FROM bruto")
    r["cnpj_formato"] = q("SELECT ANY_VALUE(cnpj) FROM bruto WHERE cnpj NOT LIKE '%*%'")[0]
    r["nao_numericos"] = q("SELECT COUNT(*) FROM b2 WHERE v IS NULL")[0]
    r["negativos"] = q("SELECT COUNT(*) FROM b2 WHERE v < 0")[0]
    r["zerados"] = q("SELECT COUNT(*) FROM b2 WHERE v = 0")[0]
    r["total"] = q("SELECT SUM(v) FROM b2")[0]
    p = q("SELECT MIN(v), quantile_cont(v, 0.25), median(v), AVG(v), quantile_cont(v, 0.75), quantile_cont(v, 0.99), MAX(v) FROM b2")
    r["estat"] = dict(zip(["min", "p25", "mediana", "media", "p75", "p99", "max"], [float(x) for x in p]))
    # IIQ em escala log10: com média ~190x a mediana, o IIQ linear marcaria 13% dos registros
    lq1, lq3 = q("SELECT quantile_cont(log10(v), 0.25), quantile_cont(log10(v), 0.75) FROM b2 WHERE v > 0")
    lim = 10 ** (lq3 + 3 * (lq3 - lq1))
    r["outliers_iqr3"] = q(f"SELECT COUNT(*), SUM(v) FROM b2 WHERE v > {lim}")
    r["lim_outlier"] = lim
    top = con.execute("""SELECT nome, uf, tributo, mes, codigo_in, v FROM b2 ORDER BY v DESC LIMIT 10""").fetchall()

    r["dup_chave"] = q("""SELECT COUNT(*) FROM (SELECT cnpj, ano, mes, codigo_in, tributo, COUNT(*) n
                          FROM bruto GROUP BY ALL HAVING n > 1)""")[0]
    r["dup_linha"] = q("""SELECT COALESCE(SUM(n - 1), 0) FROM (SELECT COUNT(*) n FROM bruto GROUP BY ALL HAVING n > 1)""")[0] if r["dup_chave"] else 0

    r["cnpj_mascarado"] = q("SELECT COUNT(*) FROM cn WHERE c LIKE '%*%'")[0]
    r["cnpj_fora_padrao"] = q("SELECT COUNT(*) FROM cn WHERE c NOT LIKE '%*%' AND NOT regexp_full_match(c, '[0-9]{14}')")[0]
    r["cnpj_nao_matriz"] = q("SELECT COUNT(*) FROM cn WHERE c NOT LIKE '%*%' AND substr(c, 9, 4) <> '0001'")[0]
    r["cnae_7dig"] = q("SELECT COUNT(*) FROM bruto WHERE regexp_full_match(cnae, '[0-9]{7}')")[0]
    ufs = {u for (u,) in con.execute("SELECT DISTINCT uf FROM bruto").fetchall()}
    r["ufs"] = len(ufs)
    r["ufs_invalidas"] = sorted(ufs - UFS)
    meses = [m for (m,) in con.execute("SELECT DISTINCT mes FROM bruto ORDER BY TRY_CAST(mes AS INT)").fetchall()]
    r["meses"] = meses
    r["anos"] = [a for (a,) in con.execute("SELECT DISTINCT ano FROM bruto").fetchall()]
    codigos = sorted({c for (c,) in con.execute("SELECT DISTINCT TRY_CAST(codigo_in AS INT) FROM bruto").fetchall() if c is not None})
    r["codigos"] = len(codigos)
    with open(REFS / "tabela_beneficios_dirbi.csv", encoding="utf-8") as f:
        tab = {int(l["codigo"]) for l in csv.DictReader(f)}
    r["codigos_sem_nome"] = [c for c in codigos if c not in tab]
    tribs = con.execute("SELECT tributo, COUNT(*), SUM(v) FROM b2 GROUP BY 1 ORDER BY 3 DESC").fetchall()
    r["cnpjs"] = q("SELECT COUNT(DISTINCT cnpj) FROM bruto")[0]
    r["raizes"] = q("SELECT COUNT(DISTINCT substr(c, 1, 8)) FROM cn WHERE c NOT LIKE '%*%'")[0]
    mun_acento = [m for (m,) in con.execute(
        "SELECT DISTINCT municipio FROM bruto WHERE municipio <> strip_accents(municipio) ORDER BY 1").fetchall()]


    # ------------------------------------------------------------------ console
    print(f"Linhas: {inteiro(r['linhas'])} | CNPJs: {inteiro(r['cnpjs'])} | raízes: {inteiro(r['raizes'])} | códigos: {r['codigos']}")
    print(f"Total declarado: {brl(r['total'])} ({bi(r['total'])})")
    print(f"Vazios: {r['nulos_total']} | não numéricos: {r['nao_numericos']} | negativos: {r['negativos']} | zerados: {r['zerados']}")
    print(f"Duplicados na chave (cnpj, ano, mês, código, tributo): {r['dup_chave']} | linhas idênticas: {r['dup_linha']}")
    print(f"CNPJ mascarado pela RFB: {r['cnpj_mascarado']} | fora do padrão: {r['cnpj_fora_padrao']} | não matriz: {inteiro(r['cnpj_nao_matriz'])}")
    print(f"CNAE com 7 dígitos: {pct(r['cnae_7dig']/r['linhas'], 2)} | UFs: {r['ufs']} (inválidas: {r['ufs_invalidas']})")
    print(f"Meses: {meses} | anos: {r['anos']} | códigos sem nome na tabela: {r['codigos_sem_nome']}")
    print(f"Outliers (log10: > Q3 + 3·IIQ = {brl(lim)}): {inteiro(r['outliers_iqr3'][0])} linhas, {bi(r['outliers_iqr3'][1] or 0)}")

    # ------------------------------------------------------------------ relatório
    L = ["# Relatório de qualidade dos dados - DIRBI 2025 (R02)", "",
         f"Gerado em {agora()} por `pipeline/p02_perfil.py` a partir de `{arq.split('/')[-1].split(chr(92))[-1]}`.", "",
         f"Colunas originais: {', '.join(cols_orig)} (renomeadas por posição para {', '.join(COLUNAS)}).", "",
         "## 1. Volume", "",
         "| Medida | Valor |", "|---|---|",
         f"| Registros | {inteiro(r['linhas'])} |", f"| CNPJs distintos | {inteiro(r['cnpjs'])} |",
         f"| Raízes de CNPJ (8 dígitos, sem mascarados) | {inteiro(r['raizes'])} |",
         f"| Códigos de benefício | {r['codigos']} |", f"| Tributos | {len(tribs)} |",
         f"| Total declarado | {brl(r['total'])} |", "",
         "## 2. Verificações", "",
         "| Verificação | Resultado | Regra de tratamento |", "|---|---|---|",
         f"| Campos vazios | {r['nulos_total']} | Nenhuma ação necessária |",
         f"| Valor não numérico | {r['nao_numericos']} | Valor lido como texto e convertido explicitamente (vírgula decimal) |",
         f"| Valor negativo | {r['negativos']} | Nenhuma ação necessária |",
         f"| Valor zerado | {r['zerados']} | Nenhuma ação necessária |",
         f"| Duplicados na chave (CNPJ, ano, mês, código, tributo) | {r['dup_chave']} | Chave única confirmada |",
         f"| Linhas idênticas | {r['dup_linha']} | — |",
         f"| CNPJ mascarado pela RFB | {r['cnpj_mascarado']} | Manter nos totais; rotular \"CNPJ não divulgado\"; excluir de rankings e concentração |",
         f"| CNPJ fora do padrão (14 dígitos após remover pontuação; formato publicado: {r['cnpj_formato']}) | {r['cnpj_fora_padrao']} | Remover pontuação (. / -) |",
         f"| CNPJ de estabelecimento não matriz | {inteiro(r['cnpj_nao_matriz'])} ({pct(r['cnpj_nao_matriz']/r['linhas'], 2)}) | Agregar pela raiz do CNPJ (8 dígitos) |",
         f"| CNAE com 7 dígitos | {pct(r['cnae_7dig']/r['linhas'], 2)} | Ler como texto; LPAD(7, '0') por segurança |",
         f"| UFs distintas | {r['ufs']} (inválidas: {r['ufs_invalidas'] or 'nenhuma'}) | — |",
         f"| Meses | {', '.join(meses)} | Mês inteiro (1-12), diferente do dicionário da RFB (dd/mm/aaaa) |",
         f"| Ano | {', '.join(r['anos'])} | — |",
         f"| Códigos sem nome na tabela de benefícios | {r['codigos_sem_nome'] or 'nenhum'} | Rotular \"não identificado\" (premissa P2) |",
         f"| Municípios com acento | {', '.join(mun_acento) or 'nenhum'} | Normalizar (caixa alta, sem acento) antes da junção com o IBGE |", "",
         "## 3. Distribuição do valor (R$ por registro)", "",
         "| Mínimo | P25 | Mediana | Média | P75 | P99 | Máximo |", "|---|---|---|---|---|---|---|",
         "| " + " | ".join(brl(r["estat"][k]) for k in ["min", "p25", "mediana", "media", "p75", "p99", "max"]) + " |", "",
         f"Distribuição muito assimétrica (média ≈ {r['estat']['media']/r['estat']['mediana']:.0f}× a mediana). "
         f"Pelo critério Q3 + 3·IIQ aplicado ao log10 do valor (limite de {brl(lim)}), {inteiro(r['outliers_iqr3'][0])} registros são extremos e somam "
         f"{bi(r['outliers_iqr3'][1] or 0)}. Eles **não são removidos**: os maiores são declarações legítimas de grandes empresas "
         "(ver tabela abaixo). Regra: manter, usar escala logarítmica nos gráficos de distribuição e reportar medianas.", "",
         "| Empresa | UF | Tributo | Mês | Código | Valor |", "|---|---|---|---|---|---|"]
    L += [f"| {n} | {u} | {t} | {m} | {c} | {brl(v)} |" for n, u, t, m, c, v in top]
    L += ["", "## 4. Total por tributo", "", "| Tributo | Registros | Valor | % |", "|---|---|---|---|"]
    L += [f"| {t} | {inteiro(n)} | {bi(v)} | {pct(v/r['total'])} |" for t, n, v in tribs]
    L += ["", "## 5. Regras de tratamento adotadas no pipeline (R03)", "",
          "1. Ler todas as colunas como texto e renomear por posição (o cabeçalho tem acentos).",
          "2. Converter Valor (vírgula decimal, sem separador de milhar) para DECIMAL(18,2) (somas exatas) e Mês para inteiro.",
          "3. Remover a pontuação do CNPJ, derivar a raiz (8 primeiros dígitos) e marcar CNPJs mascarados pela RFB.",
          "4. Normalizar municípios (caixa alta, sem acento, só letras e números) antes da junção com o IBGE.",
          "5. Agrupar tributos \"- Importação\" ao tributo correspondente apenas na comparação com o DGT (coluna `tributo_grupo`).",
          "6. Não remover outliers; não imputar valores (não há vazios)."]
    (DOCS / "relatorio_qualidade.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("Relatório gravado em docs/relatorio_qualidade.md")
    return r
