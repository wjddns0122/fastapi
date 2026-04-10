# 💌 오늘의 궁합 - 관계를 매일 조금씩 좋게 만드는 앱

> 사주와 타로를 핑계로, 관계를 매일 조금씩 좋게 만드는 게임형 앱.

---

## 📱 서비스 소개

오늘의 궁합은 단순한 운세 앱이 아닙니다.  
사주 · 타로 · 행동지수를 결합한 **동적 궁합 엔진**을 기반으로,  
매일 편지를 쓰고 미션을 수행하며 관계를 직접 변화시켜 나가는 **행동형 관계 앱**입니다.

---

## ✨ 핵심 기능

### 🔮 오늘의 궁합

매일 변하는 실시간 궁합 점수 시스템

```
오늘 궁합 = 기본 궁합 (사주) + 오늘의 운세 변수 (타로) + 관계 행동 점수 (미션/편지)
```

- 오늘의 궁합 점수 및 키워드 3개
- 타로 1장 + 오늘의 관계 처방전
- 행동하면 점수가 올라가는 동적 구조
- 지난 7일 궁합 추이 그래프

### 💌 편지 시스템

단순 채팅이 아닌 **비동기 감정 전달** 플랫폼

- 오늘의 편지 작성 및 즉시 발송
- 예약 발송 (기념일, 특정 날짜)
- 조건부 발송 (상대 기분이 낮은 날 / 7일 뒤 / 100일 뒤)
- 타임캡슐 편지
- 타로 기반 문장 템플릿 추천
- 편지지 테마 · 봉인 애니메이션

### 🎯 미션 / 관계 레벨업

궁합을 "보는 앱"에서 "행동하는 앱"으로

- 매일 1~3개 데일리 미션
- 미션 수행 시 궁합 점수 보정
- 스트릭 · 배지 · 관계 경험치
- 달성 보상 (특별 편지지, 프리미엄 타로 등)

### 📊 관계 리포트

데이터 기반 관계 분석 (프리미엄)

- 이번 주 감정 흐름 · 다툼 위험 패턴
- 잘 맞는 대화 시간대 분석
- 월간 · 연간 궁합 변화 리포트
- 감정 패턴 · 자주 성공한 미션 통계

---

## 🗂️ 프로젝트 구조

```
.
├── app/
│   └── main.py                  # FastAPI 앱 진입점
├── core/                        # 공통 설정 및 유틸리티
│   ├── config.py                # 환경 변수 및 앱 설정
│   ├── database.py              # DB 연결 설정
│   ├── dependencies.py          # 공통 의존성 (인증 등)
│   └── security.py              # JWT · 암호화 유틸
├── modules/
│   ├── auth/                    # 인증 · 소셜 로그인
│   │   ├── router.py
│   │   ├── service.py
│   │   └── schemas.py
│   ├── users/                   # 사용자 정보 · 프로필
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── relationships/           # 관계 연결 · 초대 링크
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── compatibility/           # 궁합 엔진 (핵심)
│   │   ├── router.py
│   │   ├── service.py           # 기본궁합 + 운세변수 + 행동점수 계산
│   │   ├── engine.py            # 동적 궁합 알고리즘
│   │   ├── models.py
│   │   └── schemas.py
│   ├── tarot/                   # 타로 카드 · 오늘의 운세
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── letters/                 # 편지 · 타임캡슐 · 예약 발송
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── scheduler.py         # 예약/조건부 발송 스케줄러
│   │   ├── models.py
│   │   └── schemas.py
│   ├── missions/                # 데일리 미션 · 스트릭 · 보상
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── schemas.py
│   └── reports/                 # 관계 리포트 · 분석 (프리미엄)
│       ├── router.py
│       ├── service.py
│       ├── models.py
│       └── schemas.py
├── .github/
│   └── workflows/
│       └── deploy.yml           # Railway 자동 배포
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🛠️ 기술 스택

| 구분     | 기술                         |
| -------- | ---------------------------- |
| Backend  | FastAPI (Python 3.11)        |
| Database | PostgreSQL + SQLAlchemy      |
| Cache    | Redis                        |
| 인증     | JWT + OAuth2 (카카오 · 애플) |
| 스케줄러 | APScheduler (편지 예약 발송) |
| 배포     | Railway                      |
| CI/CD    | GitHub Actions               |
| 컨테이너 | Docker                       |

---

## 🚀 로컬 실행

### 1. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일에 DB, JWT, 외부 API 키 입력
```

### 2. Docker로 실행

```bash
docker build -t today-compatibility .
docker run -p 8000:8000 --env-file .env today-compatibility
```

### 3. 로컬 직접 실행

```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 3-1. 마이그레이션

```bash
# 최신 스키마 반영
alembic upgrade head

# 새 리비전 생성
alembic revision -m "add_xxx"
```

### 4. API 문서 확인

```
http://localhost:8000/docs      # Swagger UI
http://localhost:8000/redoc     # ReDoc
```

---

## 📦 배포

`main` 브랜치에 push하면 Railway에 자동 배포됩니다.

```bash
git push origin main
# → GitHub Actions 실행
# → Railway 자동 배포
# → https://your-app.up.railway.app
```

---

## 💰 수익화 구조

| 플랜                  | 제공 범위                                                         |
| --------------------- | ----------------------------------------------------------------- |
| 무료                  | 오늘의 궁합 점수, 타로 1장, 편지 작성, 기본 미션, 최근 7일 기록   |
| 프리미엄 (월 4,900원) | 궁합 상세 해설, 월간 리포트, 감정 패턴 분석, 프리미엄 편지지/테마 |
| 1회성 리포트          | 월간 관계 리포트 2,900원 / 연간 리포트 9,900원                    |
| 아이템                | 스페셜 편지지, 봉인 이펙트, 캐릭터 스킨 1,000원~4,900원           |

---

## 📋 MVP 개발 로드맵

- [x] 프로젝트 초기 세팅 및 배포 환경 구성
- [ ] 회원가입 / 로그인 / 관계 연결
- [ ] 궁합 엔진 (기본 궁합 + 타로 변수 + 행동 보정)
- [ ] 오늘의 궁합 홈 화면 API
- [ ] 편지 작성 / 예약 발송 / 타임캡슐
- [ ] 데일리 미션 / 스트릭 / 보상
- [ ] 관계 리포트 (프리미엄)
- [ ] 결제 연동 (인앱 구매)

---

## 📄 라이선스

Private Repository - All rights reserved.
