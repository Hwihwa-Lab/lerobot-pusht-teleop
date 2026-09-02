# -*- coding: utf-8 -*-
"""
One-Click Hugging Face Deployment Pipeline for LeRobot 2D PushT Simulator.
Supports:
1) Hugging Face Models (Default - Model bundle, weights & README card)
2) Hugging Face Datasets (LeRobot standard - Teleop demonstration JSON datasets)
3) Hugging Face Spaces (Interactive live web demo)
"""

import os
import sys
import glob
import json
import zipfile
from pathlib import Path

try:
    from huggingface_hub import HfApi, create_repo
except ImportError:
    HfApi = None  # type: ignore
    create_repo = None  # type: ignore

def generate_model_card(repo_id: str) -> str:
    """Generate Hugging Face Model Card with metadata."""
    return f"""---
language:
- en
- ko
license: mit
tags:
- robotics
- lerobot
- imitation-learning
- physical-ai
- pusht
- teleoperation
- 2d-physics
pipeline_tag: robotics
---

# 🤖 LeRobot 2D PushT Simulator & Teleoperation Bundle

Interactive 2D Physical AI Simulator and Demonstration Collector for the **Hugging Face LeRobot** PushT benchmark.

## 📦 Contents
- **Standalone 2D Physics Simulator** (60 FPS SAT collision, impulse response, friction)
- **Real-time Mouse Teleoperation Engine** (PD spring tracking)
- **Goal Coverage Evaluator** (Real-time IoU calculation)
- **LeRobot Compatible Episode Datasets**

## 🕹️ Quick Run
```bash
# 1. Run Web Dashboard
python server.py

# 2. Run Python Pygame Window
python pusht_teleop.py
```

## 🔗 References
- [Hugging Face LeRobot Official Repository](https://github.com/huggingface/lerobot)
"""

def generate_spaces_readme(repo_id: str) -> str:
    """Generate Hugging Face Space README with Static SDK."""
    return f"""---
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
Live interactive Web Simulator for Hugging Face LeRobot PushT benchmark.
"""

def create_bundle_zip(current_dir: Path) -> str:
    zip_path = current_dir / "lerobot_pusht_bundle.zip"
    include_files = [
        "index.html", "style.css", "pusht_sim.js", "pusht_teleop.py",
        "server.py", "README.md", "README_KR.md", "DOCS_AI_CODING_PROTOCOL.md",
        "DOCS_SYSTEM_ARCHITECTURE.md", "DOCS_DATA_SCHEMA.md",
        "DOCS_MODEL_EVALUATION_AND_HF_DEPLOY.md", "DOCS_UI_DESIGN_SPEC.md"
    ]
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for f in include_files:
            fp = current_dir / f
            if fp.exists():
                zipf.write(fp, arcname=f)
    print(f"📦 Created bundle archive: {zip_path.name}")
    return str(zip_path)

def deploy():
    print("=" * 65)
    print("🚀 LeRobot 2D PushT - Hugging Face Universal Deployment Pipeline")
    print("=" * 65)

    # 1. Get Hugging Face Token
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("\n🔑 Hugging Face Write Token이 필요합니다.")
        print("토큰 확인: https://huggingface.co/settings/tokens")
        token = input("HF Token 입력: ").strip()

    if not token:
        print("❌ 토큰이 입력되지 않아 배포를 취소합니다.")
        return

    api = HfApi(token=token)

    try:
        user_info = api.whoami()
        username = user_info["name"]
        print(f"✅ Authenticated as: {username}")
    except Exception as e:
        print(f"❌ 인증 실패: {e}")
        return

    # 2. Select Deployment Target
    print("\n[배포 대상 저장소 선택]")
    print("1) Hugging Face Models   (기존 프로젝트 방식 - 모델 및 시뮬레이터 번들 업로드) [추천]")
    print("2) Hugging Face Datasets (LeRobot 표준 - 수집된 텔레옵 에피소드 데이터셋 업로드)")
    print("3) Hugging Face Spaces   (웹 브라우저 실시간 라이브 데모 호스팅)")
    choice = input("\n선택 번호 (1/2/3, 기본값: 1): ").strip() or "1"

    current_dir = Path(__file__).parent

    # ==========================================
    # Option 1: Hugging Face Models (Standard)
    # ==========================================
    if choice == "1":
        model_name = input(f"Models 레포지토리 이름 [기본값: lerobot-pusht-simulator]: ").strip() or "lerobot-pusht-simulator"
        repo_id = f"{username}/{model_name}"
        print(f"\n📦 Creating/Verifying Model Repo: {repo_id}...")

        try:
            create_repo(repo_id=repo_id, repo_type="model", exist_ok=True, token=token)
            
            # Generate Model Card
            model_card = generate_model_card(repo_id)
            with open(current_dir / "README.md", "w", encoding="utf-8") as f:
                f.write(model_card)

            # Create ZIP bundle
            zip_file = create_bundle_zip(current_dir)

            # Upload bundle and docs
            upload_files = ["README.md", "README_KR.md", "lerobot_pusht_bundle.zip"]
            for fn in upload_files:
                fp = current_dir / fn
                if fp.exists():
                    api.upload_file(
                        path_or_fileobj=str(fp),
                        path_in_repo=fn,
                        repo_id=repo_id,
                        repo_type="model",
                        token=token
                    )
                    print(f"  ✓ {fn} 업로드 완료")

            print(f"\n🎉 Hugging Face Model 업로드 성공!")
            print(f"🌐 레포지토리 URL: https://huggingface.co/{repo_id}")

        except Exception as e:
            print(f"❌ Model 배포 중 오류: {e}")

    # ==========================================
    # Option 2: Hugging Face Datasets
    # ==========================================
    elif choice == "2":
        dataset_name = input(f"Datasets 레포지토리 이름 [기본값: lerobot-pusht-teleop-dataset]: ").strip() or "lerobot-pusht-teleop-dataset"
        repo_id = f"{username}/{dataset_name}"
        print(f"\n📦 Creating/Verifying Dataset Repo: {repo_id}...")

        try:
            create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True, token=token)
            
            json_files = glob.glob(str(current_dir / "pusht_teleop_data_*.json")) + glob.glob(str(current_dir / "lerobot_pusht_dataset_*.json"))
            if not json_files:
                print("⚠️ 로컬에 수집된 JSON 데이터셋 파일이 없습니다. 시뮬레이터에서 먼저 녹화해 주세요.")
            else:
                for jf in json_files:
                    fn = os.path.basename(jf)
                    api.upload_file(
                        path_or_fileobj=jf,
                        path_in_repo=fn,
                        repo_id=repo_id,
                        repo_type="dataset",
                        token=token
                    )
                    print(f"  ✓ {fn} 데이터셋 업로드 완료")

            print(f"\n🎉 Hugging Face Dataset 업로드 성공: https://huggingface.co/datasets/{repo_id}")

        except Exception as e:
            print(f"❌ Dataset 배포 중 오류: {e}")

    # ==========================================
    # Option 3: Hugging Face Spaces
    # ==========================================
    elif choice == "3":
        space_name = input(f"Spaces 레포지토리 이름 [기본값: lerobot-pusht-demo]: ").strip() or "lerobot-pusht-demo"
        repo_id = f"{username}/{space_name}"
        print(f"\n📦 Creating/Verifying Space: {repo_id}...")

        try:
            create_repo(repo_id=repo_id, repo_type="space", space_sdk="static", exist_ok=True, token=token)
            
            readme_content = generate_spaces_readme(repo_id)
            with open(current_dir / "README.md", "w", encoding="utf-8") as f:
                f.write(readme_content)

            files_to_upload = ["index.html", "style.css", "pusht_sim.js", "README.md"]
            for filename in files_to_upload:
                file_path = current_dir / filename
                if file_path.exists():
                    api.upload_file(
                        path_or_fileobj=str(file_path),
                        path_in_repo=filename,
                        repo_id=repo_id,
                        repo_type="space",
                        token=token
                    )
                    print(f"  ✓ {filename} 업로드 완료")

            print(f"\n🎉 Hugging Face Spaces 라이브 데모 배포 성공!")
            print(f"🌐 데모 URL: https://huggingface.co/spaces/{repo_id}")

        except Exception as e:
            print(f"❌ Spaces 배포 중 오류: {e}")

    print("\n" + "=" * 65)
    print("🏁 Deployment Pipeline Finished!")
    print("=" * 65)

if __name__ == "__main__":
    deploy()
