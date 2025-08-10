# -*- coding: utf-8 -*-
import streamlit as st
import importlib
import sys
import streamlit.components.v1 as components


from funcoes_compartilhadas.estilos import (
    aplicar_estilo_padrao,
    clear_caches,
)

from funcoes_compartilhadas.controle_acesso import (
    login, usuario_logado, menus_liberados, logoutX
)
from funcoes_compartilhadas import conversa_banco


# VAI SERVIR PARA PODER RECARREGAR A PAGINA AUXILIAR DE RECUPERAÇÃO DE SENHA
from urllib.parse import parse_qs
def reload_module(path: str):
    if path in sys.modules:
        return importlib.reload(sys.modules[path])
    return importlib.import_module(path)
query_params = st.query_params.to_dict()
if query_params.get("recuperar") == "1":
    mod = reload_module("paginas.redefinir_senha")
    mod.app()
    st.stop()


# Config inicial
st.set_page_config(page_title="app_centrovisao.", page_icon="👁️", layout="wide")
aplicar_estilo_padrao()

# CSS ajuste alinhamento do menu
st.markdown("""
    <style>
    [data-testid="stSidebar"] .stRadio > div {
        flex-direction: column;
        gap: 0.3rem;
    }
    [data-testid="stSidebar"] label {
        align-items: center;
        display: flex;
        gap: 0.5rem;
        word-break: break-word;
    }
    </style>
""", unsafe_allow_html=True)

components.html(
    """
    <script>
      const root = parent.document.documentElement;
      root.setAttribute('lang', 'pt-BR');
      root.setAttribute('translate', 'no');
      const meta = parent.document.createElement('meta');
      meta.name    = 'google';
      meta.content = 'notranslate';
      parent.document.head.appendChild(meta);
    </script>
    """,
    height=0,
)

def set_tab_title(title: str, icon_url: str | None = None) -> None:
    js = f"""<script>document.title = "{title}";"""
    if icon_url:
        js += f"""
        const link = document.querySelector('link[rel*="icon"]') || document.createElement('link');
        link.type = 'image/png';
        link.rel  = 'shortcut icon';
        link.href = '{icon_url}';
        document.head.appendChild(link);"""
    js += "</script>"
    st.markdown(js, unsafe_allow_html=True)

def reload_module(path: str):
    if path in sys.modules:
        return importlib.reload(sys.modules[path])
    return importlib.import_module(path)

def mudar_pagina(alvo: str) -> None:
    if st.session_state.get("page") != alvo:
        st.session_state["page"] = alvo
        clear_caches()
        st.rerun()

# ────────────── LOGIN ──────────────
if not usuario_logado():
    login()
    st.stop()

# ───── SIDEBAR (TUDO antes do corpo do app) ─────

# Lê menus e funcionalidades do banco
menus = conversa_banco.select("menus", {
    "ID": "id",
    "Nome": "texto",
    "Ordem": "numero100",
})

funcionalidades = conversa_banco.select("funcionalidades", {
    "ID": "id",
    "ID_Menu": "texto",
    "Nome": "texto",
    "Caminho": "texto",
})

# Organiza menus por ordem
menus = menus.sort_values(by="Ordem")

# Aplica permissões
permissoes = menus_liberados()  # None → acesso total (admin)

if permissoes is not None:
    funcionalidades = funcionalidades[
        funcionalidades["ID"].astype(str).isin(
            [str(p["ID_Funcionalidade"]) for p in permissoes]
        )
    ]

# Monta estrutura dos menus
menu_disponivel = {}
for _, menu in menus.iterrows():
    # Compara como string, sempre!
    itens = funcionalidades[funcionalidades["ID_Menu"].astype(str) == str(menu["ID"])]
    if not itens.empty:
        menu_disponivel[menu["Nome"]] = {
            row["Caminho"]: row["Nome"]
            for _, row in itens.iterrows()
        }

if not menu_disponivel:
    st.warning("⚠️ Você não tem acesso a nenhum menu.")
    st.stop()

# MENU LATERAL (Sidebar)
st.sidebar.image("imagens/logo.png", use_container_width=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)

area = st.sidebar.selectbox("Área:", list(menu_disponivel.keys()))

funcionalidades_disp = menu_disponivel[area]
rotulo = st.sidebar.radio(
    "Funcionalidade:",
    ["Selecionar..."] + list(funcionalidades_disp.values()),
    index=0
)

# 🔥 LOGOUT NO FINAL DO SIDEBAR 🔥
logoutX()   # <--- SEMPRE AQUI, depois de tudo do menu lateral

if rotulo == "Selecionar...":
    st.stop()

# Corpo do app (só a partir daqui!)
arquivo = next(k for k, v in funcionalidades_disp.items() if v == rotulo)
set_tab_title(f"{rotulo} — Meu App")

try:
    mod = reload_module(f"paginas.{arquivo}")
    mod.app()
except Exception as e:
    st.error(f"Erro ao carregar a página '{arquivo}': {e}")
