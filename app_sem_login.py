# -*- coding: utf-8 -*-
# app.py – carrega páginas Streamlit com menu agrupado por área

import streamlit as st
import importlib
import sys
import streamlit.components.v1 as components

from funcoes_compartilhadas.estilos import (
    aplicar_estilo_padrao,
    clear_caches,
)


# ─── 1. Configuração global ──────────────────────────────────────
st.set_page_config(page_title="Meu App com I.A.", page_icon="⚡", layout="wide")
aplicar_estilo_padrao()

# deixa o botão "radio" alinhado com o menu
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


# ─── 2. Funções utilitárias ──────────────────────────────────────

def set_tab_title(title: str, icon_url: str | None = None) -> None:
    """Altera o título da aba e opcionalmente o favicon."""
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
    """Importa ou recarrega um módulo (evita cache de código)."""
    if path in sys.modules:
        return importlib.reload(sys.modules[path])
    return importlib.import_module(path)


def mudar_pagina(alvo: str) -> None:
    """Se a opção no menu mudou, limpa caches e força rerun."""
    if st.session_state.get("page") != alvo:
        st.session_state["page"] = alvo
        clear_caches()
        st.rerun()


# ─── 3. Definição do menu ────────────────────────────────────────

PAGINAS = {
    "Financeiro": {
        "categorias": "Gerenciar Categorias",
        "bancos": "Gerenciar Bancos",
        "lancamentos": "Lançamentos Financeiros",
        "relatorio_pdf": "Relatório em PDF",
    },
    "Testes": {
        "calculo_imc": "Calculadora de IMC",
        "situacao_conta": "Situação da Conta",
    }
}


# ─── 4. Construção do menu lateral ───────────────────────────────

st.sidebar.image("imagens/logo.png", use_container_width=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# 🔸 Menu de Área (Selectbox)
area = st.sidebar.selectbox("Área:", list(PAGINAS.keys()))

# 🔸 Menu de Funcionalidade (Radio)
funcionalidades = PAGINAS[area]
rotulo = st.sidebar.radio(
    "Funcionalidade:",
    ["Selecionar..."] + list(funcionalidades.values()),
    index=0
)

# 🔍 Se não selecionou, para a execução
if rotulo == "Selecionar...":
    st.stop()

# 🔍 Localiza o nome do arquivo com base na escolha
arquivo = next(k for k, v in funcionalidades.items() if v == rotulo)


# ─── 5. Título da aba do navegador ───────────────────────────────
set_tab_title(f"{rotulo} — Meu App")


# ─── 6. Carrega e executa a página selecionada ───────────────────
mod = reload_module(f"paginas.{arquivo}")
mod.app()


