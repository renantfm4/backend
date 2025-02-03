# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from typing import Dict
# from datetime import datetime
# from ...crud.audit_log import create_audit_log
# from ...database.database import get_db

# router = APIRouter()

# @router.post("/audit/", response_model=dict)
# async def create_audit_log_route(
#     user_id: int,
#     change_type: str,
#     change_details: Dict,
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Rota para criar um novo log de auditoria.
#     """
#     try:
#         return await create_audit_log(user_id, change_type, change_details, db)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
