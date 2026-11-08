# Guia da Sprint 1 — o que você precisa fazer (Charley)

Tempo total estimado: **2 a 3 horas**, mais o tempo das sessões com os participantes.
Cada **📸 PRINT** é uma evidência para o relatório. Salve os prints com o nome indicado (ex.: `print01.png`)
e me envie todos ao final, junto com os arquivos pedidos.

> Dica: no Windows, **Win + Shift + S** recorta uma área da tela; depois cole no Paint e salve como PNG.

---

## Passo 1 — Rodar o pipeline (≈ 15 min) · R01 a R05 e R08

1. Descompacte `raio-x-renuncia-fiscal.zip` em uma pasta fixa, por exemplo `C:\projetos\raio-x-renuncia-fiscal`.
2. Abra o PowerShell **nessa pasta** (no Explorer, clique na barra de endereço, digite `powershell` e Enter).
3. Instale as dependências:
   ```powershell
   pip install -r requirements.txt
   ```
4. Execute o pipeline apontando para o seu `2025.csv` (troque o caminho):
   ```powershell
   python pipeline\executar_sprint1.py --csv "C:\caminho\da\pasta\2025.csv" --data-extracao 30/10/2026
   ```
   - 📸 **print01** — o início da execução (comando e bloco "R01 - Coleta", com os downloads do IBGE).
   - 📸 **print02** — o bloco "R03 - Tratamento e integração" (reconciliação e junções).
   - 📸 **print03** — o final: "Top 20 benefícios", "RESUMO DA EXECUÇÃO" e a linha "Pronto".
5. Se aparecer `[FALHOU]` em algum download, abra o link mostrado no navegador, salve o arquivo com o nome indicado
   em `dados\brutos\` e rode o comando de novo (o que já foi baixado não é baixado outra vez).
6. 📸 **print04** — o Explorer aberto em `dados\brutos\` mostrando os arquivos e tamanhos.
7. **Envie no chat o arquivo `entrega_sprint1.zip`** (fica na pasta do projeto; tem poucos MB).

## Passo 2 — Abrir o painel no seu computador (≈ 5 min) · R05 e R06

```powershell
streamlit run app\app.py
```
O navegador abre sozinho. 📸 **print05** — a página "Visão geral" com o PowerShell visível ao lado
(mostra que é execução local). Para parar, Ctrl + C no PowerShell.

## Passo 3 — GitHub (≈ 20 min) · R01 (versionamento)

1. Crie uma conta em <https://github.com> (se ainda não tiver).
2. Instale o **GitHub Desktop** (<https://desktop.github.com>) e entre com a conta. Ele respeita o `.gitignore`,
   o que garante que a base bruta e a base tratada **não** subam (restrição R9). Não use o upload pelo site.
3. No GitHub Desktop: **File > Add local repository** > escolha a pasta do projeto > clique em
   **"create a repository"** > Name: `raio-x-renuncia-fiscal` > **Create repository**.
4. Confira, na lista de alterações, que **não** aparecem arquivos de `dados\tratados\` nem `.csv` grandes.
   Escreva o resumo `Sprint 1: pipeline, dicionário e painel` > **Commit to main**.
5. **Publish repository** > desmarque "Keep this code private" (precisa ser público para o Streamlit gratuito) > Publish.
6. 📸 **print06** — a página do repositório no GitHub, mostrando as pastas e o README.

## Passo 4 — Publicar no Streamlit Community Cloud (≈ 15 min) · P7 / R05

1. Acesse <https://share.streamlit.io> > **Continue with GitHub** e autorize.
2. **Create app** > "Deploy a public app from GitHub":
   - Repository: `seu-usuario/raio-x-renuncia-fiscal` · Branch: `main` · Main file path: `app/app.py`
   - App URL: `raio-x-renuncia-fiscal` (ou o que estiver disponível) > **Deploy**.
3. Aguarde a instalação (2 a 5 min). 📸 **print07** — o painel online no computador, com a URL visível.
4. Abra a mesma URL no celular. 📸 **print08** — captura de tela do celular (teste de desempenho previsto na P7).
5. **Me mande a URL pública.**

## Passo 5 — Trello (≈ 20 min) · Evidência do planejamento

1. Em <https://trello.com>, crie o quadro **Raio-X da Renúncia Fiscal 2025** com as listas:
   `Backlog` · `A fazer` · `Em andamento` · `Em validação` · `Concluído`.
2. Crie as etiquetas: `Sprint 1` (verde), `Sprint 2` (amarela), `Sprint 3` (laranja), `Must`, `Should`, `Could`.
3. Em **Backlog**, clique em "Adicionar um cartão", **cole todas as linhas abaixo de uma vez** e escolha
   "Criar 18 cartões":
   ```
   R01 – Coletar e versionar a DIRBI 2025 e as bases complementares
   R02 – Perfilar a qualidade dos dados
   R03 – Tratar e integrar (CNPJ, CNAE, códigos, bases complementares)
   R04 – Dicionário de dados e notas metodológicas
   R05 – Visão geral com KPIs e participação por tributo
   R06 – Página "Entenda a renúncia fiscal" (glossário e alertas)
   R07 – Protótipo de baixa fidelidade e pré-teste com 3 a 5 usuários
   R08 – Viabilidade da classificação pela LC 224/2025 (20 maiores benefícios)
   R09 – Painel de concentração por empresa (Pareto, Lorenz, Gini)
   R10 – Mapa por UF (absoluto, per capita, % do PIB)
   R11 – Visão setorial por CNAE com HHI
   R12 – Ranking de benefícios e curva de Pareto
   R13 – Comparação DIRBI × DGT por tributo
   R14 – Série mensal com anotação de eventos
   R15 – Exposição ao corte da LC 224/2025
   R16 – Publicar o painel e revisar alertas
   R17 – Pós-teste com os mesmos participantes
   R18 – Busca por empresa ou CNPJ
   ```
4. Em cada cartão, coloque a etiqueta da sprint e da prioridade (R13 e R14 = Should; R18 = Could; o resto = Must)
   e a data de entrega (S1: 08/11; S2: 15/11; S3: 23/11). Opcional: cole o critério de aceite da Tabela 23 na descrição.
5. 📸 **print09** — o quadro com os 18 cartões no Backlog (planejamento da sprint).
6. Mova R01 a R08 para **A fazer**. 📸 **print10** — o quadro com o Sprint Backlog da Sprint 1.
7. Ao concluirmos tudo (depois do Passo 6), mova R01–R06 e R08 para **Concluído**, R07 para **Em validação**
   ou **Concluído** (conforme as respostas). 📸 **print11** — o quadro no fim da sprint.

## Passo 6 — Pré-teste com 3 a 5 pessoas (≈ 15 min por pessoa) · R07 / H1 e H2

1. Acesse <https://script.google.com> > **Novo projeto** > apague o conteúdo > cole o arquivo
   `validacao\criar_formulario_pre_teste.gs` > salve > selecione `criarPreTeste` > **Executar** > autorize.
2. Em **Registro de execução** aparecem dois links: um para responder e outro para editar.
   📸 **print12** — o formulário aberto (modo de visualização).
3. Atribua a cada pessoa um código (P1 a P5) e **anote quem é quem só para você** (os mesmos farão o pós-teste).
   Não precisamos de nomes no relatório.
4. Roteiro de cada sessão (presencial ou por chamada de vídeo):
   1. A pessoa responde a **Parte A sem ver o painel**.
   2. Você mostra o painel publicado (Visão geral e Entenda) e o rascunho `validacao\prototipo_baixa_fidelidade.png`.
      Peça: "encontre o total renunciado e o tributo principal" e observe se ela consegue sem ajuda.
   3. A pessoa responde a **Parte B**.
   4. Anote em uma linha qualquer dificuldade de navegação observada (vai para os "ajustes de navegação documentados").
5. No formulário, aba **Respostas** > ícone do Planilhas > **Arquivo > Fazer download > CSV**.
   📸 **print13** — a aba "Respostas" > "Resumo" do Forms.
6. **Envie no chat o CSV das respostas e as suas anotações das sessões.**

---

## O que me enviar (checklist)

- [ ] `entrega_sprint1.zip`
- [ ] URL pública do painel
- [ ] print01 a print13
- [ ] CSV das respostas do pré-teste + anotações das sessões

Com isso eu gero os prints do painel com os dados reais, consolido o R08, calculo o resultado do pré-teste
e preencho os itens 2.1.1 e 2.1.2 do relatório (versão 4).
