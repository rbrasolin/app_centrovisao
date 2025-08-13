# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime
from funcoes_compartilhadas import conversa_banco, cria_id

TABELA = "clientes"

TIPOS_COLUNAS = {
    "ID": "id",
    "CPF": "texto",
    "Origem do Cliente": "texto",
    "Convênio": "texto",
    "Nome / Razão Social": "texto",
    "Apelido / Nome Fantasia": "texto",
    "Data de Nascimento": "data",
    "CEP": "texto",
    "Endereço": "texto",
    "Número": "texto",
    "Complemento": "texto",
    "Bairro": "texto",
    "Cidade": "texto",
    "Estado": "texto",
    "Profissão": "texto",
    "Observação": "texto",
    "Data do Cadastro": "data",
    "celular": "texto",
    "celular1": "texto",
}

def parse_data(data_str):
    """Tenta converter data americana ou brasileira para datetime."""
    if not data_str or str(data_str).strip() == "":
        return None
    for fmt in ("%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(data_str), fmt)
        except ValueError:
            continue
    return None

def app():
    st.subheader("📋 Cadastro de Clientes")

    cliente_edicao = st.session_state.get("cliente_edicao", {})
    filtro_nome = st.session_state.get("filtro_nome", "")

    with st.form(key="form_cadastro_cliente", clear_on_submit=False):
        st.markdown("**Dados do Cliente**")

        id_cliente = st.text_input("ID (em branco para novo cliente)", value=cliente_edicao.get("ID", ""))
        cpf = st.text_input("CPF", value=cliente_edicao.get("CPF", ""))
        origem = st.text_input("Origem do Cliente", value=cliente_edicao.get("Origem do Cliente", ""))
        convenio = st.text_input("Convênio", value=cliente_edicao.get("Convênio", ""))
        nome_razao = st.text_input("Nome / Razão Social", value=cliente_edicao.get("Nome / Razão Social", ""))
        apelido = st.text_input("Apelido / Nome Fantasia", value=cliente_edicao.get("Apelido / Nome Fantasia", ""))

        data_edit = parse_data(cliente_edicao.get("Data de Nascimento", ""))
        data_nasc = st.date_input(
            "Data de Nascimento",
            value=data_edit if data_edit else datetime.today(),
            format="DD/MM/YYYY"
        )

        cep = st.text_input("CEP", value=cliente_edicao.get("CEP", ""))
        endereco = st.text_input("Endereço", value=cliente_edicao.get("Endereço", ""))
        numero = st.text_input("Número", value=cliente_edicao.get("Número", ""))
        complemento = st.text_input("Complemento", value=cliente_edicao.get("Complemento", ""))
        bairro = st.text_input("Bairro", value=cliente_edicao.get("Bairro", ""))
        cidade = st.text_input("Cidade", value=cliente_edicao.get("Cidade", ""))
        estado = st.text_input("Estado", value=cliente_edicao.get("Estado", ""))
        profissao = st.text_input("Profissão", value=cliente_edicao.get("Profissão", ""))
        observacao = st.text_area("Observação", value=cliente_edicao.get("Observação", ""))
        celular = st.text_input("Celular", value=cliente_edicao.get("celular", ""))
        celular1 = st.text_input("Celular 1", value=cliente_edicao.get("celular1", ""))

        botao_salvar = st.form_submit_button("Salvar")

        if botao_salvar:
            if nome_razao.strip() == "":
                st.warning("Digite o nome do cliente antes de salvar.")
            else:
                dados_cliente = {
                    "CPF": cpf,
                    "Origem do Cliente": origem,
                    "Convênio": convenio,
                    "Nome / Razão Social": nome_razao,
                    "Apelido / Nome Fantasia": apelido,
                    "Data de Nascimento": data_nasc.strftime("%d/%m/%Y") if data_nasc else "",
                    "CEP": cep,
                    "Endereço": endereco,
                    "Número": numero,
                    "Complemento": complemento,
                    "Bairro": bairro,
                    "Cidade": cidade,
                    "Estado": estado,
                    "Profissão": profissao,
                    "Observação": observacao,
                    "Data do Cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "celular": celular,
                    "celular1": celular1,
                }

                if id_cliente.strip() == "":
                    dados_cliente["ID"] = cria_id.cria_id(sequencia="cli")
                    conversa_banco.insert(TABELA, dados_cliente)
                    st.success(f"Cliente '{nome_razao}' cadastrado com sucesso!")
                else:
                    campos = list(dados_cliente.keys())
                    valores = list(dados_cliente.values())
                    conversa_banco.update(
                        TABELA,
                        campos,
                        valores,
                        where=f"ID,eq,{id_cliente}",
                        tipos_colunas=TIPOS_COLUNAS
                    )
                    st.success(f"Cliente '{nome_razao}' atualizado com sucesso!")

                st.session_state["cliente_edicao"] = {}
                st.session_state["filtro_nome"] = filtro_nome
                st.rerun()

    st.markdown("---")

    try:
        df_clientes = conversa_banco.select(TABELA, TIPOS_COLUNAS)
        if df_clientes.empty:
            st.info("Nenhum cliente cadastrado ainda.")
            return

        filtro_nome = st.text_input("Digite o nome para buscar:", value=filtro_nome)
        st.session_state["filtro_nome"] = filtro_nome

        if filtro_nome:
            df_filtrado = df_clientes[df_clientes["Nome / Razão Social"].str.contains(filtro_nome, case=False, na=False)]
            if df_filtrado.empty:
                st.warning("Nenhum cliente encontrado com esse nome.")
            else:
                for _, cliente in df_filtrado.iterrows():
                    st.write("---")
                    for campo in TIPOS_COLUNAS.keys():
                        st.write(f"**{campo}:** {cliente.get(campo, '')}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✏️ Editar {cliente['ID']}", key=f"editar_{cliente['ID']}"):
                            st.session_state["cliente_edicao"] = cliente.to_dict()
                            st.session_state["filtro_nome"] = filtro_nome
                            st.rerun()

                    with col2:
                        if st.button(f"🗑️ Excluir {cliente['ID']}", key=f"excluir_{cliente['ID']}"):
                            conversa_banco.delete(
                                TABELA,
                                where=f"ID,eq,{cliente['ID']}",
                                tipos_colunas=TIPOS_COLUNAS
                            )
                            st.success("Cliente excluído com sucesso!")
                            st.session_state["filtro_nome"] = filtro_nome
                            st.rerun()

    except Exception as e:
        st.error(f"Erro ao acessar dados de clientes: {e}")
