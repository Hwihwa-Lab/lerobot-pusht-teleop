# 🎨 LeRobot 2D PushT Simulator // UI/UX 디자인 규격서

본 문서는 `LeRobot 2D PushT 시뮬레이터`의 사이버펑크 랩(Cyberpunk Lab) 다크모드 디자인 토큰, 3단 Bento Grid 레이아웃, 마스코트 그래픽 및 컴포넌트 규격을 정의합니다.

---

## 🎨 1. 컬러 팔레트 & 디자인 토큰 (Design Tokens)

| 토큰명 | 색상 코드 | 용도 |
| :--- | :--- | :--- |
| `--bg-primary` | `#0a0d14` | 메인 백그라운드 래디얼 그라디언트 |
| `--bg-card` | `rgba(18, 24, 38, 0.85)` | 글래스모피즘 Bento Grid 카드 |
| `--accent-cyan` | `#00f2fe` | 주 강조색, 로봇 궤적 라인, 커버리지 HUD, 차트 채색 |
| `--accent-green` | `#00e676` | 성공(Success) 상태 배지, 정렬 완료 테두리, 90% 목표 점선 |
| `--accent-red` | `#ff3366` | 녹화 중(Recording) 상태 표시, 질량 중심 점 |
| `--accent-purple`| `#9d4edd` | 에이전트 좌표 메트릭, AI 오토파일럿 버튼 |
| `--border-color` | `rgba(64, 93, 140, 0.25)`| 은은한 사이버네틱 카드 테두리 |

---

## 📐 2. Bento Grid 레이아웃 사양 (Layout Specification)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Header: [🤖 Logo] LeRobot PushT Teleop Simulator (v2.0 Live)  [● 60 FPS]     │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ 1. SIMULATION VIEWPORT (580x580)     │ 2. METRICS & TELEMETRY PANEL         │
│  • 2D Canvas with 32px Grid          │  • 4 Stat Cards:                     │
│  • Goal Silhouette (Translucent Cyan)│    1) Coverage + Reward HUD          │
│  • T-Block & Agent (Glow Effects)    │    2) Active Steps + Return HUD      │
│  • 4 Action Buttons Toolbar:         │    3) Agent Position & Speed         │
│    [Reset] [Record] [Autopilot] [Exp]│    4) T-Block Pose & Angle           │
│                                      │  • Realtime Trajectory Area Chart    │
│                                      ├──────────────────────────────────────┤
│                                      │ 3. TELEOP INSTRUCTIONS GUIDE BOX     │
│                                      │  • 4-Step Guide & [Hotkeys Badge]    │
│                                      ├──────────────────────────────────────┤
│                                      │ 4. DATASET EPISODES TABLE            │
│                                      │  • EP ID / Frames / Peak / Status    │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## ✨ 3. 컴포넌트 & 마이크로 인터랙션 규격

1. **🤖 시그니처 로봇 엠블럼 (Robot Mascot)**:
   - 네온 사이언 배경 박스 + 다크 사이버 바이저 + 선명한 듀얼 렌즈 눈빛(`--accent-cyan`) + 상단 안테나 닷으로 구성된 전용 벡터 그래픽.
2. **📈 실시간 100-프레임 오실로스코프 시계열 차트**:
   - `rgba(0, 242, 254, 0.40) ~ 0.18`로 곡선 아래 영역 전체를 풍부하게 채색(Filled Area)하고 상시 90% 녹색 목표 점선 유지.
3. **⏸️ 네온 일시정지 오버레이**:
   - `Space` 키 입력 시 캔버스 중앙에 블러 효과 및 `SIMULATION PAUSED` 배지 팝업.
4. **목표 달성 시 시각적 전환**:
   - 목표 커버리지 90% 이상 시 실시간으로 T-Block 테두리와 배지가 네온 에메랄드 그린(`--accent-green`)으로 전환.
