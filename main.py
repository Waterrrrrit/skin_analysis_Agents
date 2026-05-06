from fastapi import FastAPI
from schemas import UserData, LesionData, Cosmetic
from interfaces import LLMService, DatabaseService, KnowledgeSearchService
from agents import AgentA_Treatment, AgentB_TimeSeries, AgentC_Cosmetic

app = FastAPI()

# --- 1. 임시/현재 구현체 (Adapter) ---
class LocalMockLLM(LLMService):
    def generate_text(self, prompt: str) -> str:
        # 현재는 Gemini API 등을 연결해둘 수 있습니다.
        return "[LLM 출력 결과물] 프롬프트를 바탕으로 생성된 텍스트입니다."

class LocalMockDB(DatabaseService):
    def get_past_lesion(self, user_id: str, lesion_id: str):
        # 현재는 Supabase 또는 로컬 메모리에서 가져옵니다.
        return LesionData(lesion_id=lesion_id, user_id=user_id, predicted_disease="표피낭종", 
                          probability=80.0, description="과거 데이터", size_value=10.0, timestamp="2026-04-01")

class LocalMockSearch(KnowledgeSearchService):
    def search_ingredient_effect(self, ingredient: str) -> str:
        return "관련 논문에 따르면 피부 자극을 유발할 수 있음."

# --- 2. 의존성 주입 및 에이전트 초기화 ---
# 추후 AWS로 이식할 때는 아래 객체들을 AWSBedrockLLM(), AWSDynamoDB() 등으로만 바꾸면 끝납니다.
current_llm = LocalMockLLM()
current_db = LocalMockDB()
current_search = LocalMockSearch()

agent_a = AgentA_Treatment(current_llm)
agent_b = AgentB_TimeSeries(current_llm, current_db)
agent_c = AgentC_Cosmetic(current_llm, current_search)

# --- 3. API 엔드포인트 ---
@app.post("/analyze-lesion")
async def analyze_lesion(user: UserData, lesion: LesionData, cosmetic: Cosmetic):
    # 각 에이전트 실행
    report_a = await agent_a.generate_report(user, lesion)
    report_b = agent_b.analyze_changes(lesion)
    report_c = agent_c.analyze_cosmetic(user, cosmetic)
    
    # 최종 레포트 조합
    final_report = f"""
    [병변 레포트]
    1/2. 모델 자체 출력 (생략)
    3. {report_a}
    4/5. {report_b}
    6. {report_c}
    7. 본 서비스가 출력하는 레포트는 모두 사용자 입력과 AI 분석에 의한 추천일 뿐, 법적인 책임을 지지 않습니다.
    """
    return {"status": "success", "report": final_report}
