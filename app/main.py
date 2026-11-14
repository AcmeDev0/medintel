"""
MedIntel AI — FastAPI Application.
Serves the web UI and API endpoints for the regulatory intelligence platform.
"""

from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.config import settings, BASE_DIR
from app.api.chat import router as chat_router
from app.api.checklists import router as checklist_router
from app.api.classify import router as classify_router
from app.api.documents import router as documents_router

# --- App Initialization ---
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Regulatory Intelligence Platform for African Healthcare",
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static Files & Templates ---
static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"

static_dir.mkdir(parents=True, exist_ok=True)
(static_dir / "css").mkdir(parents=True, exist_ok=True)
(static_dir / "js").mkdir(parents=True, exist_ok=True)
(static_dir / "images").mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

# --- API Routes ---
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(checklist_router, prefix="/api", tags=["Checklists"])
app.include_router(classify_router, prefix="/api", tags=["Classification"])
app.include_router(documents_router, prefix="/api", tags=["Documents"])


# --- Page Routes ---
@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Serve the landing page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Serve the chat interface."""
    return templates.TemplateResponse("chat.html", {"request": request})


@app.get("/checklists", response_class=HTMLResponse)
async def checklists_page(request: Request):
    """Serve the compliance checklists page."""
    return templates.TemplateResponse("checklists.html", {"request": request})


@app.get("/classify", response_class=HTMLResponse)
async def classify_page(request: Request):
    """Serve the device classification helper page."""
    return templates.TemplateResponse("classify.html", {"request": request})


@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    """Serve the about page."""
    return templates.TemplateResponse("about.html", {"request": request})


# --- Health Check ---
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}
