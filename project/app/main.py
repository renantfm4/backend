"""
Módulo main.py
"""

from fastapi import FastAPI
from app.api.routes import (
    token_routes,
    user_routes,
    admin_routes,
    supervisor_routes,
    unidade_saude_routes,
    atendimento_routes,
    redirect_routes,
)
from app.database import models, database
from app.database.seed import seed_data, populate_data
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware


# from app.database.populate_db import populate_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de contexto para o ciclo de vida da aplicação
        args:
            app (FastAPI): Instância da aplicação FastAPI
        yields: None
        description: Cria as tabelas do banco de dados e popula com dados iniciais
    """
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    print("Database tables created successfully")

    # await seed_data()

    await populate_data()

    print("Seed data inserted successfully")

    yield
    print("Application is shutting down")


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:8081",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(token_routes.router, tags=["token"])
app.include_router(user_routes.router, tags=["user"])
app.include_router(admin_routes.router, tags=["admin"])
app.include_router(supervisor_routes.router, tags=["supervisor"])
app.include_router(unidade_saude_routes.router, tags=["unidade_saude"])
app.include_router(atendimento_routes.router, tags=["atendimento"])
app.include_router(redirect_routes.router, tags=["redirect"])
