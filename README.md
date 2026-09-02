---
title: LeRobot 2D PushT Interactive Teleop Simulator
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: static
pinned: false
license: mit
tags:
- robotics
- lerobot
- imitation-learning
- physical-ai
- pusht
- teleoperation
---

# 🤖 LeRobot 2D PushT Interactive Teleop Simulator

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Framework: LeRobot](https://img.shields.io/badge/LeRobot-HuggingFace-yellow.svg)](https://github.com/huggingface/lerobot)
[![Physics: 60FPS](https://img.shields.io/badge/Physics-60FPS_SAT-green.svg)](pusht_sim.js)
[![Korean Doc](https://img.shields.io/badge/Language-한국어-red.svg)](README_KR.md)

An interactive, zero-dependency 2D Physical AI Simulator for the **Hugging Face LeRobot PushT benchmark**.
Experience real-time mouse teleoperation, collect demonstration datasets, evaluate goal coverage (IoU), and test autonomous AI autopilot rollouts directly in your browser or native Python!

---

## 🎮 Key Features

1. **🖱️ Real-time Mouse Teleoperation**:
   - Control the circle end-effector with spring/PD dynamic tracking ($K_p=0.28, K_d=0.12$).
2. **⚡ 60 FPS 2D Rigid Body Physics Engine**:
   - Custom Separating Axis Theorem (SAT) collision resolution, impulse response, friction, and torque mechanics.
3. **🎯 Live Goal Alignment (IoU Coverage Evaluator)**:
   - High-precision real-time IoU calculation between the T-block and the goal target zone.
4. **📦 Episode Dataset Recorder & Replay**:
   - Record 60Hz state-action demonstration trajectories and export directly to LeRobot-compatible JSON format.
5. **🤖 AI Autopilot Demo**:
   - Autonomous heuristic trajectory planner for self-aligning T-block demonstrations.
6. **🚀 One-Click Hugging Face Deployment**:
   - Built-in deployment script (`deploy_to_hf.py`) to publish directly to Hugging Face Spaces & Datasets Hub.

---

## 🕹️ Quick Start

### 1. Web Interactive Simulator (Browser)
```bash
python server.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

### 2. Python Native Pygame Teleop
```bash
python pusht_teleop.py
```
* **Controls**: Mouse (Move Robot), `SPACE` (Toggle Record & Auto-Save JSON), `R` (Reset Environment).

### 3. Deploy to Hugging Face Spaces / Datasets
```bash
python deploy_to_hf.py
```

---

## 📁 Repository Governance & Architecture

* [.cursorrules](file:///.cursorrules): AI Vibe-coding & robotics defense guidelines.
* [DOCS_AI_CODING_PROTOCOL.md](file:///DOCS_AI_CODING_PROTOCOL.md): Master constitution and document mappings.
* [DOCS_SYSTEM_ARCHITECTURE.md](file:///DOCS_SYSTEM_ARCHITECTURE.md): Physics engine & dual execution architecture.
* [DOCS_DATA_SCHEMA.md](file:///DOCS_DATA_SCHEMA.md): State/action space and LeRobot dataset schemas.
* [DOCS_MODEL_EVALUATION_AND_HF_DEPLOY.md](file:///DOCS_MODEL_EVALUATION_AND_HF_DEPLOY.md): Evaluation rubrics & HF deployment guide.
* [DOCS_UI_DESIGN_SPEC.md](file:///DOCS_UI_DESIGN_SPEC.md): Cyberpunk lab dark-mode design specifications.

---

## 📄 License
MIT License. Created for Physical AI Solopreneurs and Roboticists.
