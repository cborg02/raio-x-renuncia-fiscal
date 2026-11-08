"""R03 - Tratamento e integração da DIRBI 2025 com as bases complementares.

Entrada: dados/tratados/dirbi_2025_bruto.parquet (gerado no R02) e dados/brutos/* (R01).
Saída:   dados/tratados/dirbi_2025_tratada.parquet, dados/tratados/ref_uf.parquet
         e docs/relatorio_integracao.md (taxas de correspondência e reconciliação).
"""
from __future__ import annotations

import json

import duckdb
import pandas as pd

from comum import conectar, BRUTOS, DOCS, REFS, TOTAL_PERFIL_30OUT, TRATADOS, agora, bi, brl, inteiro, normaliza_nome, pct, titulo

VALOR_NUM = "TRY_CAST(CASE WHEN valor LIKE '%,%' THEN REPLACE(REPLACE(valor, '.', ''), ',', '.') ELSE valor END AS DECIMAL(18, 2))"


def ler_sidra(nome: str, nivel: str) -> pd.DataFrame | None:
    """Converte o JSON da API SIDRA em (codigo, nome, ano, valor), localizando as dimensões pelo cabeçalho."""
    p = BRUTOS / nome
    if not p.exists():
        return None
    dados = json.loads(p.read_text(encoding="utf-8"))
    cab, linhas = dados[0], dados[1:]
    k_cod = next(k for k, v in cab.items() if k.endswith("C") and v.startswith(nivel))
    k_nom = k_cod[:-1] + "N"
    k_ano = next(k for k, v in cab.items() if k.endswith("N") and v.startswith("Ano"))
    df = pd.DataFrame([{"codigo": int(l[k_cod]), "nome": l[k_nom], "ano": int(l[k_ano]),
                        "valor": pd.to_numeric(l["V"], errors="coerce")} for l in linhas])
    return df


def carregar_referencias(con: duckdb.DuckDBPyConnection) -> dict:
    disp = {}
    # benefícios
    ben = pd.read_csv(REFS / "tabela_beneficios_dirbi.csv")
    con.register("ben_df", ben)
    con.execute("CREATE OR REPLACE TABLE ref_beneficio AS SELECT * FROM ben_df")
    disp["beneficios"] = len(ben)

    # CNAE 2.3
    p = BRUTOS / "cnae_subclasses.json"
    if p.exists():
        sub = json.loads(p.read_text(encoding="utf-8"))
        rows = []
        for s in sub:
            c = s["classe"]; g = c["grupo"]; d = g["divisao"]; se = d["secao"]
            rows.append({"cnae": str(s["id"]).zfill(7), "cnae_subclasse_desc": s["descricao"].strip(),
                         "cnae_divisao": str(d["id"]).zfill(2), "cnae_divisao_desc": d["descricao"].strip(),
                         "cnae_secao": se["id"], "cnae_secao_desc": se["descricao"].strip()})
        con.register("cnae_df", pd.DataFrame(rows))
        con.execute("CREATE OR REPLACE TABLE ref_cnae AS SELECT * FROM cnae_df")
        disp["cnae"] = len(rows)
    else:
        con.execute("""CREATE OR REPLACE TABLE ref_cnae (cnae VARCHAR, cnae_subclasse_desc VARCHAR, cnae_divisao VARCHAR,
                       cnae_divisao_desc VARCHAR, cnae_secao VARCHAR, cnae_secao_desc VARCHAR)""")
        disp["cnae"] = 0

    # municípios + população municipal
    p = BRUTOS / "municipios_ibge.json"
    if p.exists():
        mun = pd.DataFrame(json.loads(p.read_text(encoding="utf-8")))
        mun = pd.DataFrame({"cod_municipio_ibge": mun["municipio-id"].astype(int), "municipio_ibge": mun["municipio-nome"],
                            "uf": mun["UF-sigla"], "cod_uf": mun["UF-id"].astype(int), "uf_nome": mun["UF-nome"],
                            "regiao": mun["regiao-nome"]})
        mun["municipio_norm"] = mun["municipio_ibge"].map(normaliza_nome)
        popm = ler_sidra("populacao_municipio_sidra6579.json", "Município")
        if popm is not None:
            mun = mun.merge(popm.rename(columns={"codigo": "cod_municipio_ibge", "valor": "pop_municipio",
                                                 "ano": "ano_pop"})[["cod_municipio_ibge", "pop_municipio", "ano_pop"]],
                            on="cod_municipio_ibge", how="left")
        con.register("mun_df", mun)
        con.execute("CREATE OR REPLACE TABLE ref_municipio AS SELECT * FROM mun_df")
        disp["municipios"] = len(mun)
        ufs = mun[["cod_uf", "uf", "uf_nome", "regiao"]].drop_duplicates()
    else:
        con.execute("""CREATE OR REPLACE TABLE ref_municipio (cod_municipio_ibge INT, municipio_ibge VARCHAR, uf VARCHAR,
                       cod_uf INT, uf_nome VARCHAR, regiao VARCHAR, municipio_norm VARCHAR)""")
        disp["municipios"] = 0
        ufs = pd.DataFrame(columns=["cod_uf", "uf", "uf_nome", "regiao"])

    # população e PIB por UF
    pop = ler_sidra("populacao_uf_sidra6579.json", "Unidade da Federação")
    pib = ler_sidra("pib_uf_sidra5938.json", "Unidade da Federação")
    if pop is not None:
        ufs = ufs.merge(pop.rename(columns={"codigo": "cod_uf", "valor": "populacao", "ano": "ano_populacao"})
                        [["cod_uf", "populacao", "ano_populacao"]], on="cod_uf", how="left")
    if pib is not None:
        pib["pib_reais"] = pib["valor"] * 1000  # tabela 5938 em mil reais
        ufs = ufs.merge(pib.rename(columns={"codigo": "cod_uf", "ano": "ano_pib"})[["cod_uf", "pib_reais", "ano_pib"]],
                        on="cod_uf", how="left")
    for c in ("populacao", "ano_populacao", "pib_reais", "ano_pib"):
        if c not in ufs:
            ufs[c] = None
    con.register("uf_df", ufs)
    con.execute("CREATE OR REPLACE TABLE ref_uf AS SELECT * FROM uf_df")
    disp["uf_pop"] = int(ufs["populacao"].notna().sum())
    disp["uf_pib"] = int(ufs["pib_reais"].notna().sum())
    return disp


def main() -> dict:
    titulo("R03 - Tratamento e integração")
    con = conectar()
    con.create_function("normaliza_nome", normaliza_nome, ["VARCHAR"], "VARCHAR")
    con.execute(f"CREATE OR REPLACE VIEW bruto AS SELECT * FROM read_parquet('{(TRATADOS / 'dirbi_2025_bruto.parquet').as_posix()}')")
    disp = carregar_referencias(con)
    print("Referências carregadas:", disp)

    # municípios distintos normalizados (UDF Python só nos ~5 mil valores distintos)
    con.execute("""CREATE OR REPLACE TABLE mun_dirbi AS
                   SELECT DISTINCT municipio, uf, normaliza_nome(municipio) AS municipio_norm FROM bruto""")

    destino = (TRATADOS / "dirbi_2025_tratada.parquet").as_posix()
    con.execute(f"""
    COPY (
    WITH base AS (
        SELECT
            regexp_replace(TRIM(cnpj), '[./-]', '', 'g')                       AS cnpj,
            TRIM(nome)                                                          AS nome,
            TRIM(municipio)                                                     AS municipio,
            UPPER(TRIM(uf))                                                     AS uf,
            LPAD(regexp_replace(TRIM(cnae), '[^0-9]', '', 'g'), 7, '0')         AS cnae,
            CAST(mes AS INTEGER)                                                AS mes,
            CAST(ano AS INTEGER)                                                AS ano,
            CAST(codigo_in AS INTEGER)                                          AS codigo_beneficio,
            TRIM(tributo)                                                       AS tributo,
            {VALOR_NUM}                                                         AS valor,
            valor                                                               AS valor_texto_original
        FROM bruto
    )
    SELECT
        b.cnpj,
        CASE WHEN b.cnpj LIKE '%*%' THEN NULL ELSE substr(b.cnpj, 1, 8) END    AS cnpj_raiz,
        b.cnpj LIKE '%*%'                                                       AS cnpj_mascarado,
        (b.cnpj NOT LIKE '%*%' AND substr(b.cnpj, 9, 4) = '0001')               AS matriz,
        CASE WHEN b.cnpj LIKE '%*%' THEN 'CNPJ não divulgado' ELSE b.nome END   AS nome,
        b.municipio, md.municipio_norm, rm.cod_municipio_ibge, b.uf, ru.uf_nome, ru.regiao,
        b.cnae, rc.cnae_subclasse_desc, rc.cnae_divisao, rc.cnae_divisao_desc, rc.cnae_secao, rc.cnae_secao_desc,
        b.ano, b.mes, make_date(b.ano, b.mes, 1)                                AS competencia,
        b.codigo_beneficio, COALESCE(rb.beneficio, 'Não identificado')          AS beneficio,
        b.tributo,
        CASE WHEN regexp_replace(b.tributo, '\\s*-\\s*Importa..o$', '') ILIKE 'PIS%' THEN 'PIS/Pasep'
             ELSE regexp_replace(b.tributo, '\\s*-\\s*Importa..o$', '') END    AS tributo_grupo,
        b.tributo ILIKE '%Importa%'                                            AS tributo_importacao,
        b.valor
    FROM base b
    LEFT JOIN mun_dirbi md       ON md.municipio = b.municipio AND md.uf = b.uf
    LEFT JOIN ref_municipio rm   ON rm.municipio_norm = md.municipio_norm AND rm.uf = b.uf
    LEFT JOIN ref_uf ru          ON ru.uf = b.uf
    LEFT JOIN ref_cnae rc        ON rc.cnae = b.cnae
    LEFT JOIN ref_beneficio rb   ON rb.codigo = b.codigo_beneficio
    ) TO '{destino}' (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 200000)""")
    con.execute(f"CREATE OR REPLACE VIEW tratada AS SELECT * FROM read_parquet('{destino}')")
    q = lambda s: con.execute(s).fetchone()  # noqa: E731
    n_bruto, n_trat = q("SELECT COUNT(*) FROM bruto")[0], q("SELECT COUNT(*) FROM tratada")[0]
    if n_bruto != n_trat:
        raise SystemExit(f"ERRO: a junção alterou o número de linhas ({n_bruto} -> {n_trat})")

    # ------------------------------------------------------------- reconciliação
    total_trat = q("SELECT SUM(valor) FROM tratada")[0]
    con.execute(f"""CREATE OR REPLACE TABLE rec AS
        WITH o AS (SELECT CAST(mes AS INT) mes, TRIM(tributo) tributo, SUM({VALOR_NUM}) v FROM bruto GROUP BY ALL),
             t AS (SELECT mes, tributo, SUM(valor) v FROM tratada GROUP BY ALL)
        SELECT COALESCE(o.mes, t.mes) mes, COALESCE(o.tributo, t.tributo) tributo, o.v original, t.v pipeline,
               t.v - o.v diferenca FROM o FULL JOIN t USING (mes, tributo) ORDER BY 1, 2""")
    rec_max = q("SELECT MAX(ABS(diferenca)), COUNT(*) FROM rec")
    rec_mes = con.execute("""SELECT mes, SUM(original), SUM(pipeline), SUM(diferenca) FROM rec GROUP BY 1 ORDER BY 1""").fetchall()

    # ------------------------------------------------------------- correspondência
    def taxa(cond: str) -> tuple[float, float, int]:
        v, n = q(f"SELECT SUM(valor) FILTER (WHERE {cond}), COUNT(*) FILTER (WHERE {cond}) FROM tratada")
        return (v or 0) / total_trat, (n or 0) / n_trat, n or 0

    juncoes = {
        "Tabela de benefícios (código)": taxa("beneficio <> 'Não identificado'"),
        "CNAE 2.3 (subclasse, 7 dígitos)": taxa("cnae_secao IS NOT NULL"),
        "Municípios IBGE (nome normalizado + UF)": taxa("cod_municipio_ibge IS NOT NULL"),
        "UF (população e PIB)": taxa("uf_nome IS NOT NULL"),
    }
    sem_mun = con.execute("""SELECT municipio, uf, COUNT(*), SUM(valor) FROM tratada WHERE cod_municipio_ibge IS NULL
                             GROUP BY 1, 2 ORDER BY 4 DESC LIMIT 15""").fetchall()
    sem_cnae = con.execute("""SELECT cnae, COUNT(*), SUM(valor) FROM tratada WHERE cnae_secao IS NULL
                              GROUP BY 1 ORDER BY 3 DESC LIMIT 10""").fetchall()
    sem_ben = con.execute("""SELECT codigo_beneficio, COUNT(*), SUM(valor) FROM tratada WHERE beneficio = 'Não identificado'
                             GROUP BY 1 ORDER BY 3 DESC""").fetchall()

    con.execute(f"COPY ref_uf TO '{(TRATADOS / 'ref_uf.parquet').as_posix()}' (FORMAT PARQUET)")
    mascarados = q("SELECT COUNT(*), SUM(valor) FROM tratada WHERE cnpj_mascarado")

    # ------------------------------------------------------------- console
    print(f"Linhas: bruto {inteiro(n_bruto)} = tratada {inteiro(n_trat)}")
    print(f"Total tratado: {brl(total_trat)} | perfil de 30/10: {bi(TOTAL_PERFIL_30OUT)}")
    print(f"Reconciliação mês × tributo: {rec_max[1]} células, maior diferença absoluta = {brl(rec_max[0] or 0)}")
    for k, (pv, pl, _) in juncoes.items():
        st = "OK" if pv >= 0.99 else "ABAIXO DE 99%"
        print(f"  Junção {k:<42} valor {pct(pv, 2):>8} | linhas {pct(pl, 2):>8}  [{st}]")
    print(f"CNPJ mascarado: {mascarados[0]} linhas, {brl(mascarados[1] or 0)} (rotulados 'CNPJ não divulgado')")

    # ------------------------------------------------------------- relatório
    L = ["# Relatório de tratamento, integração e reconciliação (R03)", "",
         f"Gerado em {agora()} por `pipeline/p03_tratamento.py`.", "",
         "## 1. Reconciliação com o arquivo original", "",
         f"- Registros: {inteiro(n_bruto)} no arquivo original e {inteiro(n_trat)} na base tratada.",
         f"- Total na base tratada: **{brl(total_trat)}** ({bi(total_trat)}); total do perfilamento de 30/10/2026: {bi(TOTAL_PERFIL_30OUT)}.",
         f"- Reconciliação por mês e tributo ({rec_max[1]} combinações): maior diferença absoluta = **{brl(rec_max[0] or 0)}**.", "",
         "| Mês | Arquivo original | Pipeline | Diferença |", "|---|---|---|---|"]
    L += [f"| {m:02d} | {brl(o)} | {brl(p)} | {brl(d)} |" for m, o, p, d in rec_mes]
    L += ["", "## 2. Correspondência nas junções (critério: ≥ 99% do valor)", "",
          "| Junção | % do valor | % das linhas | Situação |", "|---|---|---|---|"]
    L += [f"| {k} | {pct(pv, 2)} | {pct(pl, 2)} | {'Atende' if pv >= 0.99 else 'Não atende'} |" for k, (pv, pl, _) in juncoes.items()]
    L += ["", "### Municípios sem correspondência (maiores valores)", "", "| Município | UF | Linhas | Valor |", "|---|---|---|---|"]
    L += [f"| {m} | {u} | {inteiro(n)} | {brl(v)} |" for m, u, n, v in sem_mun] or ["| — | — | — | — |"]
    L += ["", "### CNAE sem correspondência", "", "| CNAE | Linhas | Valor |", "|---|---|---|"]
    L += [f"| {c} | {inteiro(n)} | {brl(v)} |" for c, n, v in sem_cnae] or ["| — | — | — |"]
    L += ["", "### Códigos de benefício sem nome", "", "| Código | Linhas | Valor |", "|---|---|---|"]
    L += [f"| {c} | {inteiro(n)} | {brl(v)} |" for c, n, v in sem_ben] or ["| — | — | — |"]
    L += ["", "## 3. Bases de referência carregadas", ""] + [f"- {k}: {v}" for k, v in disp.items()]
    (DOCS / "relatorio_integracao.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    con.execute(f"COPY rec TO '{(DOCS / 'reconciliacao_mes_tributo.csv').as_posix()}' (HEADER, DELIMITER ';')")
    print("Relatório gravado em docs/relatorio_integracao.md")
    return {"total": total_trat, "rec_max": rec_max[0], "juncoes": juncoes, "linhas": n_trat}
