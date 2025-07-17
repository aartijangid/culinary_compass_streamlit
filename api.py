from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict
import pandas as pd
import os
from utils.food_recommend import recommend_food
import json
from threading import Lock

app = FastAPI()
lock = Lock()

HISTORY_FILE = "data/user_log/food.xlsx"
SHEET_NAME = 'User History'

class RecommendationRequest(BaseModel):
    food_preference: str
    deficiencies: list

class UserHistory(BaseModel):
    name: str = Field(..., min_length=1)
    age: int = Field(..., gt=0, lt=150)
    gender: str = Field(..., min_length=1)
    height: float = Field(..., gt=0)
    weight: float = Field(..., gt=0)
    bmi: float = Field(..., gt=0)
    bmi_category: str = Field(..., min_length=1)
    food_preference: str = Field(..., min_length=1)
    deficiencies: List[str] = Field(default_factory=list)
    recommendations: str = Field(..., min_length=1)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        # Add schema validation
        validate_assignment = True
        # Allow extra fields
        extra = "ignore"

@app.get("/get-recommendation/")
async def get_recommendation(data: RecommendationRequest):
    """Get food recommendations based on preferences and deficiencies."""
    try:
        recommendation = recommend_food(
            data.deficiencies if data.deficiencies else 'none', 
            category=data.food_preference
        )
        return {"recommendation": recommendation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-history/")
async def save_history(user_history: UserHistory):

    try:
        history_dict = user_history.model_dump()

        # Ensure directory exists
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)

        # Convert dictionary to DataFrame
        new_data = pd.DataFrame([history_dict])

        with lock:  # Ensure thread safety
            if not os.path.exists(HISTORY_FILE):
                new_data.to_excel(HISTORY_FILE, index=False)  # Write with headers
            else:
                with pd.ExcelWriter(HISTORY_FILE, mode='a', if_sheet_exists='overlay', engine="openpyxl") as writer:
                    sheet = writer.sheets[SHEET_NAME]
                    new_data.to_excel(writer, index=False, header=False, startrow=sheet.max_row)

        return {"message": "History saved successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save history: {str(e)}")

@app.get("/get-history/")
async def get_history():
    """Retrieve all history records."""
    try:
        if os.path.exists(HISTORY_FILE):
            return {"history": pd.read_excel(HISTORY_FILE).to_dict(orient='records')}
        return {"history": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))