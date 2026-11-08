# Relatório de tratamento, integração e reconciliação (R03)

Gerado em 08/11/2026 09:15:52 por `pipeline/p03_tratamento.py`.

## 1. Reconciliação com o arquivo original

- Registros: 6.270.697 no arquivo original e 6.270.697 na base tratada.
- Total na base tratada: **R$ 366.495.982.035,69** (R$ 366,5 bi); total do perfilamento de 30/10/2026: R$ 366,5 bi.
- Reconciliação por mês e tributo (132 combinações): maior diferença absoluta = **R$ 0,00**.

| Mês | Arquivo original | Pipeline | Diferença |
|---|---|---|---|
| 01 | R$ 26.578.081.299,94 | R$ 26.578.081.299,94 | R$ 0,00 |
| 02 | R$ 25.188.311.560,10 | R$ 25.188.311.560,10 | R$ 0,00 |
| 03 | R$ 30.153.761.850,08 | R$ 30.153.761.850,08 | R$ 0,00 |
| 04 | R$ 24.150.093.073,49 | R$ 24.150.093.073,49 | R$ 0,00 |
| 05 | R$ 25.467.576.830,74 | R$ 25.467.576.830,74 | R$ 0,00 |
| 06 | R$ 28.136.337.636,39 | R$ 28.136.337.636,39 | R$ 0,00 |
| 07 | R$ 26.756.655.417,75 | R$ 26.756.655.417,75 | R$ 0,00 |
| 08 | R$ 27.641.047.168,93 | R$ 27.641.047.168,93 | R$ 0,00 |
| 09 | R$ 33.040.074.900,67 | R$ 33.040.074.900,67 | R$ 0,00 |
| 10 | R$ 29.519.544.428,03 | R$ 29.519.544.428,03 | R$ 0,00 |
| 11 | R$ 26.375.127.089,50 | R$ 26.375.127.089,50 | R$ 0,00 |
| 12 | R$ 63.489.370.780,07 | R$ 63.489.370.780,07 | R$ 0,00 |

## 2. Correspondência nas junções (critério: ≥ 99% do valor)

| Junção | % do valor | % das linhas | Situação |
|---|---|---|---|
| Tabela de benefícios (código) | 100,00% | 100,00% | Atende |
| CNAE 2.3 (subclasse, 7 dígitos) | 99,91% | 99,92% | Atende |
| Municípios IBGE (nome normalizado + UF) | 99,75% | 99,60% | Atende |
| UF (população e PIB) | 100,00% | 100,00% | Atende |

### Municípios sem correspondência (maiores valores)

| Município | UF | Linhas | Valor |
|---|---|---|---|
| SANTANA DO LIVRAMENTO | RS | 1.651 | R$ 579.345.699,90 |
| EMBU | SP | 3.171 | R$ 86.749.602,76 |
| SAO MIGUEL D'OESTE | SC | 2.105 | R$ 51.945.488,48 |
| SAO LOURENCO D'OESTE | SC | 3.912 | R$ 50.909.551,03 |
| SANTA ISABEL DO PARA | PA | 568 | R$ 32.764.627,22 |
| ARES | RN | 24 | R$ 25.580.969,14 |
| BOM JESUS | GO | 1.746 | R$ 23.970.914,95 |
| BRASOPOLIS | MG | 2.344 | R$ 18.913.581,79 |
| ARMACAO DE BUZIOS | RJ | 1.708 | R$ 14.798.560,05 |
| PARATI | RJ | 998 | R$ 5.768.133,72 |
| NOVA DO MAMORE | RO | 1.556 | R$ 5.289.032,41 |
| BALNEARIO DE PICARRAS | SC | 1.318 | R$ 2.866.062,21 |
| PRESIDENTE CASTELO BRANCO | SC | 636 | R$ 1.880.077,81 |
| BELEM DE SAO FRANCISCO | PE | 423 | R$ 1.806.551,78 |
| POXOREO | MT | 450 | R$ 1.401.582,22 |

### CNAE sem correspondência

| CNAE | Linhas | Valor |
|---|---|---|
| 3511500 | 76 | R$ 318.010.771,96 |
| 1091100 | 1.865 | R$ 4.229.484,09 |
| 4721101 | 2.427 | R$ 2.997.793,84 |
| 5611202 | 350 | R$ 731.832,60 |
| 2539000 | 58 | R$ 530.768,12 |
| 5812300 | 10 | R$ 339.678,80 |
| 1822900 | 12 | R$ 244.984,74 |
| 4751200 | 7 | R$ 6.278,31 |
| 8888888 | 4 | R$ 310,72 |

### Códigos de benefício sem nome

| Código | Linhas | Valor |
|---|---|---|
| 116 | 110 | R$ 1.475.267,77 |
| 115 | 118 | R$ 727.131,51 |
| 128 | 44 | R$ 26.585,08 |
| 92 | 4 | R$ 9.447,39 |
| 118 | 5 | R$ 201,94 |
| 105 | 20 | R$ 161,31 |
| 117 | 2 | R$ 36,73 |

## 3. Bases de referência carregadas

- beneficios: 90
- cnae: 1332
- municipios: 5571
- uf_pop: 27
- uf_pib: 27
