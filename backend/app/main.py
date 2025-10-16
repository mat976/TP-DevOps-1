import os
from typing import List
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app:app@db:5432/appdb")

app = FastAPI(title="Backend FastAPI", version="0.2.0")

STATIC_DIR = os.getenv("STATIC_DIR", "/app/static")
STATIC_INDEX = os.path.join(STATIC_DIR, "index.html")

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
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("DB init error:", e)


@app.on_event("startup")
def on_startup():
    init_db()

# Store mémoire pour fonctionnement simple sans DB
MEM_ITEMS: dict[str, dict] = {}


class Item(BaseModel):
    sku: str
    name: str
    stock: int
    threshold: int


class ItemCreate(BaseModel):
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


@app.get("/")
def root():
    # Sert l'UI si présente dans l'image; sinon JSON de diagnostic
    try:
        if os.path.exists(STATIC_INDEX):
            return FileResponse(STATIC_INDEX)
    except Exception:
        pass
    return {
        "service": "fastapi-backend",
        "message": "Backend OK",
        "docs": "/docs",
        "items": "/items",
        "health": "/health"
    }


@app.get("/config.js")
def config_js(request: Request):
    base = str(request.base_url).rstrip("/")
    backend_url = os.getenv("BACKEND_URL", base)
    content = f"window.__BACKEND_URL__ = '{backend_url}';"
    return PlainTextResponse(content, media_type="application/javascript")


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
    # Fallback mémoire si DB indisponible
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT sku, name, stock, threshold FROM items ORDER BY name;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [
            {"sku": r[0], "name": r[1], "stock": r[2], "threshold": r[3]} for r in rows
        ]
    except Exception:
        # utilise le store mémoire
        return [
            {"sku": s, "name": i["name"], "stock": i["stock"], "threshold": i["threshold"]}
            for s, i in MEM_ITEMS.items()
        ]


@app.post("/items", response_model=Item, status_code=201)
def create_item(payload: ItemCreate):
    # validations simples
    # (on vérifie avant de toucher à la DB)
    if not payload.sku or not payload.sku.strip():
        raise HTTPException(status_code=400, detail="SKU is required")
    if not payload.name or not payload.name.strip():
        raise HTTPException(status_code=400, detail="Name is required")
    if payload.stock is None or payload.stock < 0:
        raise HTTPException(status_code=400, detail="Stock must be >= 0")
    if payload.threshold is None or payload.threshold < 0:
        raise HTTPException(status_code=400, detail="Threshold must be >= 0")
    # Tentative DB, sinon fallback mémoire
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
    except Exception:
        # mémoire
        if payload.sku in MEM_ITEMS:
            raise HTTPException(status_code=409, detail="Item already exists")
        MEM_ITEMS[payload.sku] = {
            "name": payload.name,
            "stock": payload.stock,
            "threshold": payload.threshold,
        }
        return {"sku": payload.sku, "name": payload.name, "stock": payload.stock, "threshold": payload.threshold}
    # validations simples
    cur.execute("SELECT 1 FROM items WHERE sku=%s;", (payload.sku,))
    exists = cur.fetchone()
    if exists:
        cur.close(); conn.close()
        raise HTTPException(status_code=409, detail="Item already exists")
    cur.execute(
        "INSERT INTO items (sku, name, stock, threshold) VALUES (%s, %s, %s, %s)",
        (payload.sku, payload.name, payload.stock, payload.threshold),
    )
    conn.commit()
    cur.execute("SELECT sku, name, stock, threshold FROM items WHERE sku=%s;", (payload.sku,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return {"sku": row[0], "name": row[1], "stock": row[2], "threshold": row[3]}


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


class ItemUpdate(BaseModel):
    name: str | None = None
    stock: int | None = None
    threshold: int | None = None


@app.patch("/items/{sku}", response_model=Item)
def update_item(sku: str, payload: ItemUpdate):
    # Tentative DB
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT sku, name, stock, threshold FROM items WHERE sku=%s;", (sku,))
        row = cur.fetchone()
        if not row:
            cur.close(); conn.close()
            raise HTTPException(status_code=404, detail="Item not found")
        name = payload.name if payload.name is not None else row[1]
        stock = payload.stock if payload.stock is not None else row[2]
        threshold = payload.threshold if payload.threshold is not None else row[3]
        if name is None or not str(name).strip():
            cur.close(); conn.close()
            raise HTTPException(status_code=400, detail="Name is required")
        if stock is not None and stock < 0:
            cur.close(); conn.close()
            raise HTTPException(status_code=400, detail="Stock must be >= 0")
        if threshold is not None and threshold < 0:
            cur.close(); conn.close()
            raise HTTPException(status_code=400, detail="Threshold must be >= 0")
        cur.execute(
            "UPDATE items SET name=%s, stock=%s, threshold=%s WHERE sku=%s;",
            (name, stock, threshold, sku),
        )
        conn.commit()
        cur.execute("SELECT sku, name, stock, threshold FROM items WHERE sku=%s;", (sku,))
        row = cur.fetchone()
        cur.close(); conn.close()
        return {"sku": row[0], "name": row[1], "stock": row[2], "threshold": row[3]}
    except Exception:
        # Fallback mémoire
        if sku not in MEM_ITEMS:
            raise HTTPException(status_code=404, detail="Item not found")
        current = MEM_ITEMS[sku]
        name = payload.name if payload.name is not None else current["name"]
        stock = payload.stock if payload.stock is not None else current["stock"]
        threshold = payload.threshold if payload.threshold is not None else current["threshold"]
        if name is None or not str(name).strip():
            raise HTTPException(status_code=400, detail="Name is required")
        if stock is not None and stock < 0:
            raise HTTPException(status_code=400, detail="Stock must be >= 0")
        if threshold is not None and threshold < 0:
            raise HTTPException(status_code=400, detail="Threshold must be >= 0")
        MEM_ITEMS[sku] = {"name": name, "stock": stock, "threshold": threshold}
        return {"sku": sku, "name": name, "stock": stock, "threshold": threshold}


@app.delete("/items/{sku}", status_code=204)
def delete_item(sku: str):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM items WHERE sku=%s;", (sku,))
        exists = cur.fetchone()
        if not exists:
            cur.close(); conn.close()
            raise HTTPException(status_code=404, detail="Item not found")
        cur.execute("DELETE FROM items WHERE sku=%s;", (sku,))
        conn.commit()
        cur.close(); conn.close()
        return
    except Exception:
        # Fallback mémoire
        if sku not in MEM_ITEMS:
            raise HTTPException(status_code=404, detail="Item not found")
        del MEM_ITEMS[sku]
        return