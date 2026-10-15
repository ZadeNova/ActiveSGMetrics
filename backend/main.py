import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum
from routers import data, health
from config import settings

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]
)
log = structlog.get_logger()

#fastapi dev main.py

app = FastAPI()


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    log.error(
        "unhandled_exception",
        path=request.url.path,
        error=str(exc),
        exc_info=exc,
    )
    response = JSONResponse(
        status_code=500, content={"detail": "Internal server error"}
    )
    # ServerErrorMiddleware (which runs this handler) sits outside
    # CORSMiddleware regardless of registration order, so CORS headers
    # never reach a response from here unless added manually.
    origin = request.headers.get("origin")
    if origin in settings.ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,   # Change this to production URL
    allow_credentials=True,
    allow_methods=["*"], # Allow all request methods
    allow_headers=["*"],  # Allow all headers
)



app.include_router(data.router, prefix="/api/v1", tags=["Data"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])

# Lambda entry point (Function URL -> Mangum -> this ASGI app). Unused
# locally; uvicorn/fastapi-dev import `app` directly instead.
handler = Mangum(app)