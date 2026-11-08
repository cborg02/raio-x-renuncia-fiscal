# Relatório de qualidade dos dados - DIRBI 2025 (R02)

Gerado em 08/11/2026 09:15:18 por `pipeline/p02_perfil.py` a partir de `2025.csv`.

Colunas originais: CNPJ, Nome, Município, UF, Cnae, Mês, Ano, Código_IN, Tributo, Valor (renomeadas por posição para cnpj, nome, municipio, uf, cnae, mes, ano, codigo_in, tributo, valor).

## 1. Volume

| Medida | Valor |
|---|---|
| Registros | 6.270.697 |
| CNPJs distintos | 88.959 |
| Raízes de CNPJ (8 dígitos, sem mascarados) | 88.944 |
| Códigos de benefício | 95 |
| Tributos | 11 |
| Total declarado | R$ 366.495.982.035,69 |

## 2. Verificações

| Verificação | Resultado | Regra de tratamento |
|---|---|---|
| Campos vazios | 0 | Nenhuma ação necessária |
| Valor não numérico | 0 | Valor lido como texto e convertido explicitamente (vírgula decimal) |
| Valor negativo | 0 | Nenhuma ação necessária |
| Valor zerado | 0 | Nenhuma ação necessária |
| Duplicados na chave (CNPJ, ano, mês, código, tributo) | 0 | Chave única confirmada |
| Linhas idênticas | 0 | — |
| CNPJ mascarado pela RFB | 222 | Manter nos totais; rotular "CNPJ não divulgado"; excluir de rankings e concentração |
| CNPJ fora do padrão (14 dígitos após remover pontuação; formato publicado: 17.648.724/0001-49) | 0 | Remover pontuação (. / -) |
| CNPJ de estabelecimento não matriz | 21.788 (0,35%) | Agregar pela raiz do CNPJ (8 dígitos) |
| CNAE com 7 dígitos | 100,00% | Ler como texto; LPAD(7, '0') por segurança |
| UFs distintas | 27 (inválidas: nenhuma) | — |
| Meses | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 | Mês inteiro (1-12), diferente do dicionário da RFB (dd/mm/aaaa) |
| Ano | 2025 | — |
| Códigos sem nome na tabela de benefícios | [92, 105, 115, 116, 117, 118, 128] | Rotular "não identificado" (premissa P2) |
| Municípios com acento | BALNEÁRIO RINCÃO, MOJUÍ DOS CAMPOS | Normalizar (caixa alta, sem acento) antes da junção com o IBGE |

## 3. Distribuição do valor (R$ por registro)

| Mínimo | P25 | Mediana | Média | P75 | P99 | Máximo |
|---|---|---|---|---|---|---|
| R$ 0,01 | R$ 43,17 | R$ 304,65 | R$ 58.445,81 | R$ 2.243,08 | R$ 674.700,00 | R$ 3.084.292.007,65 |

Distribuição muito assimétrica (média ≈ 192× a mediana). Pelo critério Q3 + 3·IIQ aplicado ao log10 do valor (limite de R$ 314.653.745,92), 23 registros são extremos e somam R$ 19,4 bi. Eles **não são removidos**: os maiores são declarações legítimas de grandes empresas (ver tabela abaixo). Regra: manter, usar escala logarítmica nos gráficos de distribuição e reportar medianas.

| Empresa | UF | Tributo | Mês | Código | Valor |
|---|---|---|---|---|---|
| VALE S.A. | RJ | IRPJ | 12 | 20 | R$ 3.084.292.007,65 |
| SALOBO METAIS S/A | RJ | IRPJ | 12 | 20 | R$ 1.956.367.805,55 |
| STELLANTIS AUTOMOVEIS BRASIL LTDA. | MG | IRPJ | 12 | 29 | R$ 1.884.148.702,91 |
| RECOFARMA INDUSTRIA DO AMAZONAS LTDA | AM | IRPJ | 12 | 20 | R$ 829.564.946,90 |
| TRANSPORTADORA ASSOCIADA DE GAS S.A. - TAG | RJ | IRPJ | 12 | 20 | R$ 751.739.541,80 |
| PETROLEO BRASILEIRO S A PETROBRAS | RJ | IRPJ | 12 | 20 | R$ 751.497.032,30 |
| MOTO HONDA DA AMAZONIA LTDA | AM | IRPJ | 12 | 20 | R$ 728.957.797,07 |
| MOTO HONDA DA AMAZONIA LTDA | AM | IPI | 8 | 54 | R$ 720.569.547,53 |
| MOTO HONDA DA AMAZONIA LTDA | AM | IPI | 10 | 54 | R$ 712.062.095,82 |
| MOTO HONDA DA AMAZONIA LTDA | AM | IPI | 9 | 54 | R$ 711.380.879,23 |

## 4. Total por tributo

| Tributo | Registros | Valor | % |
|---|---|---|---|
| Cofins | 2.977.328 | R$ 164,3 bi | 44,8% |
| IRPJ | 30.361 | R$ 47,4 bi | 12,9% |
| PIS/Pasep | 2.927.010 | R$ 39,5 bi | 10,8% |
| Cofins - Importação | 16.418 | R$ 37,2 bi | 10,1% |
| IPI | 9.498 | R$ 32,8 bi | 8,9% |
| Contribuição Previdenciária | 219.012 | R$ 15,0 bi | 4,1% |
| Imposto de Importação | 4.356 | R$ 8,8 bi | 2,4% |
| PIS/Pasep - Importação | 60.163 | R$ 8,6 bi | 2,3% |
| CSLL | 23.935 | R$ 8,1 bi | 2,2% |
| IPI - Importação | 2.604 | R$ 4,9 bi | 1,3% |
| CIDE | 12 | R$ 0,0 bi | 0,0% |

## 5. Regras de tratamento adotadas no pipeline (R03)

1. Ler todas as colunas como texto e renomear por posição (o cabeçalho tem acentos).
2. Converter Valor (vírgula decimal, sem separador de milhar) para DECIMAL(18,2) (somas exatas) e Mês para inteiro.
3. Remover a pontuação do CNPJ, derivar a raiz (8 primeiros dígitos) e marcar CNPJs mascarados pela RFB.
4. Normalizar municípios (caixa alta, sem acento, só letras e números) antes da junção com o IBGE.
5. Agrupar tributos "- Importação" ao tributo correspondente apenas na comparação com o DGT (coluna `tributo_grupo`).
6. Não remover outliers; não imputar valores (não há vazios).
