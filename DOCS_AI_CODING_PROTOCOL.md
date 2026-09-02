# 📜 LeRobot 2D PushT Simulator // AI 코딩 프로토콜 및 문서 거버넌스

본 문서는 `Lerobot_simulator` 프로젝트 내에서 AI가 코드를 작성, 리팩토링, 디버깅할 때 준수해야 하는 **최상위 헌법(Constitution)**입니다.

---

## 🗺️ 1. 5대 거버넌스 문서 매핑 (Document Mapping)

AI는 특정 작업을 수행하기 전에 반드시 아래 표를 참조하여 해당 도메인의 상세 기획 문서를 먼저 로드해야 합니다:

| 작업 영역 | 참조 필수 문서 | 핵심 내용 |
| :--- | :--- | :--- |
| **전체 아키텍처 및 제어 흐름** | [DOCS_SYSTEM_ARCHITECTURE.md](file:///c:/Users/crack/Lerobot_simulator/DOCS_SYSTEM_ARCHITECTURE.md) | 물리 엔진, 웹 캔버스, 파이썬 브릿지, 에피소드 레코더 아키텍처 |
| **물리 상태 & 데이터셋 규격** | [DOCS_DATA_SCHEMA.md](file:///c:/Users/crack/Lerobot_simulator/DOCS_DATA_SCHEMA.md) | 2D 상태/행동 공간, IoU 수식, LeRobot 표준 JSON/Parquet 스키마 |
| **평가 기준 & 허깅페이스 배포** | [DOCS_MODEL_EVALUATION_AND_HF_DEPLOY.md](file:///c:/Users/crack/Lerobot_simulator/DOCS_MODEL_EVALUATION_AND_HF_DEPLOY.md) | 텔레옵 성공 판정 루브릭, Hugging Face Spaces & Datasets 원클릭 배포 가이드 |
| **UI/UX 디자인 및 HUD 계기판** | [DOCS_UI_DESIGN_SPEC.md](file:///c:/Users/crack/Lerobot_simulator/DOCS_UI_DESIGN_SPEC.md) | 사이버펑크 랩 다크모드, Bento Grid 레이아웃, 컬러 토큰, CSS 규격 |

---

## ⚖️ 2. AI 행동 4대 절대 원칙 (Core Rules)

### 1. No Vibe-Coding (문서 기반 개발)
* 기획서와 확정된 스키마를 무시하고 임의로 변수명이나 물리 계수를 변경하는 행위를 금지합니다.
* 모든 변경 사항은 `DOCS_DATA_SCHEMA.md`에 명시된 좌표계(512x512 World Space)와 수학적 수식을 따릅니다.

### 2. Auto-Sync Documentation (자동 문서 동기화)
* 코드 로직, 데이터 포맷, 물리 파라미터가 변경된 경우, 사용자의 추가 지시가 없더라도 **모든 연관 `DOCS_*.md` 문서를 스스로 찾아 동시에 업데이트**해야 합니다.

### 3. Hugging Face Spaces Zero-Dependency (웹 배포 무결성)
* 웹 시뮬레이터(`index.html`, `style.css`, `pusht_sim.js`)는 정적 호스팅(Static Spaces) 환경에서 외부 복잡한 번들러 없이 단독 구동될 수 있도록 유지합니다.

### 4. Zero Hallucinated Teleop Data (데이터 무결성)
* 임의의 가짜 텔레옵 데이터를 생성하여 주입하지 않고, 실제 물리 엔진 롤아웃 및 마우스 이벤트 좌표만을 데이터셋으로 기록합니다.
