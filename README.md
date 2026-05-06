# skin_analysis_Agents

이 프로젝트는 피부 종양 및 병변 데이터를 분석하고, 사용자 데이터와 화장품 성분 정보를 결합하여 맞춤형 처치법, 시계열 변화, 성분 검증 레포트를 생성하는 백엔드 멀티 에이전트 파이프라인입니다. 추후 AWS 등 클라우드 인프라로의 이식을 고려하여 의존성을 분리한 아키텍처로 설계되었습니다.

## 목표

*   사용자 피부 상태와 병변 예측 데이터를 결합한 개인화 처치 가이드 생성
*   과거 병변 기록 크기와의 비교를 통한 시계열 변화 및 징후 추적
*   RAG 기반 화장품 성분 논문/DB 검색을 통한 피부 적합성 검증
*   인터페이스 분리 원칙을 통한 높은 유지보수성 및 클라우드(AWS) 마이그레이션 용이성 확보

## 시스템 아키텍처 및 에이전트 구성

*   **Agent A (Treatment):** 사용자의 피부 타입, 예민함 여부와 모델의 추정 병변 정보(확률 포함)를 바탕으로 전문가적이고 공감하는 어조의 개인화 처치법을 3줄 이내로 작성합니다[cite: 5].
*   **Agent B (Time Series):** 데이터베이스에서 과거 병변 데이터를 불러와 현재 병변의 크기(`size_value`)와 비교 분석하여 객관적인 변화 양상을 보고합니다[cite: 5, 8]. (과거 데이터가 없을 경우 시계열 분석은 생략됩니다[cite: 5].)
*   **Agent C (Cosmetic):** RAG 검색 인터페이스를 통해 화장품 성분별 효능 논문 데이터를 찾아내고, 이를 기반으로 해당 화장품이 사용자 피부 병변에 미칠 영향을 검증하여 추천 여부를 판별합니다[cite: 5].

## 파일 역할

*   `schemas.py`: 에이전트 간 통신에 사용되는 데이터 구조(`UserData`, `LesionData`, `Cosmetic`)를 Pydantic 객체로 정의하는 파일[cite: 8].
*   `interfaces.py`: 외부 인프라(LLM 호출, DB 접근, 문서 검색)와의 결합도를 낮추기 위한 추상 클래스(`ABC`) 인터페이스 정의 파일[cite: 6].
*   `agents.py`: Agent A, B, C의 핵심 프롬프트 생성 로직과 비즈니스 로직이 구현된 파일[cite: 5].
*   `main.py`: 임시 모의(Mock) 클래스를 구현 및 주입하고, 최종적으로 FastAPI 애플리케이션을 초기화하여 API 엔드포인트를 노출하는 실행 진입 파일[cite: 7].

## 데이터 스키마 명세

**1. UserData**[cite: 8]
*   `user_id`: 사용자 고유 식별자
*   `skin_type`: 피부 타입 (지성, 건성, 복합성)
*   `is_sensitive`: 예민성 여부 (Boolean)

**2. LesionData**[cite: 8]
*   `lesion_id`: 병변 고유 식별자
*   `user_id`: 소유자 식별자
*   `predicted_disease`: 비전 모델에 의한 추정 질환명
*   `probability`: 질환 예측 확률값
*   `size_value`: 크기 등 시계열 비교 분석에 사용될 수치 데이터
*   `timestamp`: 분석 요청/기록 시간

**3. Cosmetic**[cite: 8]
*   `name`: 화장품명
*   `ingredients`: 포함된 화학 성분 리스트 (`List[str]`)

## API 실행 예시

FastAPI 서버가 실행된 후, `/analyze-lesion` 엔드포인트로 JSON 페이로드를 전송하여 종합 분석 리포트를 요청할 수 있습니다[cite: 7].

**요청(Request) 예시:**
```json
POST /analyze-lesion
{
  "user": {
    "user_id": "user_123",
    "skin_type": "지성",
    "is_sensitive": true
  },
  "lesion": {
    "lesion_id": "lesion_456",
    "user_id": "user_123",
    "predicted_disease": "피지선 결석",
    "probability": 76.0,
    "description": "우측 턱선 부위",
    "size_value": 12.5,
    "timestamp": "2026-05-06"
  },
  "cosmetic": {
    "name": "진정 토너",
    "ingredients": ["성분a", "성분b"]
  }
}
```

**추론 출력 형식 (Response):**
각 에이전트의 분석 결과를 하나로 조합한 최종 텍스트 리포트가 반환됩니다[cite: 7].
```json
{
  "status": "success",
  "report": "\n    [병변 레포트]\n    1/2. 모델 자체 출력 (생략)\n    3. [LLM 출력 결과물] 프롬프트를 바탕으로 생성된 텍스트입니다.\n    4/5. [LLM 출력 결과물] 프롬프트를 바탕으로 생성된 텍스트입니다.\n    6. [LLM 출력 결과물] 프롬프트를 바탕으로 생성된 텍스트입니다.\n    7. 본 서비스가 출력하는 레포트는 모두 사용자 입력과 AI 분석에 의한 추천일 뿐, 법적인 책임을 지지 않습니다.\n    "
}
```

## 모델과 백엔드 역할 분리

*   **비전 예측 모델 (외부):** 입력된 피부 이미지를 바탕으로 질환 분류 결과, 확률, 객관적인 징후 수치를 반환합니다[cite: 8].
*   **멀티 에이전트 (본 백엔드):** 비전 모델의 결과를 수신하여 개인의 피부 특성, 과거 데이터, 사용 중인 화장품 논문 데이터와 융합한 자연어 레포트를 도출합니다[cite: 5, 7, 8].
*   **법적 고지 강제:** 백엔드 레이어에서 리포트를 반환할 때, 의료적 법적 책임을 지지 않는다는 면책 조항 텍스트를 무조건 포함하도록 정책적으로 강제하고 있습니다[cite: 7].

## 인프라 마이그레이션 (AWS 등)

현재 코드는 `main.py`에 작성된 `LocalMockLLM`, `LocalMockDB`, `LocalMockSearch`와 같은 로컬 모의(Mock) 클래스에 의해 동작합니다[cite: 7]. 
차후 실제 서비스 배포 시, `agents.py`의 핵심 비즈니스 로직 수정 없이 `main.py`의 구현체만 AWS SDK(Boto3)를 활용한 Bedrock, DynamoDB, OpenSearch 연동 클래스로 교체하여 매핑하면 원활한 마이그레이션이 가능합니다[cite: 7].
