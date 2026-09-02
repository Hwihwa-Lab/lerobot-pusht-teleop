# 📋 LeRobot 2D PushT Simulator // 평가 및 허깅페이스 배포 프로토콜

본 문서는 마우스 텔레오퍼레이션 데이터셋의 품질 평가 기준선과 **Hugging Face Spaces (웹 시뮬레이터)** 및 **Hugging Face Datasets** 배포 절차를 정의합니다.

---

## 1. 📊 텔레옵 에피소드 평가 기준선 (Benchmark Rubrics)

| 평가 지표 | 기준값 (Pass Criteria) | 판정 상태 | 비고 |
| :--- | :--- | :--- | :--- |
| **최대 목표 커버리지 (Peak Coverage)** | $\ge 90\%$ | **PASS (성공)** | T자 블록이 목표 존에 정렬 |
| **에피소드 유효 길이 (Frame Length)** | $100 \sim 1,500$ 프레임 | **PASS (성공)** | 비정상 초단기/장기 세션 필터링 |
| **조작 지연 시간 (Input Latency)** | $< 16 \text{ ms (60 FPS)}$ | **PASS (성공)** | 부드러운 마우스 반응성 유지 |
| **웹 스탠드얼론 무결성** | 무설치 브라우저 구동 | **PASS (성공)** | HF Spaces 배포 적합성 |

---

## 2. 🧪 로컬 검증 명령어

```bash
# 1. 로컬 웹 시뮬레이터 실행 (포트 8000)
python server.py

# 2. 파이썬 Pygame 네이티브 텔레옵 창 실행
python pusht_teleop.py
```

---

## 3. 🚀 허깅페이스 원클릭 배포 프로토콜 (One-Click HF Deploy)

1. **사전 준비**: [Hugging Face Settings > Tokens](https://huggingface.co/settings/tokens)에서 **Write 권한 토큰**을 준비합니다.
2. **배포 실행**:
   ```bash
   python deploy_to_hf.py
   ```
3. 터미널 프롬프트에 토큰을 입력하면:
   - **Hugging Face Spaces (Static)**: 웹 시뮬레이터를 즉시 호스팅하여 누구나 접속 가능한 공개 링크 생성.
   - **Hugging Face Datasets**: 로컬에 수집된 텔레옵 에피소드 JSON 데이터를 Hub 레포지토리로 자동 전송.
