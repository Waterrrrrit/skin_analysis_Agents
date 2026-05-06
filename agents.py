from schemas import UserData, LesionData, Cosmetic
from interfaces import LLMService, DatabaseService, KnowledgeSearchService

class AgentA_Treatment:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    async def generate_report(self, user: UserData, lesion: LesionData) -> str:
        prompt = f"""
        사용자 정보: 피부타입 {user.skin_type}, 예민함 여부 {user.is_sensitive}
        병변 정보: {lesion.predicted_disease} (확률 {lesion.probability}%)
        위 정보를 바탕으로 알맞은 개인화 처치법을 전문가적로서 3줄 이내로 작성.
        """
        return await self.llm.generate_text(prompt)
    
class AgentB_TimeSeries:
    def __init__(self, llm_service: LLMService, db_service: DatabaseService):
        self.llm = llm_service
        self.db = db_service

    def analyze_changes(self, current_lesion: LesionData) -> str:
        past_lesion = self.db.get_past_lesion(current_lesion.user_id, current_lesion.lesion_id)
        
        if not past_lesion:
            return "과거 데이터가 없어 시계열 분석을 생략합니다."
            
        prompt = f"""
        과거 병변 크기: {past_lesion.size_value}
        현재 병변 크기: {current_lesion.size_value}
        위 두 데이터를 비교하여 변화 양상 및 징후를 객관적으로 보고.
        """
        return self.llm.generate_text(prompt)

class AgentC_Cosmetic:
    def __init__(self, llm_service: LLMService, search_service: KnowledgeSearchService):
        self.llm = llm_service
        self.search = search_service

    def analyze_cosmetic(self, user: UserData, cosmetic: Cosmetic) -> str:
        # 1. 성분 효과 검색 (RAG)
        effects = []
        for ingredient in cosmetic.ingredients:
            effect_info = self.search.search_ingredient_effect(ingredient)
            effects.append(f"{ingredient}: {effect_info}")
            
        effects_str = "\n".join(effects)
        
        # 2. LLM을 통한 최종 분석
        prompt = f"""
        사용자 피부: {user.skin_type}, 예민함 {user.is_sensitive}
        화장품 성분별 효능 논문 데이터: {effects_str}
        위 논문 데이터를 기반으로, 이 화장품이 사용자 피부 병변에 미칠 영향을 검증하고 추천 여부를 작성해.
        """
        return self.llm.generate_text(prompt)
