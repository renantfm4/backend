import asyncio
from sqlalchemy import select
from app.database.models import Role, User
from app.database.database import SessionLocal 
from app.core.security import get_password_hash
import os

FIXED_ROLES = ["Admin", "Supervisor", "Pesquisador"]
# ADMIN_DATA = {
#     "nome_usuario": "Administrador",
#     "email": "admin@seusistema.com",
#     "cpf": "00000000000",
#     "senha": "senhaadmin", 
#     "is_active": True,
# }

ADMIN_DATA = {
    "nome_usuario": os.getenv("ADMIN_NOME_INICIAL"),
    "email": os.getenv("ADMIN_EMAIL_INICIAL"),
    "cpf": os.getenv("ADMIN_CPF_INICIAL"),
    "senha": os.getenv("ADMIN_SENHA_INICIAL"),
    "is_active": True,
}

async def seed_data():
    async with SessionLocal() as session:
        result = await session.execute(select(Role))
        roles_existentes = result.scalars().all()

        if not roles_existentes:
            for role_name in FIXED_ROLES:
                role = Role(name=role_name)
                session.add(role)
            await session.commit()
            print("Roles inseridas:", FIXED_ROLES)
        else:
            print("Roles já existem.")

        result = await session.execute(select(User).filter(User.email == ADMIN_DATA["email"]))
        admin_existente = result.scalars().first()

        if not admin_existente:
            admin = User(
                nome_usuario=ADMIN_DATA["nome_usuario"],
                email=ADMIN_DATA["email"],
                cpf=ADMIN_DATA["cpf"],
                senha_hash=get_password_hash(ADMIN_DATA["senha"]),
                is_active=ADMIN_DATA["is_active"],
            )
            result = await session.execute(select(Role).filter(Role.name == "Admin"))
            admin_role = result.scalars().first()
            if admin_role:
                admin.roles.append(admin_role)
            session.add(admin)
            await session.commit()
            print("Usuário admin criado.")
        else:
            print("Usuário admin já existe.")
