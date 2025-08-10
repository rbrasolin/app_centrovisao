import streamlit as st
import pandas as pd
from funcoes_compartilhadas import conversa_banco

# Função para cadastrar um novo usuário
def cadastrar_usuario():
    # Título da página
    st.title("Cadastro de Usuários")

    # Formulário de cadastro
    with st.form("form_usuario"):
        nome = st.text_input("Nome Completo")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        senha_conf = st.text_input("Confirmar Senha", type="password")

        # Botão de envio do formulário
        enviar = st.form_submit_button("Cadastrar")

        # Validação de dados
        if enviar:
            if senha != senha_conf:
                st.error("As senhas não conferem.")
            elif not nome or not email or not senha:
                st.error("Todos os campos são obrigatórios.")
            else:
                # Inserir dados na planilha 'usuarios'
                dados_usuario = {
                    "Nome": nome.strip(),
                    "Email": email.strip().lower(),
                    "Senha": senha.strip(),
                }
                # Aqui, você pode usar a função de inserção do seu banco de dados
                conversa_banco.insert("usuarios", dados_usuario)
                st.success(f"Usuário {nome} cadastrado com sucesso!")

# Exibir a lista de usuários cadastrados
def listar_usuarios():
    st.subheader("Usuários Cadastrados")
    usuarios = conversa_banco.select("usuarios", {
        "ID": "id",
        "Nome": "texto",
        "Email": "texto",
        "Senha": "texto",
    })

    # Exibe a lista de usuários
    st.dataframe(usuarios)

# Função principal que organiza a página
def app():
    # Cadastro de usuário
    cadastrar_usuario()

    # Exibir a lista de usuários
    listar_usuarios()

