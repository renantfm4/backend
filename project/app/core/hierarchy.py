from enum import IntEnum
from fastapi import Depends, HTTPException, status
from ..database import models
from ..crud.token import get_current_user

class RoleEnum(IntEnum):
    PESQUISADOR = 1
    SUPERVISOR = 2
    ADMIN = 3

def require_role(min_role: RoleEnum):
    async def role_checker(current_user: models.User = Depends(get_current_user)):
        if not current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário não possui nenhuma role definida."
            )
        user_max_level = max(role.nivel_acesso for role in current_user.roles)
        
        if user_max_level < min_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário não tem permissão para acessar esse recurso."
            )
        return current_user
    return role_checker


# user_max_level = max(role.nivel_acesso for role in current_user.roles)
# if role.nivel_acesso > user_max_level:
#     raise HTTPException(status_code=400, detail="Você não pode atribuir roles com nível de acesso maior que o seu.")