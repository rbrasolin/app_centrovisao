# -*- coding: utf-8 -*-
# funcoes_compartilhadas/envia_email.py

import smtplib
from email.mime.text import MIMEText
import streamlit as st
import os

# ===================================================
# 🔧 Helpers de carga robusta
# ===================================================
def _get_from_mapping(mapping: dict, candidates: list, label: str) -> str:
    """Tenta obter a primeira chave disponível na ordem dos 'candidates'."""
    for k in candidates:
        if k in mapping and mapping[k]:
            return mapping[k]
    raise KeyError(f"Chave '{label}' não encontrada. Procurei por: {', '.join(candidates)}")

def _get_from_module(mod, candidates: list, label: str) -> str:
    """Tenta obter o primeiro atributo disponível na ordem dos 'candidates'."""
    for k in candidates:
        if hasattr(mod, k):
            v = getattr(mod, k)
            if v:
                return v
    raise AttributeError(f"Atributo '{label}' não encontrado no módulo. Procurei por: {', '.join(candidates)}")

# ===================================================
# 🔐 Carrega credenciais (Cloud via Secrets | Local via credenciais/gmail.py)
# ===================================================
def _carregar_credenciais_gmail():
    """
    Ordem de busca:
    1) Streamlit Secrets (quando existir e tiver o bloco [gmail])
    2) Módulo local credenciais/gmail.py
    Aceita múltiplos nomes de variáveis para evitar erro de grafia/acento.
    """
    # Candidatos aceitos para usuário e senha (suporta variações comuns)
    user_candidates = ["usuario", "usuário", "EMAIL_REMETENTE", "email", "user", "username", "remetente"]
    pass_candidates = ["senhaapp", "SENHA_APP", "EMAIL_SENHA", "senha", "password", "senha_aplicativo"]

    # 1) Tenta Secrets de forma segura (sem estourar quando não existir secrets.toml local)
    use_secrets = False
    if os.environ.get("STREAMLIT_RUNTIME"):  # estamos no runtime do Streamlit
        try:
            # ⚠️ 'in st.secrets' tenta parsear o arquivo; por isso o try/except
            if "gmail" in st.secrets:
                use_secrets = True
        except Exception:
            use_secrets = False

    if use_secrets:
        gmail_secrets = dict(st.secrets["gmail"])
        remetente = _get_from_mapping(gmail_secrets, user_candidates, "usuário/remetente (secrets)")
        senha_app = _get_from_mapping(gmail_secrets, pass_candidates, "senha de app (secrets)")
        return remetente, senha_app

    # 2) Fallback local: credenciais/gmail.py
    try:
        from credenciais import gmail  # não commitar esse arquivo no repositório público!
    except Exception as e:
        raise ImportError(
            "Não encontrei o módulo local 'credenciais/gmail.py'. "
            "Crie-o com suas credenciais OU configure o bloco [gmail] em Secrets no Streamlit Cloud."
        ) from e

    remetente = _get_from_module(gmail, user_candidates, "usuário/remetente (local)")
    senha_app = _get_from_module(gmail, pass_candidates, "senha de app (local)")
    return remetente, senha_app

try:
    REMETENTE, SENHA_APP = _carregar_credenciais_gmail()
except Exception as e:
    # Mostra no app e repropaga para facilitar diagnóstico
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
        # Define o tipo da mensagem (texto puro ou HTML)
        conteudo_tipo = "html" if html else "plain"
        msg = MIMEText(mensagem, conteudo_tipo)
        msg["Subject"] = assunto
        msg["From"] = REMETENTE
        msg["To"] = destino

        # Conexão com servidor SMTP do Gmail (TLS na porta 587)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(REMETENTE, SENHA_APP)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        st.error(f"Erro ao enviar email: {e}")
        return False
