/**
 * Cria no Google Forms o pré-teste de compreensão (R07 / H1) e a entrevista sobre o protótipo (H2).
 *
 * Como usar: acesse https://script.google.com > Novo projeto > apague o conteúdo > cole este arquivo >
 * Salvar > selecione a função criarPreTeste > Executar > autorize com sua conta Google.
 * Os links do formulário aparecem em "Registro de execução" (Ver > Registros).
 *
 * O mesmo formulário será reaplicado no pós-teste (Sprint 3, R17) com os mesmos participantes.
 */
function criarPreTeste() {
  var form = FormApp.create('Raio-X da Renúncia Fiscal 2025 — Pré-teste de compreensão');
  form.setIsQuiz(true);
  form.setCollectEmail(false);
  form.setDescription(
    'Obrigado por participar! São 8 perguntas rápidas sobre benefícios fiscais federais e algumas perguntas sobre um protótipo.\n' +
    'Não existe resposta "errada" para você: o que está sendo testado é o painel, não o participante. ' +
    'Se não souber, marque "Não sei" — isso também é uma informação útil. Tempo estimado: 10 minutos.');

  form.addListItem().setTitle('Código do participante (informado pelo pesquisador)')
      .setChoiceValues(['P1', 'P2', 'P3', 'P4', 'P5']).setRequired(true);
  form.addMultipleChoiceItem().setTitle('Qual perfil mais se aproxima do seu?')
      .setChoiceValues(['Cidadão interessado no tema', 'Jornalista / comunicação', 'Analista de finanças públicas / setor público', 'Estudante / pesquisador'])
      .showOtherOption(true).setRequired(true);

  form.addPageBreakItem().setTitle('Parte A — Compreensão (responda sem consultar o painel)');
  var q = [
    ['Em 2025, as empresas declararam à Receita Federal (DIRBI) ter usufruído aproximadamente quanto em benefícios fiscais federais?',
      ['Cerca de R$ 37 bilhões', 'Cerca de R$ 370 bilhões', 'Cerca de R$ 3,7 trilhões', 'Não sei'], 1],
    ['Qual tributo concentra a maior parte desse valor?',
      ['Imposto de Renda (IRPJ)', 'Cofins', 'IPI', 'Não sei'], 1],
    ['Aproximadamente quantas empresas declararam usufruir de algum benefício em 2025?',
      ['Cerca de 9 mil', 'Cerca de 90 mil', 'Cerca de 900 mil', 'Não sei'], 1],
    ['O valor declarado na DIRBI corresponde a todo o gasto tributário federal estimado para 2025?',
      ['Sim, é o mesmo valor', 'Não, corresponde a cerca de dois terços, porque a DIRBI não cobre Simples Nacional, MEI e pessoas físicas', 'Não, é maior que a estimativa oficial', 'Não sei'], 1],
    ['Uma mineradora com sede no Rio de Janeiro aparece usufruindo do benefício Sudam/Sudene. O mais correto é concluir que:',
      ['A atividade beneficiada ocorre no Rio de Janeiro', 'Há um erro nos dados', 'O dado mostra a UF da sede; a operação beneficiada pode estar em outra região', 'Não sei'], 2],
    ['Uma empresa aparecer entre as maiores beneficiárias indica que ela cometeu alguma irregularidade?',
      ['Sim', 'Não, usufruir de benefício previsto em lei é legal', 'Depende do valor', 'Não sei'], 1],
    ['O que a Lei Complementar nº 224/2025 faz com a maior parte dos benefícios fiscais federais a partir de 2026?',
      ['Extingue todos', 'Reduz em cerca de 10%, com exceções (ex.: Zona Franca, Simples Nacional, cesta básica)', 'Amplia os benefícios', 'Não sei'], 1],
    ['O benefício declarado de IRPJ é muito maior em dezembro do que nos outros meses. A explicação mais provável é:',
      ['Uma mudança de lei em dezembro', 'A forma de apuração do IRPJ (trimestral e anual), que concentra valores no fim dos períodos', 'Erro de digitação das empresas', 'Não sei'], 1]
  ];
  q.forEach(function (it, i) {
    var item = form.addMultipleChoiceItem();
    item.setTitle('A' + (i + 1) + '. ' + it[0]).setRequired(true).setPoints(1);
    item.setChoices(it[1].map(function (c, j) { return item.createChoice(c, j === it[2]); }));
  });
  form.addScaleItem().setTitle('Quão confiante você está nas suas respostas da Parte A?')
      .setBounds(1, 5).setLabels('Nada confiante', 'Muito confiante').setRequired(true);

  form.addPageBreakItem().setTitle('Parte B — Protótipo (o pesquisador vai mostrar as telas)')
      .setHelpText('Observe a tela "Visão geral" já construída e o rascunho das próximas telas.');
  var likert = [
    'B1. As telas organizadas por perguntas (quanto, quem, onde, setores, benefícios) facilitam entender o tema.',
    'B2. Prefiro respostas prontas e contextualizadas a montar consultas com filtros.',
    'B3. Os alertas de interpretação (cobertura, sede, mudanças no tempo) são úteis.',
    'B4. Consegui encontrar o total renunciado e o principal tributo sem ajuda.',
    'B5. Eu usaria um painel assim para trabalho, estudo ou para me informar.'
  ];
  likert.forEach(function (t) {
    form.addScaleItem().setTitle(t).setBounds(1, 5).setLabels('Discordo totalmente', 'Concordo totalmente').setRequired(true);
  });
  form.addCheckboxItem().setTitle('B6. Quais telas do rascunho você considera mais importantes? (até 3)')
      .setChoiceValues(['Visão geral', 'Quem recebe (empresas)', 'Onde (UF)', 'Setores', 'Benefícios', 'O que muda com a LC 224'])
      .setValidation(FormApp.createCheckboxValidation().requireSelectAtMost(3).build());
  form.addParagraphTextItem().setTitle('B7. O que ficou confuso ou faltou na tela "Visão geral"?');
  form.addParagraphTextItem().setTitle('B8. Que pergunta sobre benefícios fiscais você gostaria que o painel respondesse?');

  Logger.log('Link para responder: ' + form.getPublishedUrl());
  Logger.log('Link para editar e ver respostas: ' + form.getEditUrl());
}
