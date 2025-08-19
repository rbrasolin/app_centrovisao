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

# URL da planilha
if hasattr(st, "secrets") and "G_SHEET_URL" in st.secrets:
    URL_PLANILHA = st.secrets["G_SHEET_URL"]
else:
    # fallback local
    URL_PLANILHA = "https://docs.google.com/spreadsheets/d/SEU_ID/edit#gid=0"

_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def _cred_from_secrets() -> Credentials | None:
    """Tenta carregar credenciais do st.secrets"""
    try:
        if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
            data = dict(st.secrets["gcp_service_account"])
            return Credentials.from_service_account_info(data, scopes=_SCOPES)
        if hasattr(st, "secrets") and "gcp_service_account_json" in st.secrets:
            data = json.loads(st.secrets["gcp_service_account_json"])
            return Credentials.from_service_account_info(data, scopes=_SCOPES)
    except Exception as e:
        st.error(f"Erro ao ler credenciais do secrets: {e}")
    return None

def _cred_from_file() -> Credentials | None:
    """Tenta ler credenciais locais (arquivo JSON)"""
    caminho = os.path.join("credenciais", "gdrive_credenciais.json")
    if os.path.exists(caminho):
        return Credentials.from_service_account_file(caminho, scopes=_SCOPES)
    return None

def carregar_credenciais() -> Credentials:
    cred = _cred_from_secrets()
    if cred:
        return cred

    cred = _cred_from_file()
    if cred:
        return cred

    st.error("❌ Nenhuma credencial encontrada. Configure [gcp_service_account] em secrets ou adicione credenciais/gdrive_credenciais.json.")
    raise FileNotFoundError("Credenciais do Google não configuradas.")

# Autoriza acesso ao Google Sheets
try:
    _creds = carregar_credenciais()
    _gc = gspread.authorize(_creds)
    _sheet = _gc.open_by_url(URL_PLANILHA)
except Exception as e:
    st.error(f"Falha ao conectar ao Google Sheets: {e}")
    raise

# ===================================================
# ❗ RETENTATIVAS API
# ===================================================
def retry_api_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tentativas = 10
        for _ in range(tentativas):
            try:
                return func(*args, **kwargs)
            except APIError as e:
                if "Quota exceeded" in str(e) or "Rate Limit Exceeded" in str(e):
                    time.sleep(5)
                    continue
                raise
            except Exception:
                time.sleep(2)
                continue
        st.error("❌ Falha após múltiplas tentativas.")
        raise APIError("Erro persistente")
    return wrapper

# ===================================================
# 🔧 FUNÇÕES AUXILIARES
# ===================================================
def _scale(df: pd.DataFrame, tipos: dict, modo: str) -> pd.DataFrame:
    df = df.copy()
    for col, tipo in tipos.items():
        if col not in df.columns:
            continue
        if tipo == "numero100":
            df[col] = df[col] if modo == "mostrar" else df[col] * 100
    return df

def _map_cols(df: pd.DataFrame) -> dict:
    return {c.lower(): c for c in df.columns}

# ===================================================
# 🟩 SELECT
# ===================================================
@retry_api_error
def select(tabela: str, tipos_colunas: dict) -> pd.DataFrame:
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
    ws = _sheet.worksheet(tabela)
    if isinstance(dados, pd.DataFrame):
        dados = dados.to_dict("records")
    if isinstance(dados, dict):
        dados = [dados]

    for i, item in enumerate(dados, start=1):
        if not item.get("ID"):
            item["ID"] = cria_id(sequencia=str(i))

    df = pd.DataFrame(dados)
    header = ws.row_values(1) or list(df.columns)

    if not ws.row_values(1):
        ws.insert_row(header, 1)
    else:
        for c in df.columns:
            if c not in header:
                header.append(c)
        ws.update("A1", [header])

    linhas = [[r.get(h, "") for h in header] for r in df.to_dict("records")]
    ws.insert_rows(linhas, row=len(ws.get_all_values()) + 1)

# ===================================================
# 🟨 UPDATE
# ===================================================
@retry_api_error
def update(tabela: str, campos: list, valores: list, where: str, tipos_colunas: dict) -> int:
    ws = _sheet.worksheet(tabela)
    df = pd.DataFrame(ws.get_all_records()).rename(columns=str.strip)
    if df.empty:
        return 0

    df = _scale(df, tipos_colunas, "gravar")
    col_map = _map_cols(df)

    campo, _, alvo = [s.strip() for s in where.split(",")]
    real = col_map[campo.lower()]

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
    ws = _sheet.worksheet(tabela)
    df = pd.DataFrame(ws.get_all_records()).rename(columns=str.strip)
    if df.empty:
        return 0

    df = _scale(df, tipos_colunas, "gravar")
    col_map = _map_cols(df)

    campo, _, alvo = [s.strip() for s in where.split(",")]
    real = col_map[campo.lower()]

    linhas = df.index[df[real].astype(str) == str(alvo)]
    for i in sorted(linhas, reverse=True):
        ws.delete_rows(i + 2)
    return len(linhas)
