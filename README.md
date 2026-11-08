# Raio-X da Renúncia Fiscal Federal 2025

MVP do Projeto Aplicado da pós-graduação em Ciência de Dados (XP Educação). Painel que traduz a
**DIRBI 2025** (Declaração de Incentivos, Renúncias, Benefícios e Imunidades de Natureza Tributária,
Receita Federal) em respostas a perguntas simples: quanto foi renunciado, quem recebe, onde, em que setores,
por quais benefícios e o que muda com a LC nº 224/2025.

## Estrutura

```
pipeline/            scripts do tratamento (R01 a R05)
  executar_sprint1.py  executa tudo e grava logs/sprint1_execucao.log
  p01_coleta.py        R01 coleta e manifesto das bases
  p02_perfil.py        R02 perfilamento da qualidade
  p03_tratamento.py    R03 tratamento, integração e reconciliação
  p04_dicionario.py    R04 dicionário de dados
  p05_agregados.py     R05 tabelas pré-agregadas do painel e insumo do R08
referencias/         tabela de benefícios da DIRBI e classificação preliminar pela LC nº 224/2025
docs/                relatórios gerados (qualidade, integração, dicionário, manifesto)
app/                 painel Streamlit (app.py) e agregados em app/dados/
validacao/           protótipo de baixa fidelidade e formulário do pré-teste (R07)
dados/               bases brutas e tratadas (fora do Git)
```

## Como reproduzir

1. **Baixe a base bruta** (não versionada, ~615 MB, restrição R9): portal de dados abertos da Receita Federal,
   conjunto "Renúncia fiscal por regime / DIRBI", arquivo de 2025. Descompacte o `2025.csv` em qualquer pasta.
2. **Instale as dependências** (Python 3.10+):
   ```
   pip install -r requirements.txt
   ```
3. **Execute o pipeline** (as bases do IBGE e o DGT são baixados automaticamente):
   ```
   python pipeline/executar_sprint1.py --csv CAMINHO/2025.csv --data-extracao 30/10/2026
   ```
4. **Abra o painel**:
   ```
   streamlit run app/app.py
   ```

O painel lê apenas os arquivos pequenos de `app/dados/`, por isso pode ser publicado no Streamlit Community Cloud
sem a base bruta.

## Fontes

- Receita Federal: DIRBI 2025 (dados abertos); Demonstrativo dos Gastos Tributários PLOA 2025; IN RFB nº 2.198/2024
  (Anexo Único, redação da IN RFB nº 2.241/2024) e IN RFB nº 2.294/2025.
- IBGE: CNAE 2.3 (API de serviços de dados), localidades, SIDRA 6579 (população) e 5938 (PIB).
- Lei Complementar nº 224/2025.

Valores autodeclarados e sujeitos a retificação. Usufruir de benefício fiscal é legal e não indica irregularidade.
