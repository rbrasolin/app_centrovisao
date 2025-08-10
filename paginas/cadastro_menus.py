import streamlit as st
from funcoes_compartilhadas import conversa_banco

# Função para cadastrar um novo menu
def cadastrar_menu():
    # Título da página
    st.title("Cadastro de Menus")

    # Formulário de cadastro
    with st.form("form_menu"):
        nome = st.text_input("Nome do Menu")
        ordem = st.number_input("Ordem do Menu", min_value=1, step=1)

        # Botão de envio do formulário
        enviar = st.form_submit_button("Cadastrar")

        # Validação de dados
        if enviar:
            if not nome:
                st.error("O nome do menu é obrigatório.")
            else:
                # Inserir dados na planilha 'menus'
                dados_menu = {
                    "Nome": nome.strip(),
                    "Ordem": ordem,
                }
                conversa_banco.insert("menus", dados_menu)
                st.success(f"Menu '{nome}' cadastrado com sucesso!")

# Função para editar um menu
def editar_menu(menu_id):
    # Buscar dados do menu selecionado
    menu = conversa_banco.select("menus", {"ID": "id", "Nome": "texto", "Ordem": "numero100"})
    menu_selecionado = menu[menu["ID"] == menu_id].iloc[0]

    # Título da edição
    st.title(f"Editar Menu: {menu_selecionado['Nome']}")

    # Formulário de edição
    with st.form("form_editar_menu"):
        novo_nome = st.text_input("Nome do Menu", value=menu_selecionado["Nome"])
        nova_ordem = st.number_input("Ordem do Menu", value=menu_selecionado["Ordem"], min_value=1, step=1)

        # Botão para salvar as alterações
        enviar = st.form_submit_button("Salvar Alterações")

        if enviar:
            if not novo_nome:
                st.error("O nome do menu é obrigatório.")
            else:
                # Atualiza o menu na planilha
                dados_menu = {
                    "Nome": novo_nome.strip(),
                    "Ordem": nova_ordem,
                }

                # Atualiza os dados no banco, garantindo que a função update seja chamada corretamente
                sucesso = conversa_banco.update("menus", ["Nome", "Ordem"], [novo_nome.strip(), nova_ordem], where=f"ID,eq,{menu_id}", tipos_colunas={"ID": "id", "Nome": "texto", "Ordem": "numero100"})

                if sucesso > 0:
                    st.success(f"Menu '{novo_nome}' atualizado com sucesso!")
                else:
                    st.error("Ocorreu um erro ao atualizar o menu. Tente novamente.")

# Função para excluir um menu
def excluir_menu(menu_id):
    # Exclui o menu da planilha
    conversa_banco.delete("menus", where=f"ID,eq,{menu_id}", tipos_colunas={"ID": "id"})
    st.success("Menu excluído com sucesso!")

# Exibir a lista de menus cadastrados
def listar_menus():
    st.subheader("Menus Cadastrados")
    menus = conversa_banco.select("menus", {
        "ID": "id",
        "Nome": "texto",
        "Ordem": "numero100",
    })

    # Exibe a lista de menus
    if menus.empty:
        st.warning("Nenhum menu cadastrado.")
        return
    
    # Lista os menus para seleção
    menu_opcoes = {row["Nome"]: row["ID"] for _, row in menus.iterrows()}
    menu_selecionado = st.selectbox("Selecione o Menu", list(menu_opcoes.keys()))

    # Botões para editar e excluir o menu selecionado
    col1, col2 = st.columns([2, 2])
    with col1:
        if st.button("Alterar Menu"):
            if menu_selecionado:
                editar_menu(menu_opcoes[menu_selecionado])
            else:
                st.warning("Selecione um menu para editar.")
    
    with col2:
        if st.button("Excluir Menu"):
            if menu_selecionado:
                excluir_menu(menu_opcoes[menu_selecionado])
            else:
                st.warning("Selecione um menu para excluir.")

# Função principal que organiza a página
def app():
    # Cadastro de menu
    cadastrar_menu()

    # Exibir a lista de menus
    listar_menus()
