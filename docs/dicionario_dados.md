# Dicionário de dados - base analítica DIRBI 2025 (R04)

Gerado em 08/11/2026 09:15:52 por `pipeline/p04_dicionario.py`. Base: `dados/tratados/dirbi_2025_tratada.parquet` (6.270.697 registros, 26 campos).

| # | Campo | Tipo | Descrição | Origem | Transformação | % preenchido | Distintos | Exemplo |
|---|---|---|---|---|---|---|---|---|
| 1 | `cnpj` | VARCHAR | CNPJ do estabelecimento declarante (14 dígitos) | DIRBI - CNPJ | Texto; removida pontuação; 222 registros mascarados pela RFB mantidos | 100,00% | 88.959 | 17648724000149 |
| 2 | `cnpj_raiz` | VARCHAR | Raiz do CNPJ (8 dígitos) - identifica a empresa | Derivado de cnpj | 8 primeiros caracteres; nulo quando mascarado | 100,00% | 88.944 | 17648724 |
| 3 | `cnpj_mascarado` | BOOLEAN | Indica CNPJ ocultado pela própria RFB | Derivado de cnpj | Verdadeiro se contém '*' | 100,00% | 2 | False |
| 4 | `matriz` | BOOLEAN | Indica estabelecimento matriz (ordem 0001) | Derivado de cnpj | Posições 9-12 = '0001' | 100,00% | 2 | True |
| 5 | `nome` | VARCHAR | Razão social do declarante | DIRBI - Nome | Sem alteração; 'CNPJ não divulgado' quando mascarado | 100,00% | 90.063 | DISTRIBUIDORA DE ALIMENTOS ARENA DE IPIA |
| 6 | `municipio` | VARCHAR | Município da sede declarante, como publicado | DIRBI - Município | Sem alteração | 100,00% | 4.006 | IPIRANGA |
| 7 | `municipio_norm` | VARCHAR | Município normalizado para junção | Derivado de municipio | Caixa alta, sem acento, só letras e números | 100,00% | 4.006 | IPIAU |
| 8 | `cod_municipio_ibge` | BIGINT | Código IBGE do município (7 dígitos) | IBGE - Localidades | Junção por municipio_norm + UF | 99,60% | 4.146 | 2913903 |
| 9 | `uf` | VARCHAR | UF da sede declarante (não indica onde a atividade ocorreu) | DIRBI - UF | Caixa alta | 100,00% | 27 | BA |
| 10 | `uf_nome` | VARCHAR | Nome da UF | IBGE - Localidades | Junção por UF | 100,00% | 27 | Bahia |
| 11 | `regiao` | VARCHAR | Grande região | IBGE - Localidades | Junção por UF | 100,00% | 5 | Sul |
| 12 | `cnae` | VARCHAR | CNAE principal - subclasse (7 dígitos) | DIRBI - Cnae | Texto; LPAD 7 com zeros | 100,00% | 1.086 | 4639701 |
| 13 | `cnae_subclasse_desc` | VARCHAR | Descrição da subclasse CNAE | IBGE/Concla - CNAE 2.3 | Junção por cnae | 99,92% | 1.077 | COMÉRCIO VAREJISTA DE CARNES - AÇOUGUES |
| 14 | `cnae_divisao` | VARCHAR | Divisão CNAE (2 dígitos) | IBGE/Concla - CNAE 2.3 | Junção por cnae | 99,92% | 85 | 46 |
| 15 | `cnae_divisao_desc` | VARCHAR | Descrição da divisão CNAE | IBGE/Concla - CNAE 2.3 | Junção por cnae | 99,92% | 85 | COMÉRCIO POR ATACADO, EXCETO VEÍCULOS AU |
| 16 | `cnae_secao` | VARCHAR | Seção CNAE (letra A-U) | IBGE/Concla - CNAE 2.3 | Junção por cnae | 99,92% | 20 | G |
| 17 | `cnae_secao_desc` | VARCHAR | Descrição da seção CNAE | IBGE/Concla - CNAE 2.3 | Junção por cnae | 99,92% | 20 | COMÉRCIO; REPARAÇÃO DE VEÍCULOS AUTOMOTO |
| 18 | `ano` | INTEGER | Ano de apuração | DIRBI - Ano | Inteiro | 100,00% | 1 | 2025 |
| 19 | `mes` | INTEGER | Mês de apuração (1-12) | DIRBI - Mês | Inteiro (o dicionário da RFB indica dd/mm/aaaa, mas o arquivo traz 1-12) | 100,00% | 12 | 5 |
| 20 | `competencia` | DATE | Primeiro dia do mês de apuração | Derivado de ano e mes | make_date(ano, mes, 1) | 100,00% | 12 | 2025-01-01 |
| 21 | `codigo_beneficio` | INTEGER | Item do Anexo Único da IN RFB nº 2.198/2024 | DIRBI - Código_IN | Inteiro | 100,00% | 95 | 88 |
| 22 | `beneficio` | VARCHAR | Nome do benefício fiscal | Tabela de benefícios (IN RFB nº 2.241/2024) | Junção por código; 'Não identificado' se ausente | 100,00% | 89 | Papel higiênico |
| 23 | `tributo` | VARCHAR | Tributo desonerado, como publicado | DIRBI - Tributo | Sem alteração | 100,00% | 11 | Cofins |
| 24 | `tributo_grupo` | VARCHAR | Tributo sem a distinção '- Importação' | Derivado de tributo | Usado só na comparação com o DGT (R13) | 100,00% | 8 | Cofins |
| 25 | `tributo_importacao` | BOOLEAN | Indica tributo incidente na importação | Derivado de tributo | Verdadeiro se contém 'Importação' | 100,00% | 2 | False |
| 26 | `valor` | DECIMAL(18,2) | Valor do benefício usufruído no mês (R$) | DIRBI - Valor | Texto com vírgula decimal convertido para DECIMAL(18,2) | 100,00% | 1.404.888 | 4.04 |

## Notas metodológicas

1. **Unidade de análise:** cada registro é a combinação CNPJ × mês × código de benefício × tributo (chave única verificada no R02).
2. **Empresa = raiz do CNPJ.** Contagens e concentração usam os 8 primeiros dígitos; filiais (0,35% dos registros) são somadas à empresa.
3. **CNPJ mascarado pela RFB:** mantido em todos os totais como "CNPJ não divulgado" e excluído de rankings e medidas de concentração.
4. **Localização pela sede (restrição R5):** UF e município são os do CNPJ declarante. Ex.: Vale e Salobo aparecem no RJ, embora o benefício Sudam/Sudene (código 20, redução de 75% do IRPJ) esteja ligado a operações nas regiões Norte e Nordeste.
5. **Cobertura (restrição R4):** a DIRBI não inclui Simples Nacional, MEI, pessoas físicas nem benefícios fora do Anexo Único. Por isso o total (~R$ 366,5 bi) corresponde a cerca de 67% do DGT 2025 (R$ 543,6 bi); a razão é diferença de cobertura, não erro.
6. **Lista de benefícios (restrição R6):** em 2025 vigorou o Anexo Único com 88 itens (IN RFB nº 2.241/2024). A ampliação para 173 itens (IN RFB nº 2.294/2025) vale para períodos de apuração a partir de janeiro de 2026 (art. 3º). Logo, não há quebra de lista dentro de 2025.
7. **Sazonalidade de IRPJ e CSLL:** concentram-se em março, junho, setembro e, sobretudo, dezembro (apuração trimestral/anual); não é mudança de política. A série mensal (R14) separa ou anota esses tributos.
8. **Fim do Perse:** o benefício (código 1) deixa de ser usufruído a partir de abril de 2025.
9. **Natureza dos dados (R7):** valores autodeclarados e sujeitos a retificação; a análise refere-se à extração registrada no manifesto.
10. **Ética (R8):** usufruir de benefício fiscal é legal e não indica irregularidade.
11. **População e PIB:** último ano disponível no IBGE (ver colunas ano_populacao e ano_pib em ref_uf); a diferença de ano-base é declarada no painel (premissa P5).

## Tabelas pré-agregadas do painel (`app/dados/`)

| Arquivo | Granularidade | Uso |
|---|---|---|
| `kpis.json` | Ano | Cartões da visão geral (R05) |
| `agg_tributo.parquet` | Tributo | Participação por tributo (R05/H6) |
| `agg_mes_tributo.parquet` | Mês × tributo | Série mensal (R14) |
| `agg_beneficio.parquet` | Código de benefício | Ranking e Pareto (R12), LC 224 (R08/R15) |
| `agg_uf.parquet` | UF | Mapa e normalização (R10) |
| `agg_cnae_divisao.parquet` | Seção × divisão CNAE | Visão setorial (R11) |
| `agg_empresa.parquet` | Raiz do CNPJ (sem mascarados) | Concentração (R09) |
