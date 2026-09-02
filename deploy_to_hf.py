# -*- coding: utf-8 -*-
"""
HWIHWA LAB Universal Hugging Face Deployment Pipeline
One-Click Deployment for LeRobot 2D PushT Interactive Teleop Simulator.
Supports:
1) Hugging Face Spaces (Live Interactive Web Simulator - Static SDK)
2) Hugging Face Models (Official 200-Episode Benchmark Report & Python Bundle)
3) Hugging Face Datasets (Collected Teleop Demonstration JSON Episodes)
4) All-in-One Dual Deploy (Spaces + Models simultaneously)
"""

import os
import sys
import glob
import json
import zipfile
from pathlib import Path
from typing import Any

try:
    import huggingface_hub
    from huggingface_hub import HfApi, create_repo
except ImportError:
    huggingface_hub = None  # type: ignore
    HfApi = None  # type: ignore
    create_repo = None  # type: ignore

DEFAULT_REPO_NAME = "lerobot-pusht-teleop"

def create_bundle_zip(current_dir: Path) -> str:
    zip_path = current_dir / "lerobot_pusht_bundle.zip"
    include_files = [
        "index.html", "style.css", "pusht_sim.js", "pusht_teleop.py",
        "server.py", "eval_benchmark.py", "eval_info.json",
        "README.md", "README_KR.md", "DOCS_AI_CODING_PROTOCOL.md",
        "DOCS_SYSTEM_ARCHITECTURE.md", "DOCS_DATA_SCHEMA.md",
        "DOCS_MODEL_EVALUATION_AND_HF_DEPLOY.md", "DOCS_UI_DESIGN_SPEC.md", "LICENSE"
    ]
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for f in include_files:
            fp = current_dir / f
            if fp.exists():
                zipf.write(fp, arcname=f)
    print(f"📦 Created verified bundle archive: {zip_path.name}")
    return str(zip_path)

def deploy_space(api: Any, username: str, repo_name: str, token: str, current_dir: Path):
    repo_id = f"{username}/{repo_name}"
    print(f"\n🚀 Deploying to Hugging Face Spaces: {repo_id}...")
    create_repo(repo_id=repo_id, repo_type="space", space_sdk="static", exist_ok=True, token=token)

    files_to_upload = ["index.html", "style.css", "pusht_sim.js", "README.md", "README_KR.md", "eval_info.json", "LICENSE"]
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

    print(f"🎉 Spaces 배포 완료: https://huggingface.co/spaces/{repo_id}")

def deploy_model(api: Any, username: str, repo_name: str, token: str, current_dir: Path):
    repo_id = f"{username}/{repo_name}"
    print(f"\n📦 Deploying to Hugging Face Models: {repo_id}...")
    create_repo(repo_id=repo_id, repo_type="model", exist_ok=True, token=token)

    zip_file = create_bundle_zip(current_dir)
    upload_files = [
        "README.md", "README_KR.md", "eval_info.json", "eval_benchmark.py",
        "pusht_teleop.py", "server.py", "requirements.txt",
        "lerobot_pusht_bundle.zip", "LICENSE"
    ]
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

    print(f"🎉 Models 배포 완료: https://huggingface.co/models/{repo_id}")

def deploy():
    print("=" * 68)
    print("🤖 HWIHWA LAB - LeRobot 2D PushT Universal Hugging Face Deployment")
    print("=" * 68)

    token = os.environ.get("HF_TOKEN") or (huggingface_hub.get_token() if huggingface_hub else None)
    if not token:
        print("\n🔑 Hugging Face Write Token이 필요합니다.")
        print("토큰 발급/확인: https://huggingface.co/settings/tokens")
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

    print(f"\n[배포 옵션 선택 - 기본 레포 ID: {DEFAULT_REPO_NAME}]")
    print("1) 🌟 Spaces 배포   (웹 브라우저 실시간 라이브 시뮬레이터 호스팅)")
    print("2) 🤖 Models 배포   (200회 실측 벤치마크 리포트 & 파이썬 번들 등록)")
    print("3) 👑 All-in-One    (Spaces + Models 동시 배포 - [추천])")
    print("4) 📦 Datasets 배포 (수집된 텔레옵 에피소드 JSON 데이터셋 업로드)")
    choice = input("\n선택 번호 (1/2/3/4, 기본값: 3): ").strip() or "3"

    repo_name = input(f"레포지토리 이름 [기본값: {DEFAULT_REPO_NAME}]: ").strip() or DEFAULT_REPO_NAME
    current_dir = Path(__file__).parent

    try:
        if choice == "1":
            deploy_space(api, username, repo_name, token, current_dir)
        elif choice == "2":
            deploy_model(api, username, repo_name, token, current_dir)
        elif choice == "3":
            deploy_space(api, username, repo_name, token, current_dir)
            deploy_model(api, username, repo_name, token, current_dir)
            print("\n" + "★" * 68)
            print(f"👑 All-in-One Dual Deployment Finished Successfully!")
            print(f"  • 🌟 Live Spaces : https://huggingface.co/spaces/{username}/{repo_name}")
            print(f"  • 🤖 Models Card : https://huggingface.co/models/{username}/{repo_name}")
            print("★" * 68)
        elif choice == "4":
            repo_id = f"{username}/{repo_name}-dataset"
            print(f"\n📦 Creating Dataset Repo: {repo_id}...")
            create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True, token=token)
            json_files = glob.glob(str(current_dir / "pusht_teleop_data_*.json")) + glob.glob(str(current_dir / "lerobot_pusht_dataset_*.json"))
            if not json_files:
                print("⚠️ 로컬에 수집된 JSON 데이터셋 파일이 없습니다. 시뮬레이터에서 먼저 녹화해 주세요.")
            else:
                for jf in json_files:
                    fn = os.path.basename(jf)
                    api.upload_file(path_or_fileobj=jf, path_in_repo=fn, repo_id=repo_id, repo_type="dataset", token=token)
                    print(f"  ✓ {fn} 데이터셋 업로드 완료")
            print(f"🎉 Dataset 업로드 완료: https://huggingface.co/datasets/{repo_id}")

    except Exception as e:
        print(f"\n❌ 배포 중 오류 발생: {e}")

    print("\n" + "=" * 68)
    print("🏁 Deployment Pipeline Finished!")
    print("=" * 68)

if __name__ == "__main__":
    deploy()
