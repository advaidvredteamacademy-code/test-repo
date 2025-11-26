from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import List
from fastapi import File, UploadFile
from fastapi import HTTPException
from services import load_documents
from agents import classify_documents
import traceback
logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Starting up...")
    yield
    # Shutdown actions
    logger.info("Shutting down...")

app = FastAPI(
    title = "SUPERCLAIMS API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}
    

@app.post("/generate-claim")
async def generate_claim(files: List[UploadFile] = File(...,description="The files to generate a claim from")):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    try:
        if not files:
            raise HTTPException(status_code=400, detail="Failed to load any documents")

        # Load documents
        files = await load_documents(files)

        logger.info(f"Successfully loaded {len(files)} documents")

        # Classify documents
        classification_results = classify_documents(files)

        #

        # logger.info(f"Classification results: {classification_results}")
        return classification_results
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error processing files: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)