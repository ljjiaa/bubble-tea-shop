import os
import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from psycopg.errors import ForeignKeyViolation
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

load_dotenv()

app = FastAPI()

# ==================== IngredientOut, IngredientIn ====================

# Shape of an ingredient sent back to the client
class IngredientOut(BaseModel):
    id: int
    name: str
    unit: str
    reorder_threshold: float

# Shape of an ingredient the client sends in (no id)
class IngredientIn(BaseModel):
    name: str
    unit: str
    reorder_threshold: float = 0
    
# ==================== RecipeOut, RecipeIn ====================

# Shape sent in — is_active excluded, client can't set it directly
class RecipeIn(BaseModel):
    name: str
    price: float

# Shape sent back — includes is_active for soft-delete status
class RecipeOut(BaseModel):
    id: int
    name: str
    price: float
    is_active: bool


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

class LoginIn(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

#---------------------- Ingredient endpoints ----------------------

# Confirms the API is up and can reach the database
@app.get("/health")
def health_check():
    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    conn.close()
    return {"status": "ok", "database": "connected"}

# List all ingredients
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

# Create a new ingredient
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

# Update an ingredient by id
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

# Delete an ingredient — blocked (409) if it's used in a recipe
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
    
#---------------------- Recipe endpoints ----------------------

# List active recipes only (soft-deleted ones excluded)
@app.get("/recipes", response_model=list[RecipeOut])
def list_recipes():
    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, price, is_active FROM recipes WHERE is_active = true ORDER BY id")
        rows = cur.fetchall()
    conn.close()
    return [
        {"id": r[0], "name": r[1], "price": float(r[2]), "is_active": r[3]}
        for r in rows
    ]

# Create a new recipe (is_active defaults to true)
@app.post("/recipes", response_model=RecipeOut, status_code=201)
def create_recipe(recipe: RecipeIn):
    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO recipes (name, price) VALUES (%s, %s) RETURNING id, name, price, is_active",
            (recipe.name, recipe.price),
        )
        row = cur.fetchone()
    conn.commit()
    conn.close()
    return {"id": row[0], "name": row[1], "price": float(row[2]), "is_active": row[3]}

# Update a recipe — only if it's still active
@app.put("/recipes/{recipe_id}", response_model=RecipeOut)
def update_recipe(recipe_id: int, recipe: RecipeIn):
    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE recipes SET name = %s, price = %s WHERE id = %s AND is_active = true RETURNING id, name, price, is_active",
            (recipe.name, recipe.price, recipe_id),
        )
        row = cur.fetchone()
    conn.commit()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"id": row[0], "name": row[1], "price": float(row[2]), "is_active": row[3]}

# Soft delete — sets is_active = false, row itself is kept
@app.delete("/recipes/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: int):
    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE recipes SET is_active = false WHERE id = %s AND is_active = true",
            (recipe_id,),
        )
        deleted = cur.rowcount
    conn.commit()
    conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Recipe not found")
    

#---------------------- Auth ----------------------

@app.post("/auth/login", response_model=TokenOut)
def login(credentials: LoginIn):
    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    with conn.cursor() as cur:
        cur.execute("SELECT id, password_hash, role FROM app_users WHERE username = %s", (credentials.username,))
        row = cur.fetchone()
    conn.close()

    if row is None or not pwd_context.verify(credentials.password, row[1]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = jwt.encode(
        {"sub": credentials.username, "role": row[2], "exp": datetime.utcnow() + timedelta(hours=8)},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return {"access_token": token}