from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from app.storage.db import list_events

templates = Jinja2Templates(directory="app/web/templates")

def create_web_app():
    app = FastAPI(title="MillaDesign Dashboard")

    @app.get("/", response_class=HTMLResponse)
    async def home(req: Request):
        events = list_events(limit=80)
        return templates.TemplateResponse("index.html", {"request": req, "events": events})

    @app.get("/p/{person}", response_class=HTMLResponse)
    async def person(req: Request, person: str):
        events = [e for e in list_events(limit=200) if (e[5] or "").lower().find(person.lower()) >= 0]
        return templates.TemplateResponse("person.html", {"request": req, "events": events, "person": person})

    return app
