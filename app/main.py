from fastapi import FastAPI
from config import settings
import asyncpg

app = FastAPI()

async def connect_db():
    conn = await asyncpg.connect(settings.DATABASE_URL)
    return conn

@app.get("/")
async def read_root():
    conn = await connect_db()
    result = await conn.fetch("SELECT 'Hello, FastAPI with Postgres!' AS message;")
    await conn.close()
    return {"message": result[0]["message"]}
