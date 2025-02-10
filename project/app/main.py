from fastapi import FastAPI
from app.api.routes import token_routes, user_routes, admin_routes, supervisor_routes #, audit_routes, group_routes, permission_routes, role_routes
from app.database import models, database
from app.database.seed import seed_data, populate_data
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware


# from app.database.populate_db import populate_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # async with database.engine.begin() as conn:
    #     await conn.run_sync(models.Base.metadata.drop_all)
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
# app.include_router(permission_routes.router)
# app.include_router(role_routes.router)
# app.include_router(group_routes.router)
# app.include_router(audit_routes.router)
