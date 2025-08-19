# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText
import streamlit as st

def _carregar_credenciais_gmail():
    """
    Carrega credenciais do Gmail.
    - Online (Streamlit Cloud): usa [gmail] em st.secrets
    - Local: usa arquivo credenciais/gmail.py
    """
    try:
        usuario = st.secrets["gmail"]["usuario"]
        senhaapp = st.secrets["gmail"]["senhaapp"]
        smtp = st.secrets["gmail"].get("SMTP_SERVIDOR", "smtp.gmail.com")
        porta = int(st.secrets["gmail"].get("SMTP_PORTA", 587))
        return usuario, senhaapp, smtp, porta
    except Exception:
        # fallback local
        from credenciais.gmail import USUARIO, SENHA_APP, SMTP_SERVIDOR, SMTP_PORTA
        return USUARIO, SENHA_APP, SMTP_SERVIDOR, SMTP_PORTA


def enviar_email(destinatario, assunto, mensagem):
    remetente, senha, servidor, porta = _carregar_credenciais_gmail()
    msg = MIMEText(mensagem, "html", "utf-8")
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = destinatario

    try:
        with smtplib.SMTP(servidor, porta) as smtp:
            smtp.starttls()
            smtp.login(remetente, senha)
            smtp.sendmail(remetente, destinatario, msg.as_string())
        return True
    except Exception as e:
        st.error(f"❌ Erro ao enviar e-mail: {e}")
        return False
