# from sqlalchemy.ext.asyncio import AsyncSession
# from fastapi import HTTPException, Depends
# from typing import Dict
# from datetime import datetime
# from ..database.models import AuditLog

# async def create_audit_log(
#     user_id: int,
#     change_type: str,
#     change_details: Dict,
#     db: AsyncSession
# ) -> AuditLog:
#     try:
#         db_audit = AuditLog(
#             user_id=user_id,
#             change_type=change_type,
#             change_details=change_details,
#             timestamp=datetime.now()
#         )
#         db.add(db_audit)
#         await db.commit()
#         await db.refresh(db_audit)
#         return db_audit
#     except Exception as e:
#         await db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to create audit log: {str(e)}"
#         )