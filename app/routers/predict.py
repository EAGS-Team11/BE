from fastapi import APIRouter
import random

router = APIRouter(tags=["predict"])

@router.post("/")
def predict_score():
    # dummy skor AI random
    score = random.randint(0, 100)
    return {"skor_ai": score}