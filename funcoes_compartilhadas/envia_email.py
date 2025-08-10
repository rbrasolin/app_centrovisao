# funcoes_compartilhadas/envia_email.py
import smtplib
from email.mime.text import MIMEText
from credenciais import gmail

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
        remetente = gmail.usuario
        senha_app = gmail.senhaapp

        # Define o tipo da mensagem
        tipo = "html" if html else "plain"
        msg = MIMEText(mensagem, tipo)
        msg["Subject"] = assunto
        msg["From"] = remetente
        msg["To"] = destino

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(remetente, senha_app)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        print("Erro ao enviar email:", e)
        return False
