# -*- coding: utf-8 -*-
# funcoes_compartilhadas/envia_email.py

import smtplib
from email.mime.text import MIMEText
import streamlit as st

# ===================================================
# 🔐 Carrega credenciais de forma híbrida
# ===================================================
try:
    if hasattr(st, "secrets") and "gmail" in getattr(st, "secrets", {}):
        # Ambiente online (Streamlit Cloud)
        remetente = st.secrets["gmail"]["usuario"]
        senha_app = st.secrets["gmail"]["senhaapp"]
    else:
        # Ambiente local (arquivo credenciais/gmail.py)
        from credenciais import gmail
        remetente = gmail.usuario
        senha_app = gmail.senhaapp
except Exception as e:
    st.error(f"Erro ao carregar credenciais do Gmail: {e}")
    raise

# ===================================================
# 📧 Função para enviar e-mail
# ===================================================
def enviar_email(destino: str, assunto: str, mensagem: str, html: bool = False) -> bool:
    """
    Envia e-mail com suporte a texto simples ou HTML.

    Parâmetros:
    - destino: email do destinatário
    - assunto: assunto do e-mail
    - mensagem: conteúdo (texto ou html)
    - html: define se o conteúdo será tratado como HTML (True) ou texto puro (False)
    """
    try:
        # Define o tipo da mensagem
        tipo = "html" if html else "plain"
        msg = MIMEText(mensagem, tipo)
        msg["Subject"] = assunto
        msg["From"] = remetente
        msg["To"] = destino

        # Conexão com servidor SMTP
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(remetente, senha_app)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        st.error(f"Erro ao enviar email: {e}")
        return False
