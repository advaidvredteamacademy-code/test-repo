from fastapi import APIRouter

router = APIRouter()

@router.get("/", summary="Health check")
async def health_check():
    return {"message": "Hello, World!", "status": "healthy"}

