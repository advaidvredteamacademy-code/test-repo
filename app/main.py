from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.api import claims, health

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(message)s')

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Direct routes - no versioning
app.include_router(health.router, tags=["health"])
app.include_router(claims.router, tags=["claims"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )

