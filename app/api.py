import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, HTTPException
from . import db, rag
from .schemas import MaterialCreate, SearchRequest


def authorize(token):
    if not os.getenv("RAG_API_TOKEN") or token != os.getenv("RAG_API_TOKEN"):
        raise HTTPException(status_code=401, detail="Недействительный токен доступа")


@asynccontextmanager
async def lifespan(app):
    db.init()
    yield


app = FastAPI(title="Project RAG API", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"success": True, "answer": "ok"}


@app.post("/materials", status_code=201)
async def add_material(
    material: MaterialCreate, x_api_token: str | None = Header(default=None)
):
    authorize(x_api_token)
    data = material.model_dump()
    return {"success": True, "material": {"id": db.add(**data), **data}}


@app.get("/materials")
async def materials(
    slot: str | None = None, x_api_token: str | None = Header(default=None)
):
    authorize(x_api_token)
    return {"success": True, "materials": db.list_materials(slot)}


@app.delete("/materials/{material_id}")
async def remove_material(
    material_id: int, x_api_token: str | None = Header(default=None)
):
    authorize(x_api_token)
    if db.delete(material_id) is None:
        raise HTTPException(status_code=404, detail="Материал не найден")
    return {"success": True, "answer": "Материал удалён"}


@app.post("/rag/search")
async def search(
    request: SearchRequest, x_api_token: str | None = Header(default=None)
):
    authorize(x_api_token)
    try:
        return await rag.search(request.slot, request.params)
    except Exception:
        return {
            "success": False,
            "answer": "Не удалось обработать запрос. Проверьте Groq и Ollama.",
        }
