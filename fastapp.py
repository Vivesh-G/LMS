from core.config import app, templates

# Include routes
from api.routes import router as main_router
app.include_router(main_router)

# Register error handlers
from error_handlers import http_exception_handler, internal_server_error
from starlette.exceptions import HTTPException as StarletteHTTPException

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(500, internal_server_error)

import uvicorn

if __name__=='__main__':
    uvicorn.run("fastapp:app", host="127.0.0.1", port=8000, reload=True)