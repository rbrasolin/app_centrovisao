# -*- coding: utf-8 -*-
import os
import time
import json
import pandas as pd
import gspread
import streamlit as st
from functools import wraps
from gspread.exceptions import APIError
from google.oauth2.service_account import Credentials
from funcoes_compartilhadas.cria_id import cria_id

# ===================================================
# 🔐 CREDENCIAIS E CONEXÃO COM PLANILHA
# ===================================================

# 1) URL da planilha:
#    - pega de st.secrets["G_SHEET_URL"] se existir
#    - senão usa o fallback abaixo (ajuste se quiser)
URL_PLANILHA = st.secrets.get(
    "G_SHEET_URL",
    "https://docs.google.com/spreadsheets/d/12cuz76GsmtVqlbFTsMRXbhqiUW8kVc2tbTAI-CLwAR0/edit#gid=0"
)

_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def _cred_from_secrets() -> Credentials | None:
    """
    Tenta ler credenciais do Streamlit Secrets em dois formatos:
    - st.secrets["gcp_service_account"] como dict (recomendado)
    - st.secrets["gcp_service_account_json"] como string JSON (alternativa)
    """
    try:
        if "gcp_service_account" in st.secrets:
            data = dict(st.secrets["gcp_service_account"])
            return Credentials.from_service_account_info(data, scopes=_SCOPES)
        if "gcp_service_account_json" in st.secrets:
            data = json.loads(st.secrets["gcp_service_account_json"])
            return Credentials.from_service_account_info(data, scopes=_SCOPES)
    except Exception as e:
        st.error(f"Erro ao ler credenciais de st.secrets: {e}")
        raise
    return None

def _cred_from_file() -> Credentials | None:
    """
    Tenta ler o arquivo local (desenvolvimento): credenciais/gdrive_credenciais.json
    """
    caminho = os.path.join("credenciais", "gdrive_credenciais.json")
    if os.path.exists(caminho):
        return Credentials.from_service_account_file(caminho, scopes=_SCOPES)
    return None

def carregar_credenciais() -> Credentials:
    """
    Carrega credenciais do Google:
      1) Tenta SEMPRE primeiro st.secrets (deploy)
      2) Se não houver, tenta arquivo local (dev)
      3) Se nada der certo, explica exatamente como corrigir
    """
    cred = _cred_from_secrets()
    if cred:
        return cred

    cred = _cred_from_file()
    if cred:
        return cred

    # Se chegou aqui, não tem credencial nenhuma
    msg = (
        "Credenciais não encontradas.\n\n"
        "• No Streamlit Cloud, configure **Settings → Secrets** com a seção [gcp_service_account] "
        "(cole o JSON da Service Account).\n"
        "• Em ambiente local, coloque o arquivo **credenciais/gdrive_credenciais.json**.\n"
        "• Opcional: defina também `G_SHEET_URL` em Secrets.\n"
    )
    st.error(msg)
    raise FileNotFoundError("Credenciais do Google não configuradas.")

# Autoriza acesso ao Google Sheets (com mensagem clara em caso de erro)
try:
    _creds = carregar_credenciais()
    _gc = gspread.authorize(_creds)
    _sheet = _gc.open_by_url(URL_PLANILHA)
except Exception as e:
    st.error(
        "Falha ao conectar no Google Sheets. Verifique as credenciais e a URL da planilha.\n"
        "Dica: use [gcp_service_account] em Secrets e (opcionalmente) G_SHEET_URL."
    )
    raise

# ===================================================
# ❗ RETENTATIVAS API
# ===================================================
def retry_api_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tentativas = 15
        with st.spinner("⏳ Aguardando servidor do Google..."):
            for _ in range(tentativas):
                try:
                    return func(*args, **kwargs)
                except APIError as e:
                    # Quota/Rate limit → aguarda e tenta de novo
                    if "Quota exceeded" in str(e) or "Rate Limit Exceeded" in str(e):
                        time.sleep(5)
                        continue
                    raise
                except Exception:
                    # Erros transitórios variados: tenta de novo
                    time.sleep(2)
                    continue
        st.error("❌ Falha após múltiplas tentativas (quota/instabilidade).")
        raise APIError("Falha após múltiplas tentativas.")
    return wrapper

# ===================================================
# 🔢 AJUSTE DE ESCALA NUMÉRICA
# ===================================================
def _scale(df: pd.DataFrame, tipos: dict, modo: str) -> pd.DataFrame:
    df = df.copy()
    for col, tipo in tipos.items():
        if col not in df.columns:
            continue
        if tipo == "numero100":
            df[col] = df[col] if modo == "mostrar" else df[col] * 100
    return df

# ===================================================
# 🔧 AUXILIARES
# ===================================================
def _map_cols(df: pd.DataFrame) -> dict:
    """{coluna_minúscula: Coluna_Original}"""
    return {c.lower(): c for c in df.columns}

# ===================================================
# 🟩 SELECT
# ===================================================
@retry_api_error
def select(tabela: str, tipos_colunas: dict) -> pd.DataFrame:
    """Lê a aba (worksheet) 'tabela' como DataFrame já com cabeçalho."""
    ws = _sheet.worksheet(tabela)
    rows = ws.get_all_records(value_render_option="UNFORMATTED_VALUE")
    df = pd.DataFrame(rows).rename(columns=str.strip)
    if df.empty:
        df = pd.DataFrame(columns=list(tipos_colunas.keys()))
    return _scale(df, tipos_colunas, "mostrar")

# ===================================================
# 🟦 INSERT
# ===================================================
@retry_api_error
def insert(tabela: str, dados):
    """Insere 1 ou várias linhas. Aceita dict, lista de dicts ou DataFrame."""
    ws = _sheet.worksheet(tabela)
    if isinstance(dados, pd.DataFrame):
        dados = dados.to_dict("records")
    if isinstance(dados, dict):
        dados = [dados]

    # Garante ID
    for i, item in enumerate(dados, start=1):
        if not item.get("ID"):
            item["ID"] = cria_id(sequencia=str(i))

    df = pd.DataFrame(dados)
    header = ws.row_values(1) or list(df.columns)

    # Cria/atualiza cabeçalho
    if not ws.row_values(1):
        ws.insert_row(header, 1)
    else:
        for c in df.columns:
            if c not in header:
                header.append(c)
        ws.update("A1", [header])

    # Monta linhas na ordem do header
    linhas = [[r.get(h, "") for h in header] for r in df.to_dict("records")]
    ws.insert_rows(linhas, row=len(ws.get_all_values()) + 1)

# ===================================================
# 🟨 UPDATE
# ===================================================
@retry_api_error
def update(tabela: str, campos: list, valores: list, where: str, tipos_colunas: dict) -> int:
    """
    Atualiza linhas que satisfaçam o filtro 'where' (ex.: "ID,eq,123").
    Retorna quantas linhas foram atualizadas.
    """
    ws = _sheet.worksheet(tabela)
    df = pd.DataFrame(ws.get_all_records()).rename(columns=str.strip)
    if df.empty:
        return 0

    df = _scale(df, tipos_colunas, "gravar")
    col_map = _map_cols(df)

    campo, _, alvo = [s.strip() for s in where.split(",")]
    real = col_map[campo.lower()]

    # Ajuste se tipo for numero100
    if tipos_colunas.get(real) == "numero100":
        try:
            alvo = str(float(alvo))
        except Exception:
            pass

    linhas = df.index[df[real].astype(str) == str(alvo)]
    if linhas.empty:
        return 0

    for lin in linhas:
        for c, v in zip(campos, valores):
            real_c = col_map[c.lower()]
            ws.update_cell(lin + 2, df.columns.get_loc(real_c) + 1, v)
    return len(linhas)

# ===================================================
# 🟥 DELETE
# ===================================================
@retry_api_error
def delete(tabela: str, where: str, tipos_colunas: dict) -> int:
    """Exclui linhas que atendam 'where'. Retorna quantas foram excluídas."""
    ws = _sheet.worksheet(tabela)
    df = pd.DataFrame(ws.get_all_records()).rename(columns=str.strip)
    if df.empty:
        return 0

    df = _scale(df, tipos_colunas, "gravar")
    col_map = _map_cols(df)

    campo, _, alvo = [s.strip() for s in where.split(",")]
    real = col_map[campo.lower()]

    if tipos_colunas.get(real) == "numero100":
        try:
            alvo = str(float(alvo))
        except Exception:
            pass

    linhas = df.index[df[real].astype(str) == str(alvo)]
    for i in sorted(linhas, reverse=True):
        ws.delete_rows(i + 2)
    return len(linhas)

# ===================================================
# 🔑 PERMISSÃO DE USUÁRIO (se usar no seu fluxo)
# ===================================================
@retry_api_error
def verificar_permissao_usuario(usuario_id: str, funcionalidade_nome: str) -> bool:
    permissoes = select("permissoes", {"ID_Usuario": "texto", "ID_Funcionalidade": "texto"})
    funcs = select("funcionalidades", {"ID": "id", "Nome": "texto"})
    if funcs.empty:
        return False
    alvo = funcs[funcs["Nome"] == funcionalidade_nome]
    if alvo.empty:
        return False
    funcionalidade_id = alvo["ID"].values[0]
    permissoes_usuario = permissoes[permissoes["ID_Usuario"] == usuario_id]
    return funcionalidade_id in permissoes_usuario["ID_Funcionalidade"].values
# fim
