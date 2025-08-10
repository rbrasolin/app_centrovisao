import streamlit as st
import pandas as pd
from funcoes_compartilhadas import conversa_banco

# Função para cadastrar as permissões de um usuário
def cadastrar_permissao():
    # Título da página
    st.title("Cadastro de Permissões")

    # Buscar usuários cadastrados
    df_usuarios = conversa_banco.select("usuarios", {
        "ID": "id", "Nome": "texto", "Email": "texto", "Senha": "texto"
    })

    # Buscar funcionalidades cadastradas
    df_funcionalidades = conversa_banco.select("funcionalidades", {
        "ID": "id", "ID_Menu": "texto", "Nome": "texto", "Caminho": "texto"
    })

    # Criar o formulário para selecionar o usuário e as funcionalidades
    with st.form("form_permissao"):
        usuarios_opcoes = {row["Nome"]: row["ID"] for _, row in df_usuarios.iterrows()}
        usuario_selecionado = st.selectbox("Selecione o Usuário", list(usuarios_opcoes.keys()))

        funcionalidades_selecionadas = st.multiselect(
            "Selecione as Funcionalidades", 
            options=[row["Nome"] for _, row in df_funcionalidades.iterrows()],
            default=[]
        )

        # Botão de envio do formulário
        enviar = st.form_submit_button("Cadastrar Permissões")

        if enviar:
            if not funcionalidades_selecionadas:
                st.error("Selecione ao menos uma funcionalidade.")
            else:
                for func in funcionalidades_selecionadas:
                    # Obter o ID da funcionalidade selecionada
                    id_func = df_funcionalidades[df_funcionalidades["Nome"] == func]["ID"].values[0]
                    
                    # Verificar se o usuário já tem permissão para a funcionalidade
                    permissoes_usuario = conversa_banco.select("permissoes", {
                        "ID_Usuario": "texto", 
                        "ID_Funcionalidade": "texto"
                    })

                    # Verificar se a permissão já foi atribuída
                    permissao_existente = permissoes_usuario[
                        (permissoes_usuario["ID_Usuario"] == usuarios_opcoes[usuario_selecionado]) & 
                        (permissoes_usuario["ID_Funcionalidade"] == id_func)
                    ]
                    
                    if permissao_existente.empty:
                        # Inserir nova permissão
                        dados_permissao = {
                            "ID_Usuario": usuarios_opcoes[usuario_selecionado],
                            "ID_Funcionalidade": id_func,
                        }
                        conversa_banco.insert("permissoes", dados_permissao)
                        st.success(f"Permissão '{func}' cadastrada com sucesso para o usuário '{usuario_selecionado}'.")
                    else:
                        st.warning(f"O usuário '{usuario_selecionado}' já tem permissão para a funcionalidade '{func}'.")

# Exibir as permissões cadastradas
def listar_permissoes():
    st.subheader("Permissões Cadastradas")
    
    # Buscar as permissões na planilha
    permissoes = conversa_banco.select("permissoes", {
        "ID": "id",
        "ID_Usuario": "texto",
        "ID_Funcionalidade": "texto"
    })

    # Exibe a lista de permissões
    st.dataframe(permissoes)

# Função principal que organiza a página
def app():
    # Cadastro de permissões
    cadastrar_permissao()

    # Exibir as permissões cadastradas
    listar_permissoes()
