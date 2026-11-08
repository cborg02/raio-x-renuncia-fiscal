"""R06 - Entenda a renúncia fiscal: glossário e alertas de interpretação (R4, R5, R6)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import streamlit as st

from comum_app import bi, configurar, kpis, numero_br, rodape

configurar("Entenda a renúncia fiscal")
k = kpis()

st.title("Entenda a renúncia fiscal")
st.markdown(
    "Renúncia fiscal é o tributo que o governo **deixa de arrecadar** porque uma lei concede um tratamento mais favorável "
    "a determinadas empresas, setores, regiões ou produtos (isenção, alíquota zero, redução de base, crédito presumido etc.). "
    "Na prática, funciona como um gasto público feito pelo lado da receita."
)

st.header("Alertas de interpretação")
a1, a2, a3 = st.columns(3)
with a1:
    st.warning(
        "**1. Cobertura parcial**\n\n"
        f"A DIRBI soma {bi(k['total'])}, cerca de {numero_br(k['total'] / 1e9 / k['dgt_2025_bi'] * 100, 0)}% dos "
        f"R$ {numero_br(k['dgt_2025_bi'])} bi estimados no Demonstrativo de Gastos Tributários (DGT) 2025. "
        "Ficam de fora o Simples Nacional, o MEI, as pessoas físicas e os benefícios que não constam da lista obrigatória. "
        "A diferença é de **cobertura**, não erro nem subdeclaração.",
        icon="⚠️",
    )
with a2:
    st.warning(
        "**2. Local da sede, não da atividade**\n\n"
        "UF e município são os do CNPJ declarante. Uma empresa com sede no Rio de Janeiro pode usufruir de benefício ligado a "
        "fábricas ou minas em outra região. Exemplo: Vale e Salobo aparecem no RJ, mas o benefício Sudam/Sudene "
        "(redução de 75% do IRPJ) decorre de operações no Norte e no Nordeste.",
        icon="⚠️",
    )
with a3:
    st.warning(
        "**3. Mudanças ao longo do tempo**\n\n"
        "O Perse (setor de eventos) deixou de ser usufruído a partir de abril de 2025. A lista da DIRBI foi ampliada de 88 para "
        "173 benefícios, mas só para períodos a partir de **janeiro de 2026** (IN RFB nº 2.294/2025): em 2025 a lista é estável. "
        "IRPJ e CSLL têm picos em março, junho, setembro e dezembro por causa da apuração trimestral e anual.",
        icon="⚠️",
    )
st.caption("Também: os valores são autodeclarados e podem ser retificados; usufruir de benefício fiscal é legal e não indica irregularidade.")

st.header("Glossário")
GLOSSARIO = {
    "Renúncia fiscal / gasto tributário": "Receita que o governo deixa de arrecadar por causa de um tratamento tributário favorecido previsto em lei. "
    "\"Gasto tributário\" é o termo técnico usado pela Receita Federal.",
    "DIRBI": "Declaração de Incentivos, Renúncias, Benefícios e Imunidades de Natureza Tributária. Desde 2024, empresas que usam "
    "benefícios da lista oficial informam mensalmente à Receita quanto deixaram de pagar. É a fonte deste painel.",
    "DGT": "Demonstrativo dos Gastos Tributários, publicado com o projeto de lei orçamentária. Traz estimativas para todos os "
    "benefícios, inclusive os que não passam pela DIRBI.",
    "Benefício fiscal (código)": "Cada item do Anexo Único da IN RFB nº 2.198/2024, como Zona Franca de Manaus, Sudam/Sudene, "
    "desoneração da folha ou alíquota zero da cesta básica.",
    "Tributo": "Imposto ou contribuição desonerado: Cofins, PIS/Pasep, IRPJ, CSLL, IPI, Imposto de Importação, contribuição "
    "previdenciária e CIDE. Os sufixos \"- Importação\" indicam a versão do tributo cobrada na importação.",
    "Raiz do CNPJ": "Os 8 primeiros dígitos do CNPJ, que identificam a empresa. O painel soma matriz e filiais pela raiz.",
    "CNPJ não divulgado": "Registros em que a própria Receita ocultou o CNPJ. Entram nos totais, mas não em rankings de empresas.",
    "Isenção, alíquota zero, crédito presumido": "Formas de benefício: dispensar o tributo, zerar a alíquota ou permitir "
    "que a empresa abata um crédito calculado sobre suas compras.",
    "LC nº 224/2025": "Lei Complementar que, a partir de 2026, reduz em 10% a maior parte dos benefícios federais, com exceções "
    "como Zona Franca de Manaus, Simples Nacional, cesta básica, Prouni e desoneração da folha.",
    "CNAE": "Classificação Nacional de Atividades Econômicas, usada para agrupar as empresas por setor.",
}
for termo, defin in GLOSSARIO.items():
    with st.expander(termo):
        st.write(defin)

st.header("De onde vêm os dados")
st.markdown(
    "- **DIRBI 2025**: Receita Federal, dados abertos (arquivo anual, 12 meses).\n"
    "- **Nomes dos benefícios**: Anexo Único da IN RFB nº 2.198/2024 (redação da IN RFB nº 2.241/2024).\n"
    "- **Setores**: CNAE 2.3 (IBGE/Concla). **População e PIB**: IBGE.\n"
    "- **Comparação**: Demonstrativo dos Gastos Tributários 2025 (Receita Federal)."
)
rodape()
