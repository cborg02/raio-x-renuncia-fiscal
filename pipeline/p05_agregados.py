"""R05 / R08 - Tabelas pré-agregadas do painel (restrição R9) e insumo do teste de viabilidade da LC 224/2025.

Gera em app/dados/ arquivos pequenos (versionáveis no GitHub) e docs/r08_top20_lc224.csv.
"""
from __future__ import annotations

import json

import duckdb

from comum import conectar, APP_DADOS, DOCS, REFS, TRATADOS, agora, bi, brl, inteiro, pct, titulo


def main(data_extracao: str) -> dict:
    titulo("R05 - Agregados do painel e R08 - Top 20 benefícios")
    con = conectar()
    con.execute(f"CREATE VIEW t AS SELECT * FROM read_parquet('{(TRATADOS / 'dirbi_2025_tratada.parquet').as_posix()}')")
    con.execute(f"CREATE VIEW ref_uf AS SELECT * FROM read_parquet('{(TRATADOS / 'ref_uf.parquet').as_posix()}')")
    con.execute(f"CREATE VIEW lc AS SELECT * FROM read_csv('{(REFS / 'lc224_classificacao_preliminar.csv').as_posix()}', header=true)")
    out = lambda nome: (APP_DADOS / nome).as_posix()  # noqa: E731

    k = con.execute("""SELECT SUM(valor), COUNT(*), COUNT(DISTINCT cnpj_raiz), COUNT(DISTINCT cnpj),
                              COUNT(DISTINCT codigo_beneficio), COUNT(DISTINCT tributo),
                              SUM(valor) FILTER (WHERE cnpj_mascarado), COUNT(*) FILTER (WHERE cnpj_mascarado)
                       FROM t""").fetchone()
    kpis = {"total": float(k[0]), "registros": k[1], "empresas": k[2], "cnpjs": k[3], "beneficios": k[4], "tributos": k[5],
            "valor_cnpj_nao_divulgado": float(k[6] or 0), "registros_cnpj_nao_divulgado": k[7],
            "ano": 2025, "data_extracao": data_extracao, "gerado_em": agora(),
            "dgt_2025_bi": 543.6}
    (APP_DADOS / "kpis.json").write_text(json.dumps(kpis, ensure_ascii=False, indent=2), encoding="utf-8")

    con.execute(f"""COPY (SELECT tributo, tributo_grupo, CAST(SUM(valor) AS DOUBLE) valor, COUNT(*) registros, COUNT(DISTINCT cnpj_raiz) empresas,
                         SUM(valor) / SUM(SUM(valor)) OVER () participacao
                         FROM t GROUP BY ALL ORDER BY valor DESC) TO '{out('agg_tributo.parquet')}' (FORMAT PARQUET)""")
    con.execute(f"""COPY (SELECT mes, tributo, tributo_grupo, CAST(SUM(valor) AS DOUBLE) valor, COUNT(DISTINCT cnpj_raiz) empresas
                         FROM t GROUP BY ALL ORDER BY 1, 4 DESC) TO '{out('agg_mes_tributo.parquet')}' (FORMAT PARQUET)""")
    con.execute(f"""COPY (SELECT a.*, l.classificacao_lc224, l.grau_de_certeza FROM (
                           SELECT codigo_beneficio, beneficio, CAST(SUM(valor) AS DOUBLE) valor, COUNT(DISTINCT cnpj_raiz) empresas,
                                  COUNT(DISTINCT mes) meses, SUM(valor) / SUM(SUM(valor)) OVER () participacao
                           FROM t GROUP BY ALL) a
                         LEFT JOIN lc l ON l.codigo = a.codigo_beneficio ORDER BY valor DESC)
                   TO '{out('agg_beneficio.parquet')}' (FORMAT PARQUET)""")
    con.execute(f"""COPY (SELECT t.uf, ANY_VALUE(t.uf_nome) uf_nome, ANY_VALUE(t.regiao) regiao, CAST(SUM(valor) AS DOUBLE) valor,
                                COUNT(DISTINCT cnpj_raiz) empresas, ANY_VALUE(r.populacao) populacao,
                                ANY_VALUE(r.ano_populacao) ano_populacao, ANY_VALUE(r.pib_reais) pib_reais, ANY_VALUE(r.ano_pib) ano_pib
                         FROM t LEFT JOIN ref_uf r ON r.uf = t.uf GROUP BY 1 ORDER BY valor DESC)
                   TO '{out('agg_uf.parquet')}' (FORMAT PARQUET)""")
    con.execute(f"""COPY (SELECT COALESCE(cnae_secao, '?') cnae_secao, COALESCE(cnae_secao_desc, 'Não informado') cnae_secao_desc,
                                COALESCE(cnae_divisao, '??') cnae_divisao, COALESCE(cnae_divisao_desc, 'Não informado') cnae_divisao_desc,
                                CAST(SUM(valor) AS DOUBLE) valor, COUNT(DISTINCT cnpj_raiz) empresas
                         FROM t GROUP BY ALL ORDER BY valor DESC) TO '{out('agg_cnae_divisao.parquet')}' (FORMAT PARQUET)""")
    con.execute(f"""COPY (SELECT cnpj_raiz, ANY_VALUE(nome) nome, ANY_VALUE(uf) uf, CAST(SUM(valor) AS DOUBLE) valor,
                                COUNT(DISTINCT codigo_beneficio) beneficios
                         FROM t WHERE NOT cnpj_mascarado GROUP BY 1 ORDER BY valor DESC)
                   TO '{out('agg_empresa.parquet')}' (FORMAT PARQUET, COMPRESSION ZSTD)""")

    # conferência: soma dos agregados = total da base (critério do R05)
    conf = {}
    for arq in ("agg_tributo", "agg_mes_tributo", "agg_beneficio", "agg_uf", "agg_cnae_divisao"):
        conf[arq] = con.execute(f"SELECT SUM(valor) FROM read_parquet('{out(arq + '.parquet')}')").fetchone()[0]
    emp = con.execute(f"SELECT SUM(valor) FROM read_parquet('{out('agg_empresa.parquet')}')").fetchone()[0]
    conf["agg_empresa + CNPJ não divulgado"] = float(emp) + kpis["valor_cnpj_nao_divulgado"]

    top20 = con.execute(f"""SELECT ROW_NUMBER() OVER (ORDER BY valor DESC) posicao, codigo_beneficio, beneficio, valor, participacao,
                                   SUM(participacao) OVER (ORDER BY valor DESC) acumulado, classificacao_lc224, grau_de_certeza
                            FROM read_parquet('{out('agg_beneficio.parquet')}') ORDER BY valor DESC LIMIT 20""").df()
    top20[["classificacao_lc224", "grau_de_certeza"]] = top20[["classificacao_lc224", "grau_de_certeza"]].fillna("Sem classificação")
    top20.to_csv(DOCS / "r08_top20_lc224.csv", index=False, sep=";", encoding="utf-8-sig", decimal=",")

    print(f"Total: {brl(kpis['total'])} | empresas (raízes): {inteiro(kpis['empresas'])} | benefícios: {kpis['beneficios']} "
          f"| tributos: {kpis['tributos']} | registros: {inteiro(kpis['registros'])}")
    print("Conferência das tabelas do painel (soma = total da base):")
    for a, v in conf.items():
        print(f"  {a:<36} {brl(v):>24}  diferença {brl(round(float(v) - float(kpis['total']), 2) + 0.0)}")
    print("\nTop 20 benefícios (insumo do R08):")
    for _, r in top20.iterrows():
        print(f"  {r.posicao:>2}. [{r.codigo_beneficio:>3}] {r.beneficio[:55]:<55} {bi(r.valor):>13} "
              f"acum. {pct(r.acumulado):>6}  {r.classificacao_lc224} ({r.grau_de_certeza})")
    tam = sum(p.stat().st_size for p in APP_DADOS.iterdir())
    print(f"\nArquivos do painel em app/dados/: {len(list(APP_DADOS.iterdir()))} arquivos, {tam/1024/1024:.2f} MB no total")
    return {"kpis": kpis, "conf": conf}
