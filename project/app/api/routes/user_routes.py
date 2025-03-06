from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ...database.database import get_db
# from ...crud.user import create_user, assign_role_to_user, assign_permission_to_user, assign_user_to_group
from ...database.schemas import UserCreate, UserUpdate, CompleteUserSchema #UserOut
from ...core.security import get_password_hash
from ...database import models
from ...crud.token import get_user_by_cpf, get_user, get_current_user
from ...core.hierarchy import require_role, RoleEnum


from ...core.security import generate_invite_token, verify_invite_token
from ...utils.send_email import send_reset_password_email
from ...core.security import verify_reset_token, generate_reset_token, verify_password

router = APIRouter()


@router.post("/completar-cadastro")
async def completar_cadastro(user_data: CompleteUserSchema, db: AsyncSession = Depends(get_db)):
    email = verify_invite_token(user_data.token)
    if not email:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    stmt = select(models.User).filter(models.User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first() 

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if user.fl_ativo:
        raise HTTPException(status_code=400, detail="Usuário já completou o cadastro")

    user.nome_usuario = user_data.nome_usuario
    user.senha_hash = get_password_hash(user_data.senha)
    user.fl_ativo = True

    await db.commit()
    await db.refresh(user)

    return {"message": "Cadastro completado com sucesso! Você já pode fazer login."}


@router.get("/dados-completar-cadastro")
async def dados_completar_cadastro(token: str, db: AsyncSession = Depends(get_db)):
    email = verify_invite_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")
    
    stmt = select(models.User).filter(models.User.email == email).options(
        selectinload(models.User.unidadeSaude)
    )
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if user.fl_ativo:
        raise HTTPException(status_code=400, detail="Usuário já completou o cadastro")

    nome_unidade_saude = None
    if user.unidadeSaude:
        nome_unidade_saude = user.unidadeSaude[0].nome_unidade_saude

    return {
        "nome_usuario": user.nome_usuario,
        "email": user.email,
        "cpf": user.cpf,
        "nome_unidade_saude": nome_unidade_saude
    }
    

@router.get("/dados-resetar-senha")
async def dados_resetar_senha(token: str):
    # recebe token email, e retorna o email do usuario
    
    email = verify_invite_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")
    
    return {"email": email}


@router.post("/esqueci-minha-senha")
async def forgot_password(email: str, 
                          background_tasks: BackgroundTasks,
                          db: AsyncSession = Depends(get_db)):
    stmt = select(models.User).filter(models.User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    reset_token = generate_reset_token(email)

    user.password_reset_token = reset_token
    user.password_reset_token_used = False

    reset_link = f"sitebonito.com/resetar-senha?token={reset_token}"
    background_tasks.add_task(send_reset_password_email, email, reset_link)

    await db.commit()
    await db.refresh(user)

    return {"message": "E-mail de redefinição de senha enviado!"}


@router.post("/resetar-senha")
async def reset_password(token: str, nova_senha: str, db: AsyncSession = Depends(get_db)):
    email = verify_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    stmt = select(models.User).filter(models.User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if user.password_reset_token_used:
        raise HTTPException(status_code=400, detail="Token já utilizado")
    
    user.password_reset_token_used = True

    user.senha_hash = get_password_hash(nova_senha)
    user.id_usuario_atualizacao = user.id
    await db.commit()
    await db.refresh(user)

    return {"message": "Senha redefinida com sucesso!"}


@router.post("/alterar-senha")
async def change_password(
    senha_atual: str,
    nova_senha: str,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not verify_password(senha_atual, current_user.senha_hash):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")

    current_user.senha_hash = get_password_hash(nova_senha)
    current_user.id_usuario_atualizacao = current_user.id
    await db.commit()
    await db.refresh(current_user)

    return {"message": "Senha alterada com sucesso!"}
