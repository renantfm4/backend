from fastapi import BackgroundTasks
from smtplib import SMTP
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


smtp_server = os.getenv("SMTP_SERVER")
smtp_port = int(os.getenv("SMTP_PORT", 587))
smtp_username = os.getenv("SMTP_USERNAME")
smtp_password = os.getenv("SMTP_PASSWORD")

def send_invite_email(email: str, invite_link: str):
    subject = "Convite para completar seu cadastro"
    
    body = f"""
    <html>
    <head></head>
    <body>
        <p>Olá,</p>
        <p>Você foi convidado a acessar nossa plataforma. Para concluir seu cadastro, clique no link abaixo:</p>
        <p><a href="{invite_link}" target="_blank" style="font-size: 16px; color: blue; text-decoration: underline;">
            Completar Cadastro
        </a></p>
        <p>Este link expira em 24 horas.</p>
        <p>Atenciosamente,<br>Equipe do Sistema.</p>
    </body>
    </html>
    """

    print("LINK TOKEN", invite_link)
    send_email(email, subject, body, html=True)

def send_reset_password_email(email: str, reset_link: str):
    subject = "Redefinição de Senha"
    
    body = f"""
    <html>
    <body>
        <p>Olá,</p>
        <p>Recebemos uma solicitação para redefinir sua senha. Para criar uma nova senha, clique no link abaixo:</p>
        <p><a href="{reset_link}" style="font-size: 16px; color: blue; text-decoration: underline;">Redefinir Senha</a></p>
        <p>Se você não solicitou esta redefinição, ignore este e-mail.</p>
        <p>Atenciosamente,<br>Equipe do Sistema.</p>
    </body>
    </html>
    """

    print("LINK TOKEN", reset_link)
    send_email(email, subject, body, html=True)


def send_email(to_email, subject, body, html=False):
    msg = MIMEMultipart()
    msg["From"] = smtp_username
    msg["To"] = to_email
    msg["Subject"] = subject

    # Definir o tipo de conteúdo como HTML ou texto simples
    if html:
        msg.attach(MIMEText(body, "html"))
    else:
        msg.attach(MIMEText(body, "plain"))

    with SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(smtp_username, to_email, msg.as_string())
