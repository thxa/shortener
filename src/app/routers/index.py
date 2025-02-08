from fastapi import APIRouter, Depends, Request
from ..dependencies import rate_limit
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["index"])

templates = Jinja2Templates(directory="/src/app/templates")

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # return {"message": "Welcome to URL Shortener Service"}
    return templates.TemplateResponse(
        request=request, name="index.html", context={}
    )
