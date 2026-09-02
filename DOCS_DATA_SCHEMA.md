# 📊 LeRobot 2D PushT Simulator // 데이터 스키마 명세서

본 문서는 시뮬레이터의 상태 공간(Observation Space), 행동 공간(Action Space), 그리고 Hugging Face LeRobot 표준 에피소드 데이터셋의 JSON/Parquet 스키마를 정의합니다.

---

## 🧭 1. 공간 정의 (State & Action Space)

### 1.1 관측 공간 (Observation Space)
LeRobot PushT 환경의 상태 벡터는 총 5차원으로 구성됩니다:

$$s_t = [x_{agent}, y_{agent}, x_{block}, y_{block}, \theta_{block}]$$

| 변수명 | 차원 | 유효 범위 | 단위/설명 |
| :--- | :--- | :--- | :--- |
| `agent_pos[0]` ($x$) | Float | $[18.0, 494.0]$ | 에이전트 중심 X 좌표 (px) |
| `agent_pos[1]` ($y$) | Float | $[18.0, 494.0]$ | 에이전트 중심 Y 좌표 (px) |
| `block_pose[0]` ($x$) | Float | $[30.0, 482.0]$ | T-Block 질량 중심 X 좌표 (px) |
| `block_pose[1]` ($y$) | Float | $[30.0, 482.0]$ | T-Block 질량 중심 Y 좌표 (px) |
| `block_pose[2]` ($\theta$) | Float | $[-\pi, +\pi]$ | T-Block 회전각 (Radian) |

### 1.2 행동 공간 (Action Space)
에이전트가 이동하고자 하는 2D 목표 위치:

$$a_t = [x_{target}, y_{target}]$$

---

## 🎯 2. 보상 및 목표 커버리지(IoU) 수식

목표 포즈 $G = (x_g=256, y_g=256, \theta_g=0.0)$에 대해:

1. **위치 점수 (Position Score)**:
   $$S_{pos} = \max\left(0, 1 - \frac{\sqrt{(x_b - x_g)^2 + (y_b - y_g)^2}}{140}\right)$$

2. **각도 점수 (Rotation Score)**:
   $$S_{rot} = \max\left(0, 1 - \frac{|\theta_b - \theta_g|}{1.2}\right)$$

3. **최종 커버리지 (Coverage Ratio)**:
   $$\text{Coverage} = \min\left(1.0, (0.65 \cdot S_{pos} + 0.35 \cdot S_{rot})\right)$$
   * $\text{Coverage} \ge 0.90$ (90% 이상) 달성 시 `success = True`.

---

## 📦 3. LeRobot 표준 데이터셋 포맷 (JSON Schema)

내보내기(`[💾 Export Dataset]`) 및 파이썬 저장 시 생성되는 JSON 구조:

```json
[
  {
    "id": 1,
    "length": 340,
    "maxCoverage": 0.942,
    "success": true,
    "timestamp": "16:25:30",
    "frames": [
      {
        "step": 1,
        "agent": [256.0, 100.0],
        "block": [256.0, 320.0, 0.400],
        "target": [256.0, 105.0],
        "coverage": 0.462,
        "success": false
      },
      {
        "step": 2,
        "agent": [256.0, 103.2],
        "block": [256.0, 320.0, 0.400],
        "target": [256.0, 110.0],
        "coverage": 0.462,
        "success": false
      }
    ]
  }
]
```
