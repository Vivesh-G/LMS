from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

templates = Jinja2Templates(directory="templates")

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("errors/404.html", {
            "request": request,
            "message": str(exc.detail)
        }, status_code=exc.status_code)

async def internal_server_error(request: Request, exc: Exception):
    return templates.TemplateResponse("errors/500.html", {
        "request": request,
        "message": "An unexpected error occurred. Please try again later."
    }, status_code=500)
