# -*- coding: utf-8 -*-
"""
Estilo global:
• Tipografia Poppins
• Tamanho derivado (h1, h2, menu, etc.)
• Título sticky
• Responsividade dos botões e colunas
• Mantém Material Icons nos ícones da sidebar
"""

import streamlit as st
from math import ceil

# ─── 1. Controles ────────────────────────────────────────────────
FONTE_BASE = 22
PHI = 1.618

FONTES = {
    "poppins":        "'Poppins', sans-serif",
    "material_icons": "'Material Icons'",
    "h1":             f"{FONTE_BASE}px",
    "h2_h3":          f"{FONTE_BASE/PHI:.0f}px",
    "p":              f"{FONTE_BASE/PHI:.0f}px",
    "li":             f"{ceil(FONTE_BASE/PHI*0.8):.0f}px",
    "menu":           f"{ceil(FONTE_BASE/PHI*0.9):.0f}px",
}

# ─── 2. CSS global ───────────────────────────────────────────────
def aplicar_estilo_padrao() -> None:
    st.markdown(
f"""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">

<style>
/* Aplica Poppins em tudo, EXCETO nos ícones */
*:not([data-testid="stIconMaterial"]):not(.material-icons) {{
    font-family: 'Poppins', sans-serif !important;
}}

/* Mantém Material Icons nos ícones */
.material-icons,
[data-testid="stIconMaterial"] {{
    font-family: 'Material Icons' !important;
}}


/* === Variáveis === */
:root {{
    --fonte-poppins  : {FONTES['poppins']};
    --fonte-material : {FONTES['material_icons']};
    --tam-h1         : {FONTES['h1']};
    --tam-h2-h3      : {FONTES['h2_h3']};
    --tam-p          : {FONTES['p']};
    --tam-li         : {FONTES['li']};
    --tam-menu       : {FONTES['menu']};
}}

/* === Tipografia Base === */
html, body, .stApp {{ font-family: var(--fonte-poppins) !important; }}
.material-icons {{ font-family: var(--fonte-material) !important; }}

h1 {{ font-size: var(--tam-h1) !important; line-height:1.2; margin-top:0; }}
h2, h3 {{ font-size: var(--tam-h2-h3) !important; line-height:1.3; }}
p {{ font-size: var(--tam-p) !important; line-height:1.45; }}
li {{ font-size: var(--tam-li) !important; line-height:1.45; }}
[data-testid="stSidebar"] * {{ font-size: var(--tam-menu) !important; }}

/* === Layout Global === */
.block-container {{
    padding-top: 0;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 100%;
}}

/* === Header sticky === */
#page-title-wrapper {{
    position: sticky;
    top: 0;
    z-index: 100;
    padding: .5rem 0 .75rem 0;
    background-color: inherit;
}}

/* === Remove Footer === */
footer {{ display: none !important; }}

/* === ⬇️ Responsividade das colunas e botões === */

/* 🔥 Desktop: mantém colunas na mesma linha com gap */
div[data-testid="stHorizontalBlock"] {{
    gap: 0.75rem;
    flex-wrap: nowrap;
}}

/* 🔥 Mobile: quebra linha, botões em 100% */
@media (max-width: 768px) {{
    div[data-testid="stHorizontalBlock"] {{
        flex-wrap: wrap !important;
    }}

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
        flex: 1 1 100% !important;
        max-width: 100% !important;
    }}

    button, div[role="button"] {{
        width: 100% !important;
    }}
}}
</style>
""",
        unsafe_allow_html=True,
    )



# ─── 3. Utilitários ───────────────────────────────────────────────
def set_page_title(texto: str) -> None:
    st.markdown(
        f"<div id='page-title-wrapper'><h1>{texto}</h1></div>",
        unsafe_allow_html=True,
    )

def clear_caches() -> None:
    st.cache_data.clear()
    st.cache_resource.clear()
