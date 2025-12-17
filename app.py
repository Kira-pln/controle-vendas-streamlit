import streamlit as st
import pandas as pd
from datetime import date
import io

# ---------------- CONFIGURAÇÃO DA PÁGINA ----------------
st.set_page_config(
    page_title="Controle de Vendas",
    layout="wide"
)

# ---------------- ESTADO INICIAL ----------------
if "produtos" not in st.session_state:
    st.session_state.produtos = pd.DataFrame(
        columns=["Produto", "Descrição"]
    )

if "vendas" not in st.session_state:
    st.session_state.vendas = pd.DataFrame(
        columns=[
            "Produto",
            "Quantidade",
            "Preço de venda",
            "Percentual (%)",
            "Valor a receber",
            "Data"
        ]
    )

# ---------------- MENU LATERAL ----------------
st.sidebar.title("Menu")
pagina = st.sidebar.radio(
    "Selecione a opção",
    ["Cadastro de produtos", "Registrar venda", "Relatórios"]
)

# ======================================================
# PÁGINA 1 — CADASTRO DE PRODUTOS
# ======================================================
if pagina == "Cadastro de produtos":

    st.title("Cadastro de produtos")

    col1, col2 = st.columns(2)

    with col1:
        nome_produto = st.text_input("Nome do produto")
    with col2:
        descricao = st.text_input("Descrição do produto")

    if st.button("Cadastrar produto"):
        if nome_produto.strip() == "":
            st.warning("Informe o nome do produto.")
        else:
            novo_produto = pd.DataFrame(
                [[nome_produto, descricao]],
                columns=["Produto", "Descrição"]
            )
            st.session_state.produtos = pd.concat(
                [st.session_state.produtos, novo_produto],
                ignore_index=True
            )
            st.success("Produto cadastrado com sucesso.")

    st.subheader("Produtos cadastrados")
    st.dataframe(st.session_state.produtos, use_container_width=True)

# ======================================================
# PÁGINA 2 — REGISTRAR VENDA
# ======================================================
elif pagina == "Registrar venda":

    st.title("Registrar venda")

    if st.session_state.produtos.empty:
        st.warning("Cadastre um produto antes de registrar vendas.")
    else:
        produto = st.selectbox(
            "Produto",
            st.session_state.produtos["Produto"]
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            quantidade = st.number_input(
                "Quantidade vendida",
                min_value=1,
                step=1
            )

        with col2:
            preco = st.number_input(
                "Preço de venda (R$)",
                min_value=0.0,
                step=0.01,
                format="%.2f"
            )

        with col3:
            percentual = st.number_input(
                "Percentual a receber (%)",
                min_value=0.0,
                step=0.1,
                format="%.1f"
            )

        with col4:
            data_venda = st.date_input(
                "Data da venda",
                value=date.today()
            )

        valor_receber = quantidade * preco * (percentual / 100)

        st.markdown(
            f"**Valor a receber:** R$ {valor_receber:.2f}"
        )

        if st.button("Registrar venda"):
            nova_venda = pd.DataFrame(
                [[
                    produto,
                    quantidade,
                    preco,
                    percentual,
                    valor_receber,
                    data_venda
                ]],
                columns=st.session_state.vendas.columns
            )

            st.session_state.vendas = pd.concat(
                [st.session_state.vendas, nova_venda],
                ignore_index=True
            )

            st.success("Venda registrada com sucesso.")

# ======================================================
# PÁGINA 3 — RELATÓRIOS
# ======================================================
elif pagina == "Relatórios":

    st.title("Relatório de vendas")

    if st.session_state.vendas.empty:
        st.warning("Nenhuma venda registrada.")
    else:
        st.dataframe(st.session_state.vendas, use_container_width=True)

        total_produtos = st.session_state.vendas["Quantidade"].sum()
        total_vendido = (
            st.session_state.vendas["Quantidade"]
            * st.session_state.vendas["Preço de venda"]
        ).sum()
        total_receber = st.session_state.vendas["Valor a receber"].sum()

        col1, col2, col3 = st.columns(3)

        col1.metric("Total de produtos vendidos", total_produtos)
        col2.metric("Valor total vendido (R$)", f"{total_vendido:.2f}")
        col3.metric("Valor total a receber (R$)", f"{total_receber:.2f}")

        # EXPORTAÇÃO PARA EXCEL
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            st.session_state.vendas.to_excel(
                writer,
                index=False,
                sheet_name="Relatório de Vendas"
            )

        st.download_button(
            label="Exportar relatório para Excel",
            data=buffer,
            file_name="relatorio_vendas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
