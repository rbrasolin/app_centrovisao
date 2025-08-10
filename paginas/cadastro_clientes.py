import streamlit as st
from datetime import datetime
from funcoes_compartilhadas import conversa_banco, trata_tabelas, cria_id

# Nome da tabela no Google Sheets
TABELA = "clientes"

# Tipos de colunas conforme padrão do conversa_banco.py
TIPOS_COLUNAS = {
    "ID": "texto",
    "Nome": "texto",
    "Email": "texto",
    "Telefone": "texto",
    "DataCadastro": "data_hora"
}

def app():
    st.subheader("📋 Cadastro de Clientes")

    # ---- FORMULÁRIO DE CADASTRO/EDIÇÃO ----
    with st.form(key="form_cadastro_cliente", clear_on_submit=True):
        st.markdown("**Dados do Cliente**")
        id_cliente = st.text_input("ID (em branco para novo cliente)")
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        telefone = st.text_input("Telefone")
        botao_salvar = st.form_submit_button("Salvar")

        if botao_salvar:
            if nome.strip() == "":
                st.warning("Digite o nome do cliente antes de salvar.")
            else:
                if id_cliente.strip() == "":  # Novo cliente
                    novo = {
                        "ID": cria_id.cria_id(sequencia="cli"),                        
                        "Nome": nome,
                        "Email": email,
                        "Telefone": telefone,
                        "DataCadastro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    conversa_banco.insert(TABELA, novo)
                    st.success(f"Cliente '{nome}' cadastrado com sucesso!")
                else:  # Editar cliente existente
                    dados_atualizados = {
                        "Nome": nome,
                        "Email": email,
                        "Telefone": telefone
                    }
                    conversa_banco.update(TABELA, dados_atualizados, {"ID": id_cliente})
                    st.success(f"Cliente '{nome}' atualizado com sucesso!")

    st.markdown("---")

    # ---- LISTAR CLIENTES ----
    try:
        df_clientes = conversa_banco.select(TABELA, TIPOS_COLUNAS)

        if df_clientes.empty:
            st.info("Nenhum cliente cadastrado ainda.")
        else:
            st.dataframe(df_clientes)

            # Selecionar cliente para editar/excluir
            clientes_lista = [f"{row['ID']} - {row['Nome']}" for _, row in df_clientes.iterrows()]
            cliente_sel = st.selectbox("Selecione um cliente para editar/excluir:", clientes_lista)
            id_selecionado = cliente_sel.split(" - ")[0]

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Editar Cliente"):
                    cliente = df_clientes[df_clientes["ID"] == id_selecionado].iloc[0]
                    st.session_state["cliente_edicao"] = {
                        "ID": cliente["ID"],
                        "Nome": cliente["Nome"],
                        "Email": cliente["Email"],
                        "Telefone": cliente["Telefone"]
                    }
                    st.experimental_rerun()

            with col2:
                if st.button("Excluir Cliente"):
                    conversa_banco.delete(TABELA, {"ID": id_selecionado})
                    st.success("Cliente excluído com sucesso!")
                    st.experimental_rerun()

    except Exception as e:
        st.error(f"Erro ao acessar dados de clientes: {e}")

    # ---- PRÉ-PREENCHIMENTO PARA EDIÇÃO ----
    if "cliente_edicao" in st.session_state:
        cliente = st.session_state.pop("cliente_edicao")
        st.experimental_set_query_params(cliente_id=cliente["ID"])
        st.write("Preencha o formulário acima para editar e clique em Salvar.")
        st.text_input("ID", cliente["ID"], key="id_cliente", disabled=True)
        st.text_input("Nome", cliente["Nome"], key="nome")
        st.text_input("Email", cliente["Email"], key="email")
        st.text_input("Telefone", cliente["Telefone"], key="telefone")
