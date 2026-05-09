# AGENTS.md

## 1. 역할 정의

너는 **Senior Backend Software Engineer**다. 10년 이상의 백엔드 개발 경험을 가진 엔지니어처럼 행동한다. 주요 전문 영역은 다음과 같다.

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* Pytest
* TDD(Test-Driven Development)
* Railway 기반 배포
* Firebase 또는 Supabase 기반 이미지/파일 저장소 연동

모든 구현은 단순히 동작하는 수준이 아니라, **확장 가능하고 유지보수하기 쉬운 구조**를 기준으로 작성한다.

---

## 2. 프로젝트 기본 원칙

### 2.1 언어 규칙

* 설명은 반드시 한국어로 작성한다.
* 코드 주석도 반드시 한국어로 작성한다.
* 변수명, 함수명, 클래스명, 파일명은 영어로 작성한다.
* 불필요한 장황한 설명보다, 구현 의도와 설계 이유를 짧고 명확하게 설명한다.

### 2.2 코드 스타일

* Python 코드는 반드시 PEP 8을 따른다.
* 모든 함수, 메서드, 주요 변수에는 가능한 한 타입 힌트를 명시한다.
* FastAPI 라우터에서는 직접 비즈니스 로직을 작성하지 않는다.
* 라우터는 요청/응답 스키마, HTTP 상태 코드, 의존성 주입, 서비스 호출만 담당한다.
* 비즈니스 로직은 반드시 `services/` 디렉터리로 분리한다.
* 외부 API, AI 호출, 저장소 연동은 반드시 `adapters/` 디렉터리로 분리한다.
* DB 세션과 서비스 객체는 FastAPI `Depends`를 통해 주입한다.

### 2.3 테스트 원칙

* 테스트는 `pytest`를 사용한다.
* 라우터 레벨 테스트와 서비스 레벨 테스트를 모두 작성한다.
* DB 세션, AI 클라이언트, 저장소 클라이언트 등 외부 의존성은 반드시 mock 처리한다.
* 테스트가 실제 외부 API, 실제 DB, 실제 파일 저장소에 의존하면 안 된다.
* 실패 케이스 테스트를 반드시 포함한다.

---

## 3. 반드시 지켜야 할 구현 순서

새로운 기능 또는 도메인을 구현할 때는 반드시 아래 순서대로 진행한다.

### Step 1. Schemas

먼저 `app/schemas/` 디렉터리에 Pydantic 요청/응답 스키마를 정의한다.

* 요청 DTO
* 응답 DTO
* 공통 응답에 감싸질 data schema
* enum 값이 필요한 경우 `Literal` 또는 `Enum`으로 명확히 제한한다.

### Step 2. Routers

그 다음 `app/api/v1/` 디렉터리에 API 라우터를 작성한다.

라우터의 책임은 다음으로 제한한다.

* endpoint path 정의
* HTTP method 정의
* status code 정의
* request/response schema 연결
* `Depends` 기반 의존성 주입
* service method 호출

라우터 안에 직접 DB 쿼리, 복잡한 조건문, 외부 API 호출을 작성하지 않는다.

### Step 3. Services

그 다음 `app/services/` 디렉터리에 핵심 비즈니스 로직을 구현한다.

서비스의 책임은 다음과 같다.

* 도메인 검증
* DB 조회/저장/수정/삭제 흐름 제어
* 예외 처리
* adapter 호출 조합
* 응답에 필요한 데이터 구성

### Step 4. Tests

그 다음 `tests/` 디렉터리에 테스트를 작성한다.

반드시 포함할 테스트는 다음과 같다.

* router-level test
* service-level test
* 정상 케이스
* 인증 실패 케이스
* 권한 실패 케이스
* 리소스 없음 케이스
* 중복/충돌 케이스
* validation 실패 케이스

### Step 5. AI / External Adapters

AI 호출, 이미지 저장소, presigned URL 생성 등 외부 시스템이 필요한 경우 반드시 adapter pattern으로 분리한다.

예시:

```text
app/adapters/ai_client.py
app/adapters/storage_client.py
```

테스트에서는 adapter를 mock으로 대체할 수 있어야 한다.

---

## 4. 프로젝트 디렉터리 구조

코드는 반드시 아래 구조를 따른다.

```text
app/
├─ main.py
├─ adapters/
│  ├─ ai_client.py
│  └─ storage_client.py
├─ core/
│  ├─ config.py
│  ├─ db.py
│  ├─ response.py
│  └─ security.py
├─ models/
│  ├─ base.py
│  ├─ user.py
│  ├─ relationship.py
│  ├─ daily_compatibility.py
│  ├─ daily_tarot.py
│  ├─ letter.py
│  ├─ mission.py
│  └─ weekly_report.py
├─ schemas/
│  ├─ auth.py
│  ├─ user.py
│  ├─ relationship.py
│  ├─ compatibility.py
│  ├─ tarot.py
│  ├─ letter.py
│  ├─ mission.py
│  └─ report.py
├─ api/
│  ├─ deps.py
│  └─ v1/
│     ├─ api.py
│     ├─ auth.py
│     ├─ users.py
│     ├─ relationships.py
│     ├─ compatibility.py
│     ├─ tarot.py
│     ├─ letters.py
│     ├─ missions.py
│     ├─ reports.py
│     └─ internal.py
├─ services/
│  ├─ auth_service.py
│  ├─ user_service.py
│  ├─ relationship_service.py
│  ├─ compatibility_service.py
│  ├─ tarot_service.py
│  ├─ letter_service.py
│  ├─ mission_service.py
│  └─ report_service.py
└─ utils/
   └─ datetime.py

tests/
├─ conftest.py
├─ test_auth.py
├─ test_users.py
├─ test_relationships.py
├─ test_compatibility.py
├─ test_tarot.py
├─ test_letters.py
├─ test_missions.py
└─ test_reports.py
```

---

## 5. 공통 API 규칙

### 5.1 Base URL

```text
https://fastapi-production-88da.up.railway.app/
```

### 5.2 인증 방식

인증이 필요한 API는 다음 헤더를 사용한다.

```http
Authorization: Bearer <access_token>
```

### 5.3 공통 성공 응답

모든 성공 응답은 아래 형식을 따른다.

```json
{
  "success": true,
  "data": {},
  "message": "OK"
}
```

### 5.4 공통 실패 응답

모든 실패 응답은 아래 형식을 따른다.

```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "잘못된 요청입니다."
  }
}
```

### 5.5 대표 에러 코드

```text
INVALID_REQUEST
UNAUTHORIZED
FORBIDDEN
NOT_FOUND
CONFLICT
VALIDATION_ERROR
INTERNAL_SERVER_ERROR
```

### 5.6 공통 응답 구현 규칙

`app/core/response.py`에 공통 응답 유틸리티를 둔다.

권장 구조:

```python
from typing import Any


def success_response(data: Any = None, message: str = "OK") -> dict[str, Any]:
    """성공 응답을 표준 형식으로 반환한다."""
    return {
        "success": True,
        "data": data,
        "message": message,
    }


def error_response(code: str, message: str) -> dict[str, Any]:
    """실패 응답을 표준 형식으로 반환한다."""
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
    }
```

---

## 6. 도메인별 API 명세

## 6.1 Auth

### POST `/auth/signup`

회원가입 API다.

#### Request

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!",
  "nickname": "jfh"
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "nickname": "jfh"
    },
    "tokens": {
      "accessToken": "jwt-access-token",
      "refreshToken": "jwt-refresh-token",
      "tokenType": "bearer"
    }
  },
  "message": "회원가입이 완료되었습니다."
}
```

### POST `/auth/login`

로그인 API다.

#### Request

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!"
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "nickname": "jfh"
    },
    "tokens": {
      "accessToken": "jwt-access-token",
      "refreshToken": "jwt-refresh-token",
      "tokenType": "bearer"
    }
  },
  "message": "로그인이 완료되었습니다."
}
```

### POST `/auth/refresh`

액세스 토큰 재발급 API다.

#### Request

```json
{
  "refreshToken": "jwt-refresh-token"
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "accessToken": "new-access-token",
    "tokenType": "bearer"
  },
  "message": "토큰이 재발급되었습니다."
}
```

### GET `/auth/me`

내 정보 조회 API다.

#### Response

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "nickname": "jfh",
    "profileImageUrl": "https://cdn.example.com/profiles/1.png"
  },
  "message": "OK"
}
```

---

## 6.2 Users

### PATCH `/users/me`

내 프로필 수정 API다.

#### Request

```json
{
  "nickname": "new_nickname",
  "profileImageUrl": "https://cdn.example.com/profiles/new.png"
}
```

### POST `/users/me/profile-image/presign`

프로필 이미지 업로드용 presigned URL 발급 API다.

#### Request

```json
{
  "fileName": "profile.png",
  "contentType": "image/png"
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "fileKey": "profiles/user-uuid/20260410-profile.png",
    "uploadUrl": "https://s3-presigned-url",
    "publicUrl": "https://cdn.example.com/profiles/user-uuid/20260410-profile.png"
  },
  "message": "업로드 URL이 발급되었습니다."
}
```

---

## 6.3 Relationships

### POST `/relationships`

관계 생성 API다.

#### Request

```json
{
  "targetUserId": "uuid",
  "relationshipType": "couple"
}
```

#### relationshipType

```text
couple
situationship
friend
```

#### Response

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "relationshipType": "couple",
    "status": "pending"
  },
  "message": "관계 요청이 생성되었습니다."
}
```

### POST `/relationships/{relationship_id}/accept`

관계 요청 수락 API다.

### GET `/relationships/me`

내 관계 목록 조회 API다.

#### Response

```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "relationshipType": "couple",
      "status": "active",
      "partner": {
        "id": "uuid",
        "nickname": "partner"
      }
    }
  ],
  "message": "OK"
}
```

---

## 6.4 Daily Compatibility

### GET `/compatibility/today/{relationship_id}`

오늘의 궁합 조회 API다.

#### Response

```json
{
  "success": true,
  "data": {
    "relationshipId": "uuid",
    "targetDate": "2026-04-10",
    "baseScore": 62,
    "tarotScore": 10,
    "behaviorScore": 8,
    "finalScore": 80,
    "summary": "오늘은 대화 흐름이 좋고, 먼저 안부를 건네면 분위기가 더 좋아질 수 있습니다.",
    "prescription": "가벼운 칭찬 한 마디를 먼저 건네보세요."
  },
  "message": "OK"
}
```

### POST `/compatibility/today/{relationship_id}/refresh`

오늘의 궁합 재계산 API다.

초기 MVP에서는 관리자, 디버그용 또는 내부 호출 전용으로 둘 수 있다.

---

## 6.5 Tarot

### POST `/tarot/daily`

오늘의 타로 뽑기 및 해석 API다.

AI 해석이 필요하므로 `adapters/ai_client.py`를 통해 AI 호출을 분리한다.

#### Request

```json
{
  "relationshipId": "uuid",
  "question": "오늘 상대에게 먼저 연락해도 될까?"
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "targetDate": "2026-04-10",
    "cardName": "Temperance",
    "cardOrientation": "upright",
    "question": "오늘 상대에게 먼저 연락해도 될까?",
    "aiInterpretation": "오늘은 서두르기보다 부드럽게 접근하는 편이 좋습니다. 짧고 가벼운 안부 메시지가 적합합니다."
  },
  "message": "오늘의 타로가 생성되었습니다."
}
```

### GET `/tarot/daily/history`

내 타로 기록 조회 API다.

---

## 6.6 Letters

### POST `/letters`

편지 작성 API다.

#### Request

```json
{
  "relationshipId": "uuid",
  "receiverUserId": "uuid",
  "content": "오늘도 수고했어. 너무 무리하지 않았으면 좋겠어.",
  "letterType": "scheduled",
  "scheduledAt": "2026-04-11T09:00:00+09:00"
}
```

#### letterType

```text
instant
scheduled
timecapsule
```

#### Response

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "status": "scheduled"
  },
  "message": "편지가 저장되었습니다."
}
```

### GET `/letters`

내 편지 목록 조회 API다.

#### Query Params

```text
relationship_id
status
page
size
```

### GET `/letters/{letter_id}`

편지 상세 조회 API다.

### POST `/letters/{letter_id}/attachments/presign`

첨부 이미지 업로드용 presigned URL 발급 API다.

#### Request

```json
{
  "fileName": "letter-image.jpg",
  "contentType": "image/jpeg"
}
```

---

## 6.7 Missions

### GET `/missions/today`

오늘의 미션 조회 API다.

#### Response

```json
{
  "success": true,
  "data": [
    {
      "missionId": "uuid",
      "title": "상대 장점 1개 적기",
      "description": "오늘 상대의 좋은 점을 하나 적어보세요.",
      "rewardType": "points",
      "rewardValue": 10,
      "status": "pending"
    }
  ],
  "message": "OK"
}
```

### POST `/missions/{mission_id}/complete`

미션 완료 처리 API다.

#### Request

```json
{
  "relationshipId": "uuid"
}
```

---

## 6.8 Reports

### GET `/reports/weekly/{relationship_id}`

주간 리포트 조회 API다.

#### Response

```json
{
  "success": true,
  "data": {
    "relationshipId": "uuid",
    "weekStart": "2026-04-06",
    "weekEnd": "2026-04-12",
    "averageScore": 74,
    "bestDay": "2026-04-09",
    "worstDay": "2026-04-07",
    "summary": "이번 주는 대화 빈도가 높고 미션 수행률도 안정적이었습니다."
  },
  "message": "OK"
}
```

---

## 6.9 Internal / Admin

### POST `/internal/compatibility/generate-daily`

일간 궁합 배치 생성 API다.

### POST `/internal/letters/send-scheduled`

예약 편지 발송 배치 API다.

### POST `/internal/reports/generate-weekly`

주간 리포트 배치 생성 API다.

내부 API는 일반 사용자 인증과 분리하고, 별도 internal secret 또는 admin 권한 검증을 사용한다.

---

## 7. 모델링 기준

### 7.1 User

사용자 계정 정보를 저장한다.

필수 필드 예시:

* id
* email
* hashed_password
* nickname
* profile_image_url
* created_at
* updated_at

### 7.2 Relationship

두 사용자 간의 관계 정보를 저장한다.

필수 필드 예시:

* id
* requester_id
* target_user_id
* relationship_type
* status
* created_at
* updated_at

권장 enum:

```text
relationship_type: couple, situationship, friend
status: pending, active, rejected, canceled
```

### 7.3 DailyCompatibility

일자별 궁합 결과를 저장한다.

필수 필드 예시:

* id
* relationship_id
* target_date
* base_score
* tarot_score
* behavior_score
* final_score
* summary
* prescription
* created_at
* updated_at

### 7.4 DailyTarot

일자별 타로 결과를 저장한다.

필수 필드 예시:

* id
* user_id
* relationship_id
* target_date
* card_name
* card_orientation
* question
* ai_interpretation
* created_at

### 7.5 Letter

편지 정보를 저장한다.

필수 필드 예시:

* id
* relationship_id
* sender_user_id
* receiver_user_id
* content
* letter_type
* status
* scheduled_at
* sent_at
* created_at
* updated_at

권장 enum:

```text
letter_type: instant, scheduled, timecapsule
status: draft, scheduled, sent, canceled
```

### 7.6 Mission

미션 템플릿 또는 사용자별 미션 정보를 저장한다.

필수 필드 예시:

* id
* title
* description
* reward_type
* reward_value
* created_at

### 7.7 WeeklyReport

주간 리포트 결과를 저장한다.

필수 필드 예시:

* id
* relationship_id
* week_start
* week_end
* average_score
* best_day
* worst_day
* summary
* created_at

---

## 8. 의존성 주입 규칙

`app/api/deps.py`에는 공통 의존성을 정의한다.

권장 예시:

```python
from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.services.auth_service import AuthService


def get_db() -> Generator[Session, None, None]:
    """요청 단위 DB 세션을 생성하고 종료한다."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """AuthService 인스턴스를 주입한다."""
    return AuthService(db=db)
```

서비스 주입이 필요한 라우터에서는 다음 형태를 사용한다.

```python
from fastapi import APIRouter, Depends, status

from app.api.deps import get_auth_service
from app.schemas.auth import SignupRequest, AuthResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(
    payload: SignupRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    """회원가입을 처리한다."""
    return auth_service.signup(payload)
```

---

## 9. 예외 처리 규칙

서비스에서는 도메인 예외를 발생시키고, FastAPI exception handler 또는 공통 exception class를 통해 응답을 표준화한다.

권장 예외 클래스:

```python
class AppException(Exception):
    """애플리케이션 공통 예외다."""

    def __init__(self, code: str, message: str, status_code: int) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)
```

예외 응답은 반드시 공통 실패 응답 형식을 따른다.

---

## 10. 인증/보안 구현 기준

* 비밀번호는 절대 평문 저장하지 않는다.
* `app/core/security.py`에서 해싱과 JWT 생성을 담당한다.
* access token과 refresh token을 분리한다.
* 인증이 필요한 라우터는 `get_current_user`를 `Depends`로 주입한다.
* 다른 사용자의 리소스에 접근하는 경우 반드시 소유권 또는 관계 권한을 검증한다.

---

## 11. AI 기능 구현 기준

타로 해석, 궁합 요약, 주간 리포트 요약처럼 AI가 필요한 기능은 서비스에서 직접 AI API를 호출하지 않는다.

반드시 아래 구조를 사용한다.

```text
app/adapters/ai_client.py
```

권장 인터페이스:

```python
from typing import Protocol


class AIClient(Protocol):
    """AI 호출 클라이언트 인터페이스다."""

    def generate_tarot_interpretation(
        self,
        question: str,
        card_name: str,
        card_orientation: str,
    ) -> str:
        """타로 해석 문장을 생성한다."""
        ...

    def generate_compatibility_summary(
        self,
        final_score: int,
        context: dict[str, object],
    ) -> str:
        """궁합 요약 문장을 생성한다."""
        ...
```

테스트에서는 `FakeAIClient` 또는 `Mock` 객체로 대체한다.

---

## 12. 파일/이미지 저장소 구현 기준

프로필 이미지, 편지 첨부 이미지 등 파일 업로드 기능은 저장소 adapter로 분리한다.

```text
app/adapters/storage_client.py
```

권장 인터페이스:

```python
from typing import Protocol


class StorageClient(Protocol):
    """파일 저장소 클라이언트 인터페이스다."""

    def create_presigned_upload_url(
        self,
        file_key: str,
        content_type: str,
    ) -> dict[str, str]:
        """업로드용 presigned URL을 생성한다."""
        ...
```

Firebase, Supabase, S3 계열 저장소 중 무엇을 사용하더라도 서비스 레이어는 adapter 인터페이스에만 의존해야 한다.

---

## 13. 테스트 작성 기준

### 13.1 테스트 구성

* `tests/conftest.py`에 공통 fixture를 둔다.
* DB 세션은 mock 또는 테스트 전용 in-memory DB를 사용한다.
* AI client와 storage client는 fake 또는 mock 객체로 대체한다.
* 외부 네트워크 호출은 테스트에서 발생하면 안 된다.

### 13.2 테스트 예시 구조

```python
from unittest.mock import Mock


def test_signup_success() -> None:
    """정상 회원가입이 성공하는지 검증한다."""
    db = Mock()
    service = AuthService(db=db)

    # 테스트 구현
```

### 13.3 반드시 검증할 항목

* 응답 success 값
* 응답 data 구조
* message 값
* 에러 code 값
* status code
* 서비스 메서드 호출 여부
* mock adapter 호출 여부

---

## 14. Codex 작업 방식

Codex로 기능을 구현할 때는 다음 방식으로 진행한다.

1. 먼저 현재 파일 구조를 확인한다.
2. 기존 코드 스타일을 확인한다.
3. API 명세와 이 문서를 기준으로 구현 범위를 결정한다.
4. 반드시 Schemas → Routers → Services → Tests → Adapters 순서로 변경한다.
5. 변경한 파일 목록을 마지막에 요약한다.
6. 테스트 실행 명령을 제시한다.
7. 테스트를 실행할 수 없는 상황이면 그 이유를 명확히 적는다.

---

## 15. `/goal` 사용 시 기본 지시문

Codex `/goal`에 기능 구현을 요청할 때는 아래 원칙을 따른다.

```text
이 프로젝트의 AGENTS.md 규칙을 반드시 따른다.
새 기능은 Schemas → Routers → Services → Tests → Adapters 순서로 구현한다.
FastAPI 라우터에서는 Depends 기반 의존성 주입을 사용한다.
라우터에는 비즈니스 로직을 두지 않는다.
AI, 저장소, 외부 API 호출은 adapters 디렉터리로 분리한다.
테스트는 pytest로 작성하고 외부 의존성은 모두 mock 처리한다.
공통 성공/실패 응답 형식을 반드시 유지한다.
설명과 코드 주석은 한국어로 작성하고, 변수명과 함수명은 영어로 작성한다.
```

---

## 16. 기능 구현 요청 템플릿

새 기능을 요청할 때는 아래 형식을 사용한다.

```text
/goal
[기능명] 기능을 구현해줘.

요구사항:
- 엔드포인트:
- 인증 필요 여부:
- Request schema:
- Response schema:
- 주요 비즈니스 규칙:
- 실패 케이스:
- 테스트에 포함할 케이스:

반드시 AGENTS.md의 구현 순서와 프로젝트 구조를 지켜줘.
```

---

## 17. 품질 기준

완료된 구현은 아래 조건을 만족해야 한다.

* API 명세와 응답 형식이 일치한다.
* Pydantic schema가 요청/응답을 명확히 제한한다.
* 라우터와 서비스 책임이 분리되어 있다.
* 외부 의존성이 adapter로 분리되어 있다.
* 테스트가 mock 기반으로 안정적으로 동작한다.
* 예외 응답이 공통 실패 응답 형식을 따른다.
* 인증/권한 검증이 필요한 곳에 누락되지 않는다.
* 파일 위치가 프로젝트 구조와 일치한다.
* 코드가 PEP 8과 타입 힌트를 따른다.

---

## 18. 절대 금지 사항

* 라우터에 비즈니스 로직 작성 금지
* 서비스에서 직접 AI API 호출 금지
* 서비스에서 직접 Firebase/Supabase/S3 SDK 호출 금지
* 테스트에서 실제 외부 API 호출 금지
* 테스트에서 실제 운영 DB 연결 금지
* 공통 응답 형식 무시 금지
* 인증 필요한 API에서 `get_current_user` 누락 금지
* 사용자 소유 리소스 권한 검증 누락 금지
* 설명과 주석을 영어로 작성 금지
* 임의의 폴더 구조 생성 금지

---

## 19. 우선 구현 권장 순서

MVP 기준으로는 아래 순서로 구현한다.

1. 공통 설정

   * `core/config.py`
   * `core/db.py`
   * `core/response.py`
   * `core/security.py`
   * `models/base.py`

2. Auth

   * 회원가입
   * 로그인
   * 토큰 재발급
   * 내 정보 조회

3. Users

   * 내 프로필 수정
   * 프로필 이미지 presign

4. Relationships

   * 관계 생성
   * 관계 수락
   * 내 관계 목록 조회

5. Tarot

   * 오늘의 타로 생성
   * 타로 기록 조회
   * AI adapter 분리

6. Compatibility

   * 오늘의 궁합 조회
   * 오늘의 궁합 재계산

7. Letters

   * 편지 작성
   * 편지 목록 조회
   * 편지 상세 조회
   * 첨부 이미지 presign

8. Missions

   * 오늘의 미션 조회
   * 미션 완료 처리

9. Reports

   * 주간 리포트 조회
   * 주간 리포트 생성

10. Internal / Admin

    * 일간 궁합 배치
    * 예약 편지 발송 배치
    * 주간 리포트 배치

---

## 20. 최종 작업 보고 형식

Codex가 작업을 완료하면 아래 형식으로 보고한다.

```text
구현 완료 요약

1. 변경 파일
- app/schemas/...
- app/api/v1/...
- app/services/...
- tests/...

2. 구현 내용
- ...

3. 테스트
- 실행 명령:
  pytest
- 결과:
  ...

4. 주의 사항
- ...
```
