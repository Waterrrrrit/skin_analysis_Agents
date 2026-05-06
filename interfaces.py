from abc import ABC, abstractmethod
from typing import Optional
from schemas import UserData, LesionData, Cosmetic

# 1. LLM 호출을 위한 인터페이스
class LLMService(ABC):
    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        pass

# 2. 데이터베이스 접근을 위한 인터페이스
class DatabaseService(ABC):
    @abstractmethod
    def get_past_lesion(self, user_id: str, lesion_id: str) -> Optional[LesionData]:
        pass

# 3. RAG (문서 검색) 인터페이스 (에이전트 C용)
class KnowledgeSearchService(ABC):
    @abstractmethod
    def search_ingredient_effect(self, ingredient: str) -> str:
        pass
