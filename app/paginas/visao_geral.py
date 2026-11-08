"""R05 - Visão geral: total renunciado, empresas, benefícios e participação por tributo."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import plotly.express as px
import streamlit as st

from comum_app import COR_IMPORTACAO, COR_PRINCIPAL, bi, configurar, inteiro, kpis, numero_br, rodape, tabela

configurar("Visão geral")
k = kpis()

st.title("Quanto o governo federal deixou de arrecadar com benefícios fiscais declarados em 2025?")
st.markdown(
    f"Em 2025, as **pessoas jurídicas** (exceto MEI e optantes do Simples Nacional) declararam à Receita Federal, "
    f"na **DIRBI**, ter usufruído **{bi(k['total'])}** "
    "em benefícios fiscais federais, ou seja, tributos que deixaram de ser pagos por força de lei."
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total renunciado declarado", bi(k["total"]), help="Soma do campo Valor de todos os registros da DIRBI 2025.")
c2.metric("Empresas beneficiadas", inteiro(k["empresas"]),
          help="Pessoas jurídicas (exceto MEI e Simples Nacional), contadas pela raiz do CNPJ (8 dígitos). Exclui registros com CNPJ não divulgado pela RFB.")
c3.metric("Benefícios fiscais", inteiro(k["beneficios"]), help="Códigos de benefício (itens do Anexo Único da IN RFB nº 2.198/2024).")
c4.metric("Tributos envolvidos", inteiro(k["tributos"]), help="Tributos federais desonerados, separando os incidentes na importação.")

st.info(
    f"**Antes de interpretar:** a DIRBI cobre cerca de **{numero_br(k['total'] / 1e9 / k['dgt_2025_bi'] * 100, 0)}%** "
    f"do gasto tributário estimado para 2025 no DGT (R$ {numero_br(k['dgt_2025_bi'])} bi), porque não inclui Simples Nacional, "
    "MEI, pessoas físicas nem benefícios fora da lista obrigatória. Veja a página **Entenda a renúncia fiscal**.",
    icon="ℹ️",
)
# ajuste de navegação do pré-teste (R07): no celular o menu lateral fica recolhido
st.page_link("paginas/entenda.py", label="Entenda a renúncia fiscal: glossário e alertas de interpretação",
             icon=":material/menu_book:")

st.subheader("Em quais tributos está a renúncia?")
agrupar = st.toggle("Somar os tributos na importação ao tributo correspondente", value=False)
t = tabela("agg_tributo")
if agrupar:
    t = t.groupby("tributo_grupo", as_index=False)["valor"].sum().rename(columns={"tributo_grupo": "tributo"})
    t["tipo"] = "Total"
else:
    t = t.assign(tipo=t["tributo"].str.contains("Importa").map({True: "Importação", False: "Operações internas"}))
t["participacao"] = t["valor"] / t["valor"].sum()
t = t.sort_values("valor")
t["rotulo"] = [f"{bi(v)} · {numero_br(p * 100)}%" for v, p in zip(t["valor"], t["participacao"])]

fig = px.bar(t, x="valor", y="tributo", orientation="h", text="rotulo", color="tipo",
             color_discrete_map={"Operações internas": COR_PRINCIPAL, "Importação": COR_IMPORTACAO, "Total": COR_PRINCIPAL})
fig.update_traces(textposition="outside", cliponaxis=False,
                  hovertemplate="%{y}<br>%{text}<extra></extra>")
fig.update_layout(height=max(320, 42 * len(t)), margin=dict(l=10, r=140, t=10, b=10), xaxis_title=None, yaxis_title=None,
                  xaxis=dict(showticklabels=False, showgrid=False), legend_title=None,
                  legend=dict(orientation="h", y=-0.08), plot_bgcolor="rgba(0,0,0,0)",
                  yaxis=dict(categoryorder="array", categoryarray=list(t["tributo"])))
st.plotly_chart(fig, width="stretch")

top = t.sort_values("valor", ascending=False).head(3)
st.markdown(
    "**Leitura:** a renúncia está concentrada em poucos tributos. "
    + ", ".join(f"{r.tributo} ({numero_br(r.participacao * 100)}%)" for r in top.itertuples())
    + f" somam {numero_br(top['participacao'].sum() * 100)}% do total."
)

with st.expander("Como estes números foram conferidos"):
    st.markdown(
        f"- Base: {inteiro(k['registros'])} registros (CNPJ × mês × benefício × tributo), {inteiro(k['cnpjs'])} CNPJs.\n"
        f"- O total do painel foi reconciliado com o arquivo original da RFB por mês e tributo, sem diferença.\n"
        f"- {inteiro(k['registros_cnpj_nao_divulgado'])} registros ({bi(k['valor_cnpj_nao_divulgado'], 2)}) têm CNPJ "
        "ocultado pela própria RFB: entram nos totais como \"CNPJ não divulgado\", mas não na contagem de empresas."
    )

st.subheader("Próximas visões (Sprint 2 e 3)")
st.markdown(
    "- **Quem** concentra os benefícios (empresas)  \n- **Onde** estão as sedes beneficiadas (UF, per capita e % do PIB)  \n"
    "- **Em que setores** (CNAE)  \n- **Por quais benefícios**  \n- **O que muda com a LC nº 224/2025** (corte de 10%)"
)
st.page_link("paginas/entenda.py", label="Próxima página: Entenda a renúncia fiscal", icon=":material/arrow_forward:")
rodape()
