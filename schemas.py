from pydantic import BaseModel
from typing import List, Optional

class UserData(BaseModel):
    user_id: str
    skin_type: str  # 지성, 건성, 복합성
    is_sensitive: bool

class LesionData(BaseModel):
    lesion_id: str
    user_id: str
    predicted_disease: str
    probability: float
    description: str
    size_value: float  # 크기 등 시계열 분석용 수치
    timestamp: str

class Cosmetic(BaseModel):
    name: str
    ingredients: List[str]
