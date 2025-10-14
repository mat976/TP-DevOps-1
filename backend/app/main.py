import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app:app@db:5432/appdb")

app = FastAPI(title="Backend FastAPI", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
              sku TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              stock INTEGER NOT NULL,
              threshold INTEGER NOT NULL
            );
            """
        )
        cur.execute("SELECT COUNT(*) FROM items;")
        count = cur.fetchone()[0]
        if count == 0:
            cur.executemany(
                "INSERT INTO items (sku, name, stock, threshold) VALUES (%s, %s, %s, %s)",
                [
                    ("ALIM-PA-001", "Pâtes Spaghetti 500g", 36, 20),
                    ("ALIM-SC-014", "Sauce Tomate 250g", 12, 15),
                    ("ALIM-HU-077", "Huile d’Olive 1L", 0, 10),
                ],
            )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("DB init error:", e)


@app.on_event("startup")
def on_startup():
    init_db()


class Item(BaseModel):
    sku: str
    name: str
    stock: int
    threshold: int


class StockUpdate(BaseModel):
    stock: int


class StockAdjust(BaseModel):
    delta: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-check")
def db_check():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        cur.close()
        conn.close()
        return {"database": "ok"}
    except Exception as e:
        return {"database": "error", "detail": str(e)}

@app.get("/articles", response_model=List[Item])
def articles():
    try:
        return list_items()  # tente la DB
    except Exception:
        return []  # fallback 200 même si DB down


@app.get("/items", response_model=List[Item])
def list_items():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT sku, name, stock, threshold FROM items ORDER BY name;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {"sku": r[0], "name": r[1], "stock": r[2], "threshold": r[3]} for r in rows
    ]


@app.patch("/items/{sku}/stock", response_model=Item)
def update_stock(sku: str, payload: StockUpdate):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT sku, name, stock, threshold FROM items WHERE sku=%s;", (sku,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close()
        raise HTTPException(status_code=404, detail="Item not found")
    cur.execute("UPDATE items SET stock=%s WHERE sku=%s;", (payload.stock, sku))
    conn.commit()
    cur.execute("SELECT sku, name, stock, threshold FROM items WHERE sku=%s;", (sku,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return {"sku": row[0], "name": row[1], "stock": row[2], "threshold": row[3]}


@app.post("/items/{sku}/adjust", response_model=Item)
def adjust_stock(sku: str, payload: StockAdjust):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT stock FROM items WHERE sku=%s;", (sku,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close()
        raise HTTPException(status_code=404, detail="Item not found")
    new_stock = max(0, row[0] + payload.delta)
    cur.execute("UPDATE items SET stock=%s WHERE sku=%s;", (new_stock, sku))
    conn.commit()
    cur.execute("SELECT sku, name, stock, threshold FROM items WHERE sku=%s;", (sku,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return {"sku": row[0], "name": row[1], "stock": row[2], "threshold": row[3]}