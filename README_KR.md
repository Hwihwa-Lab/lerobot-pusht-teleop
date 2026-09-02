# 🤖 LeRobot 2D PushT 마우스 텔레오퍼레이션 시뮬레이터

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Framework: LeRobot](https://img.shields.io/badge/LeRobot-HuggingFace-yellow.svg)](https://github.com/huggingface/lerobot)
[![Physics: 60FPS](https://img.shields.io/badge/Physics-60FPS_SAT-green.svg)](pusht_sim.js)
[![English Doc](https://img.shields.io/badge/Language-English-blue.svg)](README.md)

**허깅페이스 LeRobot 생태계**의 대표 2D 벤치마크 환경인 **PushT(T자 블록 밀기)**를 브라우저 및 파이썬에서 마우스로 실시간 조작(Teleoperation)하며 데이터를 수집하고 AI 정책을 체험할 수 있는 고성능 2D 피지컬 AI 시뮬레이터입니다.

---

## 🎮 핵심 기능

1. **🖱️ 실시간 마우스 텔레오퍼레이션**:
   - 마우스 커서를 따라 원형 로봇(End-Effector)이 스프링/PD 역학($K_p=0.28, K_d=0.12$)으로 매끄럽게 추종하며 물리적 힘 전달.
2. **⚡ 60 FPS 2D 강체 물리 엔진**:
   - 분리축 정리(SAT) 기반 충돌 처리, 충돌 임펄스 반발, 마찰력 및 회전 관성 모멘트 계산.
3. **🎯 실시간 목표 일치율 (IoU 커버리지) 연산**:
   - T자 블록이 목표 영역(Goal Zone)에 정렬되는 비율을 실시간 백분율(0~100%)로 산출.
4. **📦 에피소드 데이터 수집 & 리플레이**:
   - 60Hz 단위로 궤적을 기록하고 LeRobot 호환 JSON 데이터셋으로 즉시 내보내기 지원.
5. **🤖 AI 오토파일럿 데모**:
   - AI가 스스로 T자 블록을 목표 위치로 밀어 넣는 자율 주행 데모 모드.
6. **🚀 허깅페이스 원클릭 배포 (`deploy_to_hf.py`)**:
   - Hugging Face Spaces(웹 라이브 데모) 및 Datasets에 토큰 하나로 즉시 배포.

---

## 🕹️ 빠른 실행 가이드

### 1. 웹 인터랙티브 시뮬레이터 (브라우저)
```bash
python server.py
```
브라우저에서 **[http://localhost:8000](http://localhost:8000)** 접속.

### 2. 파이썬 Pygame 네이티브 텔레옵
```bash
python pusht_teleop.py
```
* **조작법:** 마우스 이동(로봇 조작), `SPACE`(녹화 토글 및 자동 JSON 저장), `R`(환경 리셋)

### 3. 허깅페이스 Spaces 및 Datasets 배포
```bash
python deploy_to_hf.py
```

---

## 📁 거버넌스 및 설계 문서 체계

* [.cursorrules](file:///.cursorrules): AI 바이브코딩 방어 및 로보틱스 규격 준수 룰
* [DOCS_AI_CODING_PROTOCOL.md](file:///DOCS_AI_CODING_PROTOCOL.md): 5대 거버넌스 최상위 헌법 문서
* [DOCS_SYSTEM_ARCHITECTURE.md](file:///DOCS_SYSTEM_ARCHITECTURE.md): 시스템 아키텍처 및 물리 엔진 명세
* [DOCS_DATA_SCHEMA.md](file:///DOCS_DATA_SCHEMA.md): 상태/행동 공간 및 LeRobot 데이터셋 스키마
* [DOCS_MODEL_EVALUATION_AND_HF_DEPLOY.md](file:///DOCS_MODEL_EVALUATION_AND_HF_DEPLOY.md): 평가 루브릭 및 배포 프로토콜
* [DOCS_UI_DESIGN_SPEC.md](file:///DOCS_UI_DESIGN_SPEC.md): 사이버펑크 랩 다크모드 UI 규격서
