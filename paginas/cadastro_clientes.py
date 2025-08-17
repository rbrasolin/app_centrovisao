# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime, date
from funcoes_compartilhadas import conversa_banco, cria_id
import re

# Nome da tabela no banco
TABELA = "clientes"

# Mapeamento das colunas e tipos
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

# ----------------- FUNÇÕES AUXILIARES -----------------
def parse_data(data_str):
    """Tenta converter datas em diferentes formatos para datetime."""
    if not data_str or str(data_str).strip() == "":
        return None
    for fmt in ("%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(str(data_str), fmt)
        except ValueError:
            continue
    return None

def format_data_br(data_str):
    """Converte qualquer formato para DD/MM/YYYY HH:mm:ss"""
    dt = parse_data(data_str)
    if dt:
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    return "-"

def format_cpf(cpf: str) -> str:
    """Formata CPF 000.000.000-00"""
    if not cpf:
        return ""
    cpf_num = re.sub(r"\D", "", str(cpf))
    if len(cpf_num) == 11:
        return f"{cpf_num[:3]}.{cpf_num[3:6]}.{cpf_num[6:9]}-{cpf_num[9:]}"
    return cpf

def format_celular(cel: str) -> str:
    """Formata celular (99) 99999-9999"""
    if not cel:
        return ""
    cel_num = re.sub(r"\D", "", str(cel))
    if len(cel_num) == 11:
        return f"({cel_num[:2]}) {cel_num[2:7]}-{cel_num[7:]}"
    elif len(cel_num) == 10:
        return f"({cel_num[:2]}) {cel_num[2:6]}-{cel_num[6:]}"
    return cel

def limpar_campos():
    """Limpa todos os campos do formulário"""
    for key in [
        "ID", "CPF", "Origem do Cliente", "Convênio", "Nome / Razão Social",
        "Apelido / Nome Fantasia", "Data de Nascimento", "CEP", "Endereço", "Número",
        "Complemento", "Bairro", "Cidade", "Estado", "Profissão", "Observação",
        "Data do Cadastro", "celular", "celular1"
    ]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state["cliente_edicao"] = {}

# ----------------- APP PRINCIPAL -----------------
def app():
    st.subheader("📋 Cadastro de Clientes")

    cliente_edicao = st.session_state.get("cliente_edicao", {})

    # ------------------- FILTROS NO TOPO -------------------
    try:
        df_clientes = conversa_banco.select(TABELA, TIPOS_COLUNAS)
        if df_clientes.empty:
            st.info("Nenhum cliente cadastrado ainda.")
            return

        # 🔹 Atualiza registros antigos sem "Data do Cadastro"
        for idx, row in df_clientes.iterrows():
            if not row.get("Data do Cadastro"):
                conversa_banco.update(
                    TABELA,
                    ["Data do Cadastro"],
                    [datetime.now().strftime("%d/%m/%Y %H:%M:%S")],
                    where=f"ID,eq,{row['ID']}",
                    tipos_colunas=TIPOS_COLUNAS
                )

        # Filtros de busca
        col1, col2 = st.columns(2)
        with col1:
            nome_sel = st.selectbox(
                "🔎 Buscar por Nome",
                options=[""] + df_clientes["Nome / Razão Social"].dropna().unique().tolist(),
                index=0,
            )
        with col2:
            cpf_sel = st.selectbox(
                "🔎 Buscar por CPF",
                options=[""] + df_clientes["CPF"].dropna().unique().tolist(),
                index=0,
            )

        cliente_selecionado = None
        if nome_sel:
            cliente_selecionado = df_clientes[df_clientes["Nome / Razão Social"] == nome_sel].iloc[0].to_dict()
        elif cpf_sel:
            cliente_selecionado = df_clientes[df_clientes["CPF"] == cpf_sel].iloc[0].to_dict()

        if cliente_selecionado:
            st.markdown("### 👤 Dados do Cliente")
            for campo in TIPOS_COLUNAS.keys():
                valor = cliente_selecionado.get(campo, "")
                if campo == "CPF":
                    valor = format_cpf(valor)
                elif campo in ["celular", "celular1"]:
                    valor = format_celular(valor)
                elif campo in ["Data do Cadastro", "Data de Nascimento"]:
                    valor = format_data_br(valor)
                st.write(f"**{campo}:** {valor if valor else '-'}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✏️ Editar {cliente_selecionado['ID']}", key=f"editar_{cliente_selecionado['ID']}"):
                    st.session_state["cliente_edicao"] = cliente_selecionado
                    st.rerun()
            with col2:
                if st.button(f"🗑️ Excluir {cliente_selecionado['ID']}", key=f"excluir_{cliente_selecionado['ID']}"):
                    conversa_banco.delete(
                        TABELA,
                        where=f"ID,eq,{cliente_selecionado['ID']}",
                        tipos_colunas=TIPOS_COLUNAS
                    )
                    st.success("Cliente excluído com sucesso!")
                    st.rerun()

    except Exception as e:
        st.error(f"Erro ao acessar dados de clientes: {e}")

    st.markdown("---")

    # ------------------- FORMULÁRIO DE CADASTRO/EDIÇÃO -------------------
    with st.form(key="form_cadastro_cliente", clear_on_submit=False):
        st.markdown("**Dados do Cliente**")

        id_cliente = st.text_input("ID (em branco para novo cliente)", value=cliente_edicao.get("ID", ""))

        cpf = st.text_input("CPF", value=format_cpf(cliente_edicao.get("CPF", "")))
        origem = st.text_input("Origem do Cliente", value=cliente_edicao.get("Origem do Cliente", ""))
        convenio = st.text_input("Convênio", value=cliente_edicao.get("Convênio", ""))
        nome_razao = st.text_input("Nome / Razão Social", value=cliente_edicao.get("Nome / Razão Social", ""))
        apelido = st.text_input("Apelido / Nome Fantasia", value=cliente_edicao.get("Apelido / Nome Fantasia", ""))

        # Data de nascimento: sem limite de range (corrigido)
        data_edit = parse_data(cliente_edicao.get("Data de Nascimento", ""))
        data_nasc = st.date_input(
            "Data de Nascimento",
            value=data_edit.date() if data_edit else None,
            format="DD/MM/YYYY",
            min_value=date(1900, 1, 1),
            max_value=date.today()
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

        celular = st.text_input("Celular", value=format_celular(cliente_edicao.get("celular", "")))
        celular1 = st.text_input("Celular 1", value=format_celular(cliente_edicao.get("celular1", "")))

        # Data do cadastro: sugere o dia atual se não tiver valor
        data_cadastro_edit = parse_data(cliente_edicao.get("Data do Cadastro", "")) or datetime.now()
        data_cadastro = st.text_input("Data do Cadastro", value=data_cadastro_edit.strftime("%d/%m/%Y %H:%M:%S"))

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
                    "Data do Cadastro": data_cadastro if data_cadastro else datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "celular": celular,
                    "celular1": celular1,
                }

                if id_cliente.strip() == "":
                    dados_cliente["ID"] = cria_id.cria_id(sequencia="cli")
                    conversa_banco.insert(TABELA, dados_cliente)
                    st.success(f"✅ Cliente '{nome_razao}' cadastrado com sucesso!")
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
                    st.success(f"✅ Cliente '{nome_razao}' atualizado com sucesso!")

                # 🔹 Limpa campos e reseta edição
                limpar_campos()
                st.rerun()

                #fim
