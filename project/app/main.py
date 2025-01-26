from fastapi import FastAPI
from app.api.routes import user_routes, audit_routes, group_routes, permission_routes, role_routes
from app.database import models, database
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    print("Database tables created successfully")
    yield
    print("Application is shutting down")

app = FastAPI(lifespan=lifespan)


app.include_router(user_routes.router)
app.include_router(permission_routes.router)
app.include_router(role_routes.router)
app.include_router(group_routes.router)
app.include_router(audit_routes.router)