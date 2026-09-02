# -*- coding: utf-8 -*-
"""
LeRobot 2D PushT Simulator - FastAPI & WebSocket Real-time Unified Backend
Synchronizes Python 2D Physics, Teleoperation Stream, and Auto Dataset Storage.
"""

import os
import math
import time
import json
import glob
import asyncio
from typing import List, Optional, Dict, Any

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

# Global Constants
WIDTH, HEIGHT = 512, 512
FPS = 60
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Background Physics Loop (60 FPS)
async def physics_loop():
    while True:
        engine.step_physics()
        if manager.active_connections:
            state = engine.get_state()
            await manager.broadcast(state)
        await asyncio.sleep(1.0 / FPS)

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    task = asyncio.create_task(physics_loop())
    print(f"==================================================")
    print(f"🚀 LeRobot 2D PushT Unified FastAPI & WebSocket Server")
    print(f"🌐 Access URL: http://localhost:8000")
    print(f"📡 WebSocket Stream: ws://localhost:8000/ws (60 FPS)")
    print(f"==================================================")
    yield
    task.cancel()

app = FastAPI(
    title="LeRobot PushT Physical AI Unified Control Center",
    version="2.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PushTPhysicsEngine:
    """Server-side Python 2D Physics & Teleoperation Manager"""
    def __init__(self):
        # Agent
        self.agent_x = 256.0
        self.agent_y = 100.0
        self.agent_vx = 0.0
        self.agent_vy = 0.0
        self.target_x = 256.0
        self.target_y = 100.0
        self.agent_radius = 18.0
        self.kp = 0.28
        self.kd = 0.12
        self.max_speed = 16.0

        # T-Block
        self.block_x = 256.0
        self.block_y = 320.0
        self.block_angle = 0.4
        self.block_vx = 0.0
        self.block_vy = 0.0
        self.block_omega = 0.0
        self.friction = 0.88
        self.angular_friction = 0.86

        # Geometry
        self.top_bar = {"w": 150.0, "h": 40.0, "ox": 0.0, "oy": -35.0}
        self.stem_bar = {"w": 40.0, "h": 110.0, "ox": 0.0, "oy": 40.0}

        # Goal
        self.goal_x = 256.0
        self.goal_y = 256.0
        self.goal_angle = 0.0

        # State
        self.step_count = 0
        self.coverage = 0.0
        self.success = False
        self.is_recording = False
        self.is_ai_autopilot = False
        self.ai_timer = 0.0

        # Buffers & Recorded Data
        self.current_episode = []
        self.coverage_history = []
        self.agent_trail = []

    def reset(self):
        self.step_count = 0
        self.agent_x, self.agent_y = 256.0, 100.0
        self.agent_vx, self.agent_vy = 0.0, 0.0
        self.target_x, self.target_y = 256.0, 100.0
        self.block_x, self.block_y = 256.0, 320.0
        self.block_angle = 0.4
        self.block_vx, self.block_vy, self.block_omega = 0.0, 0.0, 0.0
        self.coverage = 0.0
        self.success = False
        self.agent_trail.clear()
        self.coverage_history.clear()

    def update_mouse(self, x: float, y: float):
        if not self.is_ai_autopilot:
            self.target_x = max(10.0, min(WIDTH - 10.0, x))
            self.target_y = max(10.0, min(HEIGHT - 10.0, y))

    def start_recording(self):
        self.is_recording = True
        self.current_episode = []

    def stop_recording(self) -> Optional[Dict[str, Any]]:
        if not self.is_recording:
            return None
        self.is_recording = False
        
        if len(self.current_episode) > 20:
            ep_data = {
                "id": int(time.time() * 1000) % 10000,
                "length": len(self.current_episode),
                "maxCoverage": max(f["coverage"] for f in self.current_episode),
                "success": any(f["coverage"] >= 0.90 for f in self.current_episode),
                "timestamp": time.strftime("%H:%M:%S"),
                "frames": list(self.current_episode)
            }
            # Auto save to local dataset file
            save_fn = os.path.join(DIRECTORY, f"lerobot_pusht_dataset_{int(time.time())}.json")
            try:
                with open(save_fn, "w", encoding="utf-8") as f:
                    json.dump([ep_data], f, indent=2)
                print(f"[Python Engine] Auto-saved {len(self.current_episode)} frames to {os.path.basename(save_fn)}")
            except Exception as e:
                print(f"[Python Engine Error] Failed to save dataset: {e}")
            return ep_data
        return None

    def toggle_ai(self):
        self.is_ai_autopilot = not self.is_ai_autopilot

    def step_physics(self):
        self.step_count += 1

        # AI Autopilot Heuristic
        if self.is_ai_autopilot:
            dx = self.goal_x - self.block_x
            dy = self.goal_y - self.block_y
            dist = math.hypot(dx, dy)
            push_angle = math.atan2(dy, dx)
            desired_x = self.block_x - math.cos(push_angle) * 65.0
            desired_y = self.block_y - math.sin(push_angle) * 65.0
            diff_angle = self.goal_angle - self.block_angle
            if abs(diff_angle) > 0.15 and dist < 120.0:
                rot_sign = 1.0 if diff_angle > 0 else -1.0
                desired_x += -math.sin(self.block_angle) * 45.0 * rot_sign
                desired_y += math.cos(self.block_angle) * 45.0 * rot_sign
            self.target_x += (desired_x - self.target_x) * 0.12
            self.target_y += (desired_y - self.target_y) * 0.12

        # 1. Agent PD Tracking
        err_x = self.target_x - self.agent_x
        err_y = self.target_y - self.agent_y
        self.agent_vx = (self.agent_vx + err_x * self.kp) * (1.0 - self.kd)
        self.agent_vy = (self.agent_vy + err_y * self.kp) * (1.0 - self.kd)

        speed = math.hypot(self.agent_vx, self.agent_vy)
        if speed > self.max_speed:
            self.agent_vx = (self.agent_vx / speed) * self.max_speed
            self.agent_vy = (self.agent_vy / speed) * self.max_speed

        self.agent_x += self.agent_vx
        self.agent_y += self.agent_vy
        self.agent_x = max(self.agent_radius, min(WIDTH - self.agent_radius, self.agent_x))
        self.agent_y = max(self.agent_radius, min(HEIGHT - self.agent_radius, self.agent_y))

        # 2. Collision with T-Block
        cos_a = math.cos(self.block_angle)
        sin_a = math.sin(self.block_angle)

        for rect in [self.top_bar, self.stem_bar]:
            rcx = self.block_x + rect["ox"] * cos_a - rect["oy"] * sin_a
            rcy = self.block_y + rect["ox"] * sin_a + rect["oy"] * cos_a

            rel_x = self.agent_x - rcx
            rel_y = self.agent_y - rcy
            local_x = rel_x * cos_a + rel_y * sin_a
            local_y = -rel_x * sin_a + rel_y * cos_a

            hw = rect["w"] / 2.0
            hh = rect["h"] / 2.0
            clamped_x = max(-hw, min(hw, local_x))
            clamped_y = max(-hh, min(hh, local_y))

            dx = local_x - clamped_x
            dy = local_y - clamped_y
            dist_sq = dx * dx + dy * dy

            if dist_sq < self.agent_radius * self.agent_radius:
                dist = math.sqrt(dist_sq)
                penetration = self.agent_radius - dist
                if dist > 0.0001:
                    nx, ny = dx / dist, dy / dist
                else:
                    nx, ny = 0.0, -1.0
                    penetration = self.agent_radius

                wnx = nx * cos_a - ny * sin_a
                wny = nx * sin_a + ny * cos_a

                self.agent_x += wnx * penetration * 0.4
                self.agent_y += wny * penetration * 0.4
                self.block_vx -= wnx * penetration * 0.55
                self.block_vy -= wny * penetration * 0.55

                contact_x = rcx + clamped_x * cos_a - clamped_y * sin_a
                contact_y = rcy + clamped_x * sin_a + clamped_y * cos_a
                rx = contact_x - self.block_x
                ry = contact_y - self.block_y
                torque = (rx * (-wny) - ry * (-wnx)) * penetration * 0.025
                self.block_omega += torque

        # 3. Integrate Block Physics
        self.block_x += self.block_vx
        self.block_y += self.block_vy
        self.block_angle += self.block_omega
        self.block_vx *= self.friction
        self.block_vy *= self.friction
        self.block_omega *= self.angular_friction

        # Boundary
        margin = 30.0
        self.block_x = max(margin, min(WIDTH - margin, self.block_x))
        self.block_y = max(margin, min(HEIGHT - margin, self.block_y))

        # 4. Coverage (IoU)
        dx = self.block_x - self.goal_x
        dy = self.block_y - self.goal_y
        dist = math.hypot(dx, dy)
        diff_angle = abs((self.block_angle - self.goal_angle) % (math.pi * 2))
        if diff_angle > math.pi:
            diff_angle = math.pi * 2 - diff_angle

        pos_score = max(0.0, 1.0 - dist / 140.0)
        rot_score = max(0.0, 1.0 - diff_angle / 1.2)
        self.coverage = min(1.0, max(0.0, (pos_score * 0.65 + rot_score * 0.35) * (1.0 if pos_score > 0.3 else pos_score * 2.0)))
        self.success = (self.coverage >= 0.90)

        # 5. Recording Frame
        if self.is_recording:
            self.current_episode.append({
                "step": self.step_count,
                "agent": [round(self.agent_x, 1), round(self.agent_y, 1)],
                "block": [round(self.block_x, 1), round(self.block_y, 1), round(self.block_angle, 3)],
                "target": [round(self.target_x, 1), round(self.target_y, 1)],
                "coverage": round(self.coverage, 3),
                "success": self.success
            })

        # Trail & History
        if self.step_count % 2 == 0:
            self.agent_trail.append([round(self.agent_x, 1), round(self.agent_y, 1)])
            if len(self.agent_trail) > 45:
                self.agent_trail.pop(0)
            self.coverage_history.append(round(self.coverage, 3))
            if len(self.coverage_history) > 100:
                self.coverage_history.pop(0)

    def get_state(self) -> Dict[str, Any]:
        return {
            "type": "telemetry",
            "step": self.step_count,
            "agent": [round(self.agent_x, 1), round(self.agent_y, 1)],
            "target": [round(self.target_x, 1), round(self.target_y, 1)],
            "block": [round(self.block_x, 1), round(self.block_y, 1), round(self.block_angle, 3)],
            "goal": [self.goal_x, self.goal_y, self.goal_angle],
            "coverage": round(self.coverage, 3),
            "success": self.success,
            "is_recording": self.is_recording,
            "is_ai_autopilot": self.is_ai_autopilot,
            "trail": self.agent_trail,
            "history": self.coverage_history
        }

engine = PushTPhysicsEngine()

# Static Files
app.mount("/static", StaticFiles(directory=DIRECTORY), name="static")

@app.get("/")
async def get_index():
    return FileResponse(os.path.join(DIRECTORY, "index.html"))

@app.get("/style.css")
async def get_css():
    return FileResponse(os.path.join(DIRECTORY, "style.css"))

@app.get("/pusht_sim.js")
async def get_js():
    return FileResponse(os.path.join(DIRECTORY, "pusht_sim.js"))

@app.get("/api/episodes")
async def get_episodes():
    json_files = glob.glob(os.path.join(DIRECTORY, "lerobot_pusht_dataset_*.json")) + glob.glob(os.path.join(DIRECTORY, "pusht_teleop_data_*.json"))
    episodes = []
    for jf in sorted(json_files, reverse=True):
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    episodes.extend(data)
                elif isinstance(data, dict):
                    episodes.append(data)
        except Exception:
            pass
    return JSONResponse(content={"count": len(episodes), "episodes": episodes})

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            if msg_type == "mouse_move":
                engine.update_mouse(data.get("x", 256.0), data.get("y", 100.0))
            elif msg_type == "reset":
                engine.reset()
            elif msg_type == "record_start":
                engine.start_recording()
            elif msg_type == "record_stop":
                ep = engine.stop_recording()
                if ep:
                    await websocket.send_json({"type": "episode_saved", "episode": ep})
            elif msg_type == "toggle_ai":
                engine.toggle_ai()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"[WebSocket Error] {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
