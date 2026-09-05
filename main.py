import os
import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from psycopg.errors import ForeignKeyViolation

load_dotenv()

app = FastAPI()

class IngredientOut(BaseModel):
    id: int
    name: str
    unit: str
    reorder_threshold: float

class IngredientIn(BaseModel):
    name: str
    unit: str
    reorder_threshold: float = 0


@app.get("/health")
def health_check():
    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    conn.close()
    return {"status": "ok", "database": "connected"}

@app.get("/ingredients", response_model=list[IngredientOut])
def list_ingredients():
    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, unit, reorder_threshold FROM ingredients ORDER BY id")
        rows = cur.fetchall()
    conn.close()
    return [
        {"id": r[0], "name": r[1], "unit": r[2], "reorder_threshold": float(r[3])}
        for r in rows
    ]

@app.post("/ingredients", response_model=IngredientOut, status_code=201)
def create_ingredient(ingredient: IngredientIn):
    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO ingredients (name, unit, reorder_threshold) VALUES (%s, %s, %s) RETURNING id, name, unit, reorder_threshold",
            (ingredient.name, ingredient.unit, ingredient.reorder_threshold),
        )
        row = cur.fetchone()
    conn.commit()
    conn.close()
    return {"id": row[0], "name": row[1], "unit": row[2], "reorder_threshold": float(row[3])}

@app.put("/ingredients/{ingredient_id}", response_model=IngredientOut)
def update_ingredient(ingredient_id: int, ingredient: IngredientIn):
    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE ingredients SET name = %s, unit = %s, reorder_threshold = %s WHERE id = %s RETURNING id, name, unit, reorder_threshold",
            (ingredient.name, ingredient.unit, ingredient.reorder_threshold, ingredient_id),
        )
        row = cur.fetchone()
    conn.commit()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return {"id": row[0], "name": row[1], "unit": row[2], "reorder_threshold": float(row[3])}

from psycopg.errors import ForeignKeyViolation

@app.delete("/ingredients/{ingredient_id}", status_code=204)
def delete_ingredient(ingredient_id: int):
    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    with conn.cursor() as cur:
        try:
            cur.execute("DELETE FROM ingredients WHERE id = %s", (ingredient_id,))
        except ForeignKeyViolation:
            conn.rollback()
            conn.close()
            raise HTTPException(status_code=409, detail="Cannot delete: ingredient is used in a recipe")
        deleted = cur.rowcount
    conn.commit()
    conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Ingredient not found")