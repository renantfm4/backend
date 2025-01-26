from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class RoleCreate(BaseModel):
    name: str

class PermissionCreate(BaseModel):
    name: str
    details: str

class GroupCreate(BaseModel):
    name: str