from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
from PIL import Image
import io
import os
import logging
import traceback
from dotenv import load_dotenv
from ai import extract_menu_items, generate_next_question, recommend_dishes


# CONFIGURE LOGGING
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)-5s| %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("menu_analyzer")

# Load environment variables
load_dotenv()

app = FastAPI()

# Optional CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QAHistory(BaseModel):
    qa: List[str]


class Dish(BaseModel):
    name: str
    description: str
    price: str = ""


class RecommendRequest(BaseModel):
    dishes: List[Dish]
    qa: List[str]
    language: str


@app.post("/extract_menu")
async def extract_menu(files: List[UploadFile] = File(...)):
    try:
        if len(files) == 0:
            raise HTTPException(status_code=400, detail="No files provided")

        logger.info(f"Processing {len(files)} images for menu extraction")
        images = []
        for file in files:
            img_data = await file.read()
            image = Image.open(io.BytesIO(img_data)).convert("RGB")
            images.append(image)

        dishes = extract_menu_items(images)
        logger.info(f"Successfully extracted {len(dishes)} menu items")
        return {"dishes": dishes}
    except Exception as e:
        logger.error(f"Error extracting menu: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error extracting menu: {str(e)}")


@app.post("/next_question")
def next_question(payload: RecommendRequest):
    try:
        logger.info(
            f"Generating next question in {payload.language} for {len(payload.dishes)} dishes"
        )
        # Convert Pydantic models to dictionaries
        dishes_dict = [dish.dict() for dish in payload.dishes]
        question = generate_next_question(dishes_dict, payload.qa, payload.language)
        logger.info(f"Generated question: {question[:50]}...")
        return {"question": question}
    except Exception as e:
        logger.error(f"Error generating question: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"Error generating question: {str(e)}"
        )


@app.post("/recommend")
def recommend(payload: RecommendRequest):
    try:
        logger.info(
            f"Generating recommendations in {payload.language} for {len(payload.dishes)} dishes"
        )
        # Convert Pydantic models to dictionaries
        dishes_dict = [dish.dict() for dish in payload.dishes]
        recommendation = recommend_dishes(dishes_dict, payload.qa, payload.language)
        logger.info("Successfully generated recommendations")
        return {"recommendations": recommendation}
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"Error generating recommendations: {str(e)}"
        )


# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok", "model": os.getenv("OPENAI_API_MODEL", "default model")}
