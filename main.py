import os
import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

app = FastAPI()

@app.get("/health")
def health_check():
    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    conn.close()
    return {"status": "ok", "database": "connected"}