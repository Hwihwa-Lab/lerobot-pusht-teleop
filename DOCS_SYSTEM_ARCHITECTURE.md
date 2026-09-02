# 🏗️ LeRobot 2D PushT Simulator // 시스템 아키텍처 명세서 (v2.0 Unified)

본 문서는 `LeRobot 2D PushT 시뮬레이터`의 **FastAPI + WebSocket 실시간 파이썬 백엔드 동기화 및 하이브리드 배포 아키텍처**를 정의합니다.

---

## 🧭 1. 엔드투엔드 시스템 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             USER INTERACTION LAYER                          │
│     [ Web Browser (localhost:8000) ]           [ Python Pygame Native App ] │
│     • Mouse Move / Drag 텔레옵                 • Mouse Drag / SPACE Record  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                      WebSocket Stream │ (60 FPS Bi-directional)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PYTHON FASTAPI BACKEND (server.py)                       │
│                                                                             │
│   ┌───────────────────────────┐         ┌───────────────────────────────┐   │
│   │   PD Spring Controller    │         │     2D Rigid Body Physics     │   │
│   │   • Kp=0.28, Kd=0.12      │ ──────▶ │     • Top Bar (150x40)        │   │
│   │   • Target (x, y) Tracking│         │     • Stem Bar (40x110)       │   │
│   │   • Speed Clamp (16 px/s) │         │     • SAT Collision & Torque  │   │
│   └───────────────────────────┘         └───────────────────────────────┘   │
│                                                         │                   │
│                                                         ▼                   │
│   ┌───────────────────────────┐         ┌───────────────────────────────┐   │
│   │  Auto Dataset Collector   │         │    Goal Coverage Evaluator    │   │
│   │  • Auto-save JSON on stop │ ◀────── │     • Pos Dist & Angle Diff   │   │
│   │  • LeRobot Schema Compliant│        │     • IoU Metric (0.0 ~ 1.0)  │   │
│   └───────────────────────────┘         └───────────────────────────────┘   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
┌──────────────────────────────────────┐┌─────────────────────────────────────┐
│         LOCAL DEVELOPMENT            ││     HUGGING FACE DEPLOYMENT         │
│ • FastAPI 60Hz 실시간 텔레메트리     ││ • deploy_to_hf.py 원클릭 배포       │
│ • 로컬 JSON 데이터셋 자동 축적       ││ • 1) Models Hub (가중치 & 번들)     │
│ • 브라우저 = 파이썬 실시간 조종석    ││ • 2) Datasets Hub (수집 데이터셋)   │
│                                      ││ • 3) Spaces (웹 실시간 라이브 데모) │
└──────────────────────────────────────┘└─────────────────────────────────────┘
```

---

## 📁 2. 핵심 파일별 역할 및 기술 스택

| 파일 경로 | 역할 및 책임 | 주요 기술 스택 |
| :--- | :--- | :--- |
| `server.py` | FastAPI + WebSocket 60Hz 파이썬 물리 연산 및 데이터셋 자동 저장 백엔드 | FastAPI, Uvicorn, WebSockets |
| `index.html` | 사이버펑크 Bento Grid 관제 HUD 웹 대시보드 | HTML5 Semantic Elements |
| `style.css` | 60fps 다크모드 글래스모피즘 스타일링 | Vanilla CSS3, Grid/Flexbox |
| `pusht_sim.js` | WebSocket 실시간 백엔드 스트림 동기화 및 오프라인 Fallback 렌더러 | Vanilla JS (ES6+), Canvas 2D |
| `pusht_teleop.py` | 독립형 파이썬 Pygame 텔레옵 클라이언트 | Python 3, Pygame |
| `deploy_to_hf.py` | Models / Datasets / Spaces 3종 지원 원클릭 허깅페이스 배포 파이프라인 | `huggingface_hub` SDK |

---

## ⚙️ 3. 하이브리드 무결성 (Zero-Downtime Fallback)

1. **로컬 실행 모드 (`python server.py`)**:
   - 웹 브라우저(`http://localhost:8000`) 접속 시 WebSocket이 파이썬 백엔드와 연결되어 **파이썬 엔진이 직접 물리 계산과 텔레메트리 브로드캐스트를 60fps로 전담**합니다.
   - 녹화 완료 시 로컬 디스크에 LeRobot 포맷 JSON 데이터셋이 즉시 자동 저장됩니다.
2. **허깅페이스 Spaces 정적 배포 모드**:
   - WebSocket 연결이 없는 정적 웹 호스팅 환경에서는 `pusht_sim.js` 내장 JS 물리 엔진으로 자동 전환되어 전 세계 누구나 브라우저에서 다운타임 없이 마우스 텔레옵을 체험할 수 있습니다.
