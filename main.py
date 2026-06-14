from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from starlette.middleware.sessions import SessionMiddleware

from database.db import SessionLocal, engine, Base
from database.models import User, Equipment
from core.ai import industrial_ai

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="maintenance-secret"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    db = SessionLocal()

    user = db.query(User).filter_by(
        username=username,
        password=password
    ).first()

    db.close()

    if user:
        request.session["user"] = username
        return RedirectResponse("/", status_code=302)

    return RedirectResponse("/login", status_code=302)


@app.get("/")
def dashboard(request: Request):

    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=302)

    db = SessionLocal()
    equipments = db.query(Equipment).all()
    db.close()

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "equipments": equipments}
    )