from fastapi import BackgroundTasks
from smtplib import SMTP
import os

smtp_server = os.getenv("SMTP_SERVER")
smtp_port = int(os.getenv("SMTP_PORT", 587))
smtp_username = os.getenv("SMTP_USERNAME")
smtp_password = os.getenv("SMTP_PASSWORD")

def send_invite_email(email: str, invite_link: str):
    subject = "Convite para completar seu cadastro"
    body = f"""
    Olá,
    
    Você foi convidado a acessar nossa plataforma. Para concluir seu cadastro, clique no link abaixo:

    {invite_link}

    Este link expira em 24 horas.

    Atenciosamente,
    Equipe do Sistema.
    """
    send_email(email, subject, body)

def send_reset_password_email(email: str, reset_link: str):
    subject = "Redefinição de Senha"
    body = f"""
    Olá,

    Recebemos uma solicitação para redefinir sua senha. Para criar uma nova senha, clique no link abaixo:

    {reset_link}

    Se você não solicitou esta redefinição, ignore este e-mail.

    Atenciosamente,
    Equipe do Sistema.
    """
    send_email(email, subject, body)


def send_email(to_email, subject, body):
    message = f"Subject: {subject}\n\n{body}"
    # to utf-8
    message = message.encode('utf-8')

    with SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(smtp_username, to_email, message)