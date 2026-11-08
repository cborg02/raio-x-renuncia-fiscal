# Manifesto de coleta (R01)

Gerado em 08/11/2026 09:14:39 por `pipeline/p01_coleta.py`.

| Base | Arquivo | Status | Tamanho | Data de extração | SHA-256 (início) |
|---|---|---|---|---|---|
| DIRBI 2025 - renúncia por regime (arquivo anual, 12 meses) | `2025.csv` | registrado (fora do repositório) | 614.9 MB | 30/10/2026 | `f6ca7323edcb` |
| Estrutura da CNAE 2.3 (subclasse > classe > grupo > divisão > seção) | `cnae_subclasses.json` | já existia | 3,648,251 bytes | 30/10/2026 | `787e14982265` |
| Cadastro de municípios (código, nome, UF) | `municipios_ibge.json` | já existia | 2,372,050 bytes | 30/10/2026 | `77bf68d9f5b1` |
| População residente estimada por UF (último ano) | `populacao_uf_sidra6579.json` | já existia | 7,745 bytes | 30/10/2026 | `6095ae268b9f` |
| População residente estimada por município (último ano) | `populacao_municipio_sidra6579.json` | já existia | 1,508,656 bytes | 30/10/2026 | `2af3c54c4038` |
| PIB a preços correntes por UF (último ano, mil R$) | `pib_uf_sidra5938.json` | já existia | 8,086 bytes | 30/10/2026 | `0c180bb14b99` |
| Demonstrativo dos Gastos Tributários - PLOA 2025 (relatório) | `dgt_2025.pdf` | baixado | 3,542,599 bytes | 08/11/2026 | `e64ffe70d6bf` |
| Demonstrativo dos Gastos Tributários - PLOA 2025 (quadros por tributo e função) | `dgt_2025_quadros.xlsx` | baixado | 473,020 bytes | 08/11/2026 | `57c95815610b` |
| Tabela de benefícios da DIRBI (código, nome, tributos) | `tabela_beneficios_dirbi.csv` | versionado em referencias/ | 90 linhas | 07/11/2026 | `729df0b1102e` |
| Classificação preliminar dos benefícios pela LC nº 224/2025 | `lc224_classificacao_preliminar.csv` | versionado em referencias/ | 90 linhas | 07/11/2026 | `38a83ec1a4c1` |

Fontes:

- `2025.csv`: Receita Federal - Dados Abertos
- `cnae_subclasses.json`: IBGE/Concla - API de serviços de dados - https://servicodados.ibge.gov.br/api/v2/cnae/subclasses
- `municipios_ibge.json`: IBGE - API de localidades - https://servicodados.ibge.gov.br/api/v1/localidades/municipios?view=nivelado
- `populacao_uf_sidra6579.json`: IBGE/SIDRA - Tabela 6579 - https://apisidra.ibge.gov.br/values/t/6579/n3/all/v/9324/p/last%201
- `populacao_municipio_sidra6579.json`: IBGE/SIDRA - Tabela 6579 - https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/last%201
- `pib_uf_sidra5938.json`: IBGE/SIDRA - Tabela 5938 (Contas Regionais) - https://apisidra.ibge.gov.br/values/t/5938/n3/all/v/37/p/last%201
- `dgt_2025.pdf`: Receita Federal - https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/relatorios/renuncia/gastos-tributarios-ploa/dgt-previsao-ploa-2025-base-conceitual.pdf
- `dgt_2025_quadros.xlsx`: Receita Federal - https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/relatorios/renuncia/gastos-tributarios-ploa/dgt-previsao-ploa-2025-quadros.xlsx
- `tabela_beneficios_dirbi.csv`: IN RFB nº 2.198/2024, Anexo Único (IN RFB nº 2.241/2024)
- `lc224_classificacao_preliminar.csv`: LC nº 224/2025 (elaborada pelo autor)
