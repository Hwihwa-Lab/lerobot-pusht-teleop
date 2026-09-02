# 🎨 LeRobot 2D PushT Simulator // UI/UX 디자인 규격서

본 문서는 `LeRobot 2D PushT 시뮬레이터`의 사이버펑크 랩(Cyberpunk Lab) 다크모드 디자인 토큰, 3단 Bento Grid 레이아웃 및 컴포넌트 규격을 정의합니다.

---

## 🎨 1. 컬러 팔레트 & 디자인 토큰 (Design Tokens)

| 토큰명 | 색상 코드 | 용도 |
| :--- | :--- | :--- |
| `--bg-primary` | `#0a0d14` | 메인 백그라운드 래디얼 그라디언트 |
| `--bg-card` | `rgba(18, 24, 38, 0.85)` | 글래스모피즘 Bento Grid 카드 |
| `--accent-cyan` | `#00f2fe` | 주 강조색, 로봇 궤적 라인, 커버리지 HUD |
| `--accent-green` | `#00e676` | 성공(Success) 상태 배지, 정렬 완료 테두리 |
| `--accent-red` | `#ff3366` | 녹화 중(Recording) 상태 표시, 질량 중심 점 |
| `--accent-purple`| `#9d4edd` | 에이전트 좌표 메트릭, AI 오토파일럿 버튼 |
| `--border-color` | `rgba(64, 93, 140, 0.25)`| 은은한 사이버네틱 카드 테두리 |

---

## 📐 2. Bento Grid 레이아웃 사양 (Layout Specification)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Header: LeRobot PushT Teleop Simulator (v1.0 Live)  [● 60 FPS Physics Active]│
├──────────────────────────────────────┬──────────────────────────────────────┤
│ 1. SIMULATION VIEWPORT (580x580)     │ 2. METRICS & TELEMETRY PANEL         │
│  • 2D Canvas with 32px Grid          │  • 4 Stat Cards (Coverage, Steps,    │
│  • Goal Silhouette (Translucent Cyan)│    Agent Pos, T-Block Pose)          │
│  • T-Block & Agent (Glow Effects)    │  • Realtime Trajectory Mini-Chart    │
│  • 4 Action Buttons Toolbar          ├──────────────────────────────────────┤
│    [Reset] [Record] [AI] [Export]    │ 3. TELEOP INSTRUCTIONS GUIDE BOX     │
│                                      ├──────────────────────────────────────┤
│                                      │ 4. DATASET EPISODES TABLE            │
│                                      │  • ID / Frames / Peak / Status / Play│
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## ✨ 3. 마이크로 인터랙션 & 가이드라인
* **원스크린 데스크톱 보존**: 뷰포트 $1536 \times 762$ 기준에서 불필요한 스크롤이 발생하지 않도록 콤팩트한 패딩과 그리드 배치를 유지합니다.
* **녹화 펄스 애니메이션**: `[🔴 Record Teleop]` 활성화 시 붉은색 네온 글로우 펄스 애니메이션이 가동됩니다.
* **목표 달성 시 시각적 전환**: 목표 커버리지 90% 이상 시 실시간으로 T-Block 테두리와 배지가 네온 에메랄드 그린(`--accent-green`)으로 전환됩니다.
