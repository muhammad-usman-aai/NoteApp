from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from config.db import conn


note = APIRouter()
templates = Jinja2Templates(directory="templates")


@note.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    docs = conn.notes.notes.find({})
    newDocs = []
    for doc in docs:
        newDocs.append({
            "id": str(doc["_id"]),  # ObjectId to string for JSON serialization
            "title": doc["title"],
            "desc": doc["desc"],
            "important": doc["important"]
        })
    return templates.TemplateResponse("index.html", {"request": request, "newDocs": newDocs})


@note.post("/")
async def create_item(request: Request):
    form = await request.form()
    formDict = dict(form)
    formDict["important"] = True if formDict.get("important") == "on" else False
    conn.notes.notes.insert_one(formDict)
    return RedirectResponse("/", status_code=303)


@note.post("/delete/{id}")
async def delete_item(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid note ID format")

    result = conn.notes.notes.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return RedirectResponse("/", status_code=303)
    else:
        raise HTTPException(status_code=404, detail="Note not found")


@note.post("/update/{id}")
async def update_item(id: str, request: Request):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid note ID format")

    form = await request.form()
    update_data = {
        "title": form.get("title"),
        "desc": form.get("desc"),
        "important": form.get("important") == "on"
    }

    result = conn.notes.notes.update_one({"_id": ObjectId(id)}, {"$set": update_data})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")

    return RedirectResponse("/", status_code=303)
