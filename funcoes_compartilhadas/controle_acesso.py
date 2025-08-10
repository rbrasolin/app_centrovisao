# -*- coding: utf-8 -*-
"""
Controle de Acesso Genérico
- Login
- Logout
- Cadastro de Usuário
- Cadastro de Permissões
- Verificação de Acesso
"""

import streamlit as st
import pandas as pd
import hashlib
from funcoes_compartilhadas import conversa_banco
from PIL import Image
import base64
from io import BytesIO


# imagem
def image_base64(path):
    img = Image.open(path)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


# 🔐 Tabelas usadas no Google Sheets
TABELA_USUARIOS = "usuarios"
TABELA_PERMISSOES = "permissoes"

TIPOS_USUARIOS = {
    "ID": "id",
    "Nome": "texto",
    "Email": "texto",
    "Senha": "texto",
}

TIPOS_PERMISSOES = {
    "ID": "id",
    "ID_Usuario": "texto",
    "Programa": "texto",
    "Caminho": "texto",
}


# ──────────────────────────────────────────────────────────────────────────────
# 🔑 Função para criptografar senha
def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


# ──────────────────────────────────────────────────────────────────────────────
# 🚪 Login
# ──────────────────────────────────────────────────────────────────────────────

def login():
    from funcoes_compartilhadas.envia_email import enviar_email
    import random, string

    col1, col2, col3 = st.columns([0.35, 0.3, 0.35])

    with col2:
        # ─── Logo ────────────────────────────────────────────────
        logo_data = image_base64("imagens/logo.png")
        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="{logo_data}" style="width:70%; max-width:240px; margin-bottom:40px" />
            </div>
            """,
            unsafe_allow_html=True
        )

        # ─── Título ───────────────────────────────────────────────
        st.markdown("<h3 style='text-align:center; color:#444;'>Entre no Sistema</h3>", unsafe_allow_html=True)

        # ─── Campos ───────────────────────────────────────────────
        email = st.text_input("Email", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_senha")

        # ─── CSS do campo senha ───────────────────────────────────
        st.markdown("""
            <style>
            div[data-testid="stTextInput"] > div:first-child {
                position: relative !important;
            }
            div[data-testid="stTextInput"] svg {
                position: absolute !important;
                right: 12px !important;
                top: 2.5em !important;
                transform: none !important;
                z-index: 2;
                pointer-events: none;
            }
            input[type="password"] {
                padding-right: 2.5rem !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # ─── CSS do botão Entrar ──────────────────────────────────
        st.markdown("""
            <style>
            div[data-testid="stButton"] > button {
                display: block;
                margin: 0 auto;
                background-color:#4CAF50;
                color:#ffffff;
                font-size:14px;
                padding:6px 20px;
                border:none;
                border-radius:5px;
                transition: background-color 0.2s ease;
            }
            div[data-testid="stButton"] > button:hover {
                background-color: #388E3C;
                color: white;
            }
            </style>
        """, unsafe_allow_html=True)

        # ─── Botão Entrar ─────────────────────────────────────────
        if st.button("Entrar", key="login_botao"):
            df = conversa_banco.select(TABELA_USUARIOS, TIPOS_USUARIOS)
            df = df[df["Email"].str.lower() == email.lower()]
            st.write("Debug DF Usuarios:", df)
            if not df.empty:
                senha_hash = hash_senha(senha)

                #Debug
                st.write("Hash digitado:", senha_hash)
                st.write("Hash planilha:", df.iloc[0]["Senha"])

                
                if df.iloc[0]["Senha"] == senha_hash:
                    st.session_state["usuario_logado"] = {
                        "ID": str(df.iloc[0]["ID"]),
                        "Nome": df.iloc[0]["Nome"],
                        "Email": df.iloc[0]["Email"],
                    }
                    st.success(f"✅ Bem-vindo, {df.iloc[0]['Nome']}!")
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta.")
            else:
                st.error("❌ Usuário não encontrado.")

        # ─── CSS para centralizar o botão popover ─────────────────
        st.markdown("""
            <style>
            div[data-testid="stPopoverContainer"] > button {
                display: block;
                margin-left: auto;
                margin-right: auto;
            }
            </style>
        """, unsafe_allow_html=True)

        # ─── Link de redefinição com hover estilizado ─────────────
        st.markdown("""
            <style>
            a.link-esqueci:link,
            a.link-esqueci:visited {
                text-decoration: none;
                color: #777 !important;
                font-size: 12px;
                font-weight: normal;
            }

            a.link-esqueci:hover {
                color: #1976D2 !important;
                font-weight: bold;
            }
            </style>
            <div style='text-align:center; margin-top:10px'>
                <a href='?recuperar=1' class='link-esqueci'>
                    Esqueci minha senha
                </a>
            </div>
        """, unsafe_allow_html=True)







# ──────────────────────────────────────────────────────────────────────────────
# 🔓 Logout
def logout():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.pop("usuario_logado", None)
        st.rerun()

def logoutX():

    st.sidebar.markdown("---")

    usuario = st.session_state.get("usuario_logado")
    if usuario and isinstance(usuario, dict) and "Nome" in usuario:
        st.sidebar.markdown(
            f"<div style='text-align:center'><em>Usuário: {usuario['Nome']}</em></div>",
            unsafe_allow_html=True,
        )
    st.sidebar.markdown("\n")
    st.markdown("""
        <style>
        section[data-testid="stSidebar"] .stButton:last-of-type {
            display: flex; justify-content: center;
        }
        section[data-testid="stSidebar"] .stButton:last-of-type button {
            background-color:#e0e0e0;color:#333;font-size:14px;
            padding:6px 20px;border:none;border-radius:5px;
        }
        section[data-testid="stSidebar"] .stButton:last-of-type button:hover {
            background-color:#f44336;color:white;
        }
        header[data-testid="stHeader"] div[role="button"]{display:none!important;}
        </style>
    """, unsafe_allow_html=True)

    if st.sidebar.button("Sair"):
        st.session_state.pop("usuario_logado", None)        
        st.session_state.clear()
        st.rerun()



# ──────────────────────────────────────────────────────────────────────────────
# 🛑 Verificar se usuário está logado
def usuario_logado():
    return st.session_state.get("usuario_logado")


# ──────────────────────────────────────────────────────────────────────────────
# ✅ Verificar permissões de menus
def menus_liberados():
    if not usuario_logado():
        return []

    usuario_id = str(st.session_state["usuario_logado"]["ID"])

    # 🔥 Admin (ID=1 ou ADMIN) vê tudo
    if usuario_id in ["1", "ADMIN"]:
        return None

    df = conversa_banco.select("permissoes", {
        "ID": "id",
        "ID_Usuario": "texto",
        "ID_Funcionalidade": "texto",
    })

    if df.empty:
        return []

    df = df[df["ID_Usuario"] == usuario_id]

    return df.to_dict(orient="records")
