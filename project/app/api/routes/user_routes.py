from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
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

    if user.is_active:
        raise HTTPException(status_code=400, detail="Usuário já completou o cadastro")

    user.nome_usuario = user_data.nome_usuario
    user.senha_hash = get_password_hash(user_data.senha)
    user.is_active = True

    await db.commit()
    await db.refresh(user)

    return {"message": "Cadastro completado com sucesso! Você já pode fazer login."}

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

    reset_link = f"sitebonito.com/resetar-senha?token={reset_token}"
    background_tasks.add_task(send_reset_password_email, email, reset_link)

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




# @router.post("/users/", response_model=UserOut)
# def create_user(user: UserCreate, 
#                 db: AsyncSession = Depends(get_db),
#                 current_user: models.User = Depends(get_current_user)
# ):
#     db_user = get_user_by_cpf(db, cpf=user.cpf)
#     if db_user:
#         raise HTTPException(status_code=400, detail="CPF já cadastrado")
#     hashed_password = get_password_hash(user.senha)
#     new_user = models.User(
#         nome_usuario=user.nome_usuario,
#         cpf=user.cpf,
#         email=user.email,
#         senha_hash=hashed_password,
#         id_usuario_criacao = current_user.id
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user


# @router.get("/users/", response_model=List[UserOut])
# async def read_users(
#     skip: int = 0, 
#     limit: int = 100, 
#     db: AsyncSession = Depends(get_db), 
#     current_user: models.User = Depends(get_current_user)
# ):
#     result = await db.execute(select(models.User).offset(skip).limit(limit))
#     users = result.scalars().all()
#     return users

# @router.get("/users/{cpf}", response_model=UserOut)
# async def read_user(
#     cpf: str, 
#     db: AsyncSession = Depends(get_db), 
#     current_user: models.User = Depends(get_current_user)
# ):
#     result = await db.execute(select(models.User).filter(models.User.cpf == cpf))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(status_code=404, detail="Usuário não encontrado")
#     return user

# @router.put("/users/{cpf}", response_model=UserOut)
# async def update_user(
#     cpf: str, 
#     user_update: UserUpdate, 
#     db: AsyncSession = Depends(get_db), 
#     # current_user: models.User = Depends(get_current_user)
#     current_user: models.User = Depends(require_role(RoleEnum.SUPERVISOR))
# ):
#     user = await get_user_by_cpf(db, cpf)
#     if not user:
#         raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
#     if user_update.nome_usuario is not None:
#         user.nome_usuario = user_update.nome_usuario
#     if user_update.cpf is not None:
#         user.cpf = user_update.cpf
#     if user_update.email is not None:
#         user.email = user_update.email
#     if user_update.senha is not None:
#         user.senha_hash = get_password_hash(user_update.senha)

#     user.id_usuario_atualizacao = current_user.id

#     await db.commit()
#     await db.refresh(user)
#     return user


# @router.post("/users/")
# async def create_user_route(user: UserCreate, db: AsyncSession = Depends(get_db)):
#     """
#     Rota para criar um novo usuário.
#     """
#     try:
#         return await create_user(db, user)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
    
# @router.post("/users/{user_id}/roles/{role_id}")
# async def assign_role_to_user_route(user_id: int, role_id: int, db: AsyncSession = Depends(get_db)):
#     """
#     Rota para atribuir uma função a um usuário.
#     """
#     try:
#         return await assign_role_to_user(db, user_id, role_id)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
    
# @router.post("/users/{user_id}/permissions/{permission_id}")
# async def assign_permission_to_user_route(user_id: int, permission_id: int, db: AsyncSession = Depends(get_db)):
#     """
#     Rota para atribuir uma permissão a um usuário.
#     """
#     try:
#         return await assign_permission_to_user(db, user_id, permission_id)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
    
# @router.post("/users/{user_id}/groups/{group_id}")
# async def assign_user_to_group_route(user_id: int, group_id: int, db: AsyncSession = Depends(get_db)):
#     """
#     Rota para atribuir um usuário a um grupo.
#     """
#     try:
#         return await assign_user_to_group(db, user_id, group_id)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
    
    
