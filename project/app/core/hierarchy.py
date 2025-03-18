from enum import IntEnum
from fastapi import Depends, HTTPException, status
from ..database import models
from ..crud.token import get_current_user

class RoleEnum(IntEnum):
    PESQUISADOR = 3
    SUPERVISOR = 2
    ADMIN = 1

def require_role(min_role: RoleEnum):
    async def role_checker(current_user: models.User = Depends(get_current_user)):
        if not current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário não possui nenhuma role definida."
            )
        
        user_min_level = min(role.nivel_acesso for role in current_user.roles)
        
        if user_min_level > min_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário não tem permissão para acessar esse recurso."
            )
        return current_user
    return role_checker
