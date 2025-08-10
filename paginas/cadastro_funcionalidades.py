import streamlit as st
import pandas as pd
from funcoes_compartilhadas import conversa_banco

# Função para cadastrar uma nova funcionalidade
def cadastrar_funcionalidade():
    # Título da página
    st.title("Cadastro de Funcionalidades")

    # Buscar os menus cadastrados
    df_menus = conversa_banco.select("menus", {
        "ID": "id", "Nome": "texto", "Ordem": "numero100"
    })

    # Criar o formulário
    with st.form("form_funcionalidade"):
        nome = st.text_input("Nome da Funcionalidade")
        caminho = st.text_input("Caminho da Funcionalidade (sem .py)")

        # Menu suspenso para selecionar o menu ao qual a funcionalidade pertence
        menu_opcoes = {row["Nome"]: row["ID"] for _, row in df_menus.iterrows()}
        menu_selecionado = st.selectbox("Selecione o Menu", list(menu_opcoes.keys()))

        # Botão para enviar o formulário
        enviar = st.form_submit_button("Cadastrar")

        # Validação de dados
        if enviar:
            if not nome or not caminho:
                st.error("Todos os campos são obrigatórios.")
            else:
                # Inserir dados na planilha 'funcionalidades'
                dados_funcionalidade = {
                    "ID_Menu": menu_opcoes[menu_selecionado],
                    "Nome": nome.strip(),
                    "Caminho": caminho.strip(),
                }
                # Inserir os dados utilizando a função de inserção do banco
                conversa_banco.insert("funcionalidades", dados_funcionalidade)
                st.success(f"Funcionalidade '{nome}' cadastrada com sucesso!")

# Exibir a lista de funcionalidades cadastradas
def listar_funcionalidades():
    st.subheader("Funcionalidades Cadastradas")
    funcionalidades = conversa_banco.select("funcionalidades", {
        "ID": "id",
        "ID_Menu": "texto",
        "Nome": "texto",
        "Caminho": "texto",
    })

    # Exibe a lista de funcionalidades
    st.dataframe(funcionalidades)

# Função principal que organiza a página
def app():
    # Cadastro de funcionalidade
    cadastrar_funcionalidade()

    # Exibir a lista de funcionalidades
    listar_funcionalidades()
