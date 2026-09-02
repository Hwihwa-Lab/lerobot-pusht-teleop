# -*- coding: utf-8 -*-
"""
LeRobot 2D PushT Teleop Simulator - Standalone Pygame Dashboard (Pro Ultimate Edition)
100% Visual, Text & Functional Parity with Web Dashboard:
- Window Title: LeRobot 2D PushT Teleop Simulator - HWIHWA LAB
- Header: LeRobot 2D PushT Teleop Simulator (Main) + Real-time Mouse Teleoperation & Demonstration Data Collector | HWIHWA LAB (Sub)
- Full Keyboard Controls: [Space] Pause | [M] AI Autopilot | [R] Reset | [S] Record | [Q/ESC] Exit
- RL Rewards Telemetry: Step Reward & Cumulative Return
- Mode Indicator: MODE: TELEOP (Press 'M') vs MODE: AI AUTOPILOT
"""

import sys
import math
import time
import json
import pygame
import pygame.gfxdraw

# Window & Layout Geometry (Wide & Large Edition)
WINDOW_WIDTH = 1360
WINDOW_HEIGHT = 760
CANVAS_SIZE = 580
SIM_WORLD = 512
SCALE = CANVAS_SIZE / SIM_WORLD
FPS = 60

# Cyberpunk Lab Color Palette (High-Contrast Vivid Dark Tokens)
COLOR_BG = (10, 13, 20)
COLOR_HEADER_BG = (13, 18, 30)
COLOR_CARD = (18, 24, 38)
COLOR_CARD_SUB = (13, 18, 29)
COLOR_BORDER = (80, 115, 165)
COLOR_CYAN = (0, 242, 254)
COLOR_CYAN_LIGHT = (140, 245, 255)
COLOR_BLUE = (79, 172, 254)
COLOR_GREEN = (0, 230, 118)
COLOR_PURPLE = (192, 132, 252)
COLOR_RED = (255, 75, 120)
COLOR_TEXT_MAIN = (255, 255, 255)
COLOR_TEXT_MUTED = (175, 195, 220)       # Bright Crisp Silver-Blue
COLOR_TEXT_SUBTITLE = (145, 190, 225)    # Luminous Lab Subtitle
COLOR_TEXT_GUIDE = (225, 235, 248)       # Super Clear Ice-White for Guides

# Helper: Anti-Aliased Shapes
def draw_aa_circle(surface, color, center, radius):
    x, y = int(center[0]), int(center[1])
    r = int(radius)
    if r <= 0: return
    pygame.gfxdraw.aacircle(surface, x, y, r, color)
    pygame.gfxdraw.filled_circle(surface, x, y, r, color)

def draw_aa_polygon(surface, fill_color, border_color, points):
    int_points = [(int(p[0]), int(p[1])) for p in points]
    if len(int_points) < 3: return
    pygame.gfxdraw.filled_polygon(surface, int_points, fill_color)
    pygame.gfxdraw.aapolygon(surface, int_points, border_color)

def draw_aa_rounded_rect(surface, bg_color, border_color, rect, radius=8):
    r = pygame.Rect(rect)
    pygame.draw.rect(surface, bg_color, r, border_radius=radius)
    if border_color:
        pygame.draw.rect(surface, border_color, r, width=1, border_radius=radius)

class DotButton:
    def __init__(self, rect, text, dot_color, bg_color, border_color, text_color):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.dot_color = dot_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.text_color = text_color
        self.is_hovered = False

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def draw(self, surface, font):
        bg = (min(255, self.bg_color[0] + 25), min(255, self.bg_color[1] + 25), min(255, self.bg_color[2] + 25)) if self.is_hovered else self.bg_color
        draw_aa_rounded_rect(surface, bg, self.border_color, self.rect, radius=8)
        
        txt_surf = font.render(self.text, True, self.text_color)
        total_w = 8 + 8 + txt_surf.get_width()
        start_x = self.rect.centerx - total_w // 2
        
        draw_aa_circle(surface, self.dot_color, (start_x + 4, self.rect.centery), 3.5)
        surface.blit(txt_surf, (start_x + 16, self.rect.centery - txt_surf.get_height() // 2))

class PushTPygameDashboard:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF)
        pygame.display.set_caption("LeRobot 2D PushT Teleop Simulator - HWIHWA LAB")
        self.clock = pygame.time.Clock()

        # Large & Crisp Typography Fonts Chain
        font_family = "Segoe UI, Inter, Helvetica, Arial"
        self.font_title = pygame.font.SysFont(font_family, 22, bold=True)
        self.font_subtitle = pygame.font.SysFont(font_family, 14)
        self.font_badge = pygame.font.SysFont(font_family, 12, bold=True)
        self.font_main = pygame.font.SysFont(font_family, 15, bold=True)
        self.font_metric = pygame.font.SysFont("Segoe UI, Arial", 28, bold=True)
        self.font_small = pygame.font.SysFont(font_family, 13, bold=True)
        self.font_guide = pygame.font.SysFont(font_family, 13)
        self.font_mono = pygame.font.SysFont("Consolas, Courier New", 12)

        # Simulation Physics State
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
        self.top_bar = {"w": 150.0, "h": 40.0, "ox": 0.0, "oy": -35.0}
        self.stem_bar = {"w": 40.0, "h": 110.0, "ox": 0.0, "oy": 40.0}

        # Goal
        self.goal_x = 256.0
        self.goal_y = 256.0
        self.goal_angle = 0.0

        # Records, RL Rewards & Telemetry
        self.active_steps = 0
        self.coverage = 0.0
        self.peak_coverage = 0.0
        self.current_reward = 0.0
        self.cumulative_return = 0.0
        self.success = False
        self.is_recording = False
        self.is_ai_autopilot = False
        self.is_paused = False
        self.current_episode = []
        self.episodes = []
        self.agent_trail = []
        self.coverage_history = []

        # Action Buttons (1 Row Guaranteed - 4-Col Grid)
        btn_y = 698
        btn_w = 138
        gap = 10
        self.btn_reset = DotButton((24, btn_y, btn_w, 42), "Reset", (148, 163, 184), (30, 41, 59), COLOR_BORDER, COLOR_TEXT_MAIN)
        self.btn_record = DotButton((24 + (btn_w + gap), btn_y, btn_w, 42), "Record", COLOR_RED, (45, 20, 30), COLOR_RED, COLOR_RED)
        self.btn_ai = DotButton((24 + (btn_w + gap) * 2, btn_y, btn_w, 42), "Autopilot", COLOR_PURPLE, (35, 25, 55), COLOR_PURPLE, (216, 180, 254))
        self.btn_save = DotButton((24 + (btn_w + gap) * 3, btn_y, btn_w, 42), "Export", COLOR_CYAN, (10, 32, 48), COLOR_CYAN, COLOR_CYAN)
        self.buttons = [self.btn_reset, self.btn_record, self.btn_ai, self.btn_save]

    def reset(self):
        self.active_steps = 0
        self.peak_coverage = 0.0
        self.cumulative_return = 0.0
        self.current_reward = 0.0
        self.agent_x, self.agent_y = 256.0, 100.0
        self.agent_vx, self.agent_vy = 0.0, 0.0
        self.target_x, self.target_y = 256.0, 100.0
        self.block_x, self.block_y = 256.0, 320.0
        self.block_angle = 0.4
        self.block_vx, self.block_vy, self.block_omega = 0.0, 0.0, 0.0
        self.coverage = 0.0
        self.success = False
        self.agent_trail.clear()

    def update_physics(self, mouse_canvas_x, mouse_canvas_y):
        if self.is_paused:
            return

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
        else:
            if mouse_canvas_x is not None:
                self.target_x = max(10.0, min(SIM_WORLD - 10.0, mouse_canvas_x))
                self.target_y = max(10.0, min(SIM_WORLD - 10.0, mouse_canvas_y))

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
        self.agent_x = max(self.agent_radius, min(SIM_WORLD - self.agent_radius, self.agent_x))
        self.agent_y = max(self.agent_radius, min(SIM_WORLD - self.agent_radius, self.agent_y))

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

        margin = 30.0
        self.block_x = max(margin, min(SIM_WORLD - margin, self.block_x))
        self.block_y = max(margin, min(SIM_WORLD - margin, self.block_y))

        # 4. Coverage & RL Reward Calculation
        dx = self.block_x - self.goal_x
        dy = self.block_y - self.goal_y
        dist = math.hypot(dx, dy)
        diff_angle = abs((self.block_angle - self.goal_angle) % (math.pi * 2))
        if diff_angle > math.pi:
            diff_angle = math.pi * 2 - diff_angle

        pos_score = max(0.0, 1.0 - dist / 140.0)
        rot_score = max(0.0, 1.0 - diff_angle / 1.2)
        self.coverage = min(1.0, max(0.0, (pos_score * 0.65 + rot_score * 0.35) * (1.0 if pos_score > 0.3 else pos_score * 2.0)))
        self.peak_coverage = max(self.peak_coverage, self.coverage)
        self.success = (self.coverage >= 0.90)

        # RL Step Reward & Return
        dist_to_block = math.hypot(self.agent_x - self.block_x, self.agent_y - self.block_y)
        self.current_reward = max(-0.1, (self.coverage * 1.0) - (dist_to_block / 1000.0))

        # Active frame count & cumulative return
        if self.is_recording or self.is_ai_autopilot or speed > 0.5:
            self.active_steps = (self.active_steps + 1) % 501
            self.cumulative_return += self.current_reward

        # 5. Recording
        if self.is_recording:
            self.current_episode.append({
                "step": self.active_steps,
                "agent": [round(self.agent_x, 1), round(self.agent_y, 1)],
                "block": [round(self.block_x, 1), round(self.block_y, 1), round(self.block_angle, 3)],
                "coverage": round(self.coverage, 3),
                "reward": round(self.current_reward, 4)
            })

        if self.active_steps % 2 == 0:
            self.agent_trail.append((self.agent_x * SCALE, self.agent_y * SCALE))
            if len(self.agent_trail) > 40:
                self.agent_trail.pop(0)
            self.coverage_history.append(self.coverage)
            if len(self.coverage_history) > 100:
                self.coverage_history.pop(0)

    def draw_t_block(self, surface, x, y, angle, fill_color, border_color):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        for rect in [self.top_bar, self.stem_bar]:
            hw = (rect["w"] * SCALE) / 2.0
            hh = (rect["h"] * SCALE) / 2.0
            corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
            poly = []
            for cx, cy in corners:
                lx = rect["ox"] * SCALE + cx
                ly = rect["oy"] * SCALE + cy
                wx = x * SCALE + lx * cos_a - ly * sin_a
                wy = y * SCALE + lx * sin_a + ly * cos_a
                poly.append((wx, wy))

            draw_aa_polygon(surface, fill_color, border_color, poly)

    def run(self):
        running = True
        canvas_rect = pygame.Rect(24, 70, CANVAS_SIZE, 615)

        while running:
            mouse_pos = pygame.mouse.get_pos()
            for b in self.buttons:
                b.check_hover(mouse_pos)

            mouse_canvas_x = None
            mouse_canvas_y = None
            if canvas_rect.collidepoint(mouse_pos):
                mouse_canvas_x = (mouse_pos[0] - canvas_rect.left) / SCALE
                mouse_canvas_y = (mouse_pos[1] - canvas_rect.top) / SCALE

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.is_paused = not self.is_paused
                    elif event.key == pygame.K_m:
                        self.is_ai_autopilot = not self.is_ai_autopilot
                        self.btn_ai.text = "Autopilot ON" if self.is_ai_autopilot else "Autopilot"
                        self.btn_ai.dot_color = COLOR_GREEN if self.is_ai_autopilot else COLOR_PURPLE
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_s or event.key == pygame.K_RETURN:
                        self.is_recording = not self.is_recording
                        if self.is_recording:
                            self.current_episode = []
                            self.btn_record.text = "Stop"
                            self.btn_record.bg_color = COLOR_RED
                            self.btn_record.text_color = (255, 255, 255)
                            self.btn_record.dot_color = (255, 255, 255)
                        else:
                            self.btn_record.text = "Record"
                            self.btn_record.bg_color = (45, 20, 30)
                            self.btn_record.text_color = COLOR_RED
                            self.btn_record.dot_color = COLOR_RED
                            if len(self.current_episode) > 20:
                                ep = {
                                    "id": len(self.episodes) + 1,
                                    "length": len(self.current_episode),
                                    "maxCoverage": max(f["coverage"] for f in self.current_episode),
                                    "success": any(f["coverage"] >= 0.90 for f in self.current_episode),
                                    "time": time.strftime("%H:%M:%S")
                                }
                                self.episodes.insert(0, ep)
                    elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.btn_reset.rect.collidepoint(mouse_pos):
                        self.reset()
                    elif self.btn_record.rect.collidepoint(mouse_pos):
                        self.is_recording = not self.is_recording
                        if self.is_recording:
                            self.current_episode = []
                            self.btn_record.text = "Stop"
                            self.btn_record.bg_color = COLOR_RED
                            self.btn_record.text_color = (255, 255, 255)
                            self.btn_record.dot_color = (255, 255, 255)
                        else:
                            self.btn_record.text = "Record"
                            self.btn_record.bg_color = (45, 20, 30)
                            self.btn_record.text_color = COLOR_RED
                            self.btn_record.dot_color = COLOR_RED
                            if len(self.current_episode) > 20:
                                ep = {
                                    "id": len(self.episodes) + 1,
                                    "length": len(self.current_episode),
                                    "maxCoverage": max(f["coverage"] for f in self.current_episode),
                                    "success": any(f["coverage"] >= 0.90 for f in self.current_episode),
                                    "time": time.strftime("%H:%M:%S")
                                }
                                self.episodes.insert(0, ep)
                    elif self.btn_ai.rect.collidepoint(mouse_pos):
                        self.is_ai_autopilot = not self.is_ai_autopilot
                        self.btn_ai.text = "Autopilot ON" if self.is_ai_autopilot else "Autopilot"
                        self.btn_ai.dot_color = COLOR_GREEN if self.is_ai_autopilot else COLOR_PURPLE
                    elif self.btn_save.rect.collidepoint(mouse_pos):
                        fn = f"lerobot_pusht_dataset_{int(time.time())}.json"
                        with open(fn, "w", encoding="utf-8") as f:
                            json.dump(self.episodes, f, indent=2)
                        print(f"[*] Saved dataset to {fn}")

            self.update_physics(mouse_canvas_x, mouse_canvas_y)

            # ================= RENDER =================
            self.screen.fill(COLOR_BG)

            # Top Header Bar
            header_rect = pygame.Rect(0, 0, WINDOW_WIDTH, 58)
            pygame.draw.rect(self.screen, COLOR_HEADER_BG, header_rect)
            pygame.draw.line(self.screen, COLOR_BORDER, (0, 58), (WINDOW_WIDTH, 58), 1)

            # Robot Brand Icon (🤖 Signature Robotics Mascot)
            draw_aa_rounded_rect(self.screen, (0, 210, 255), (0, 242, 254), (24, 11, 36, 36), radius=9)
            # Robot Face Details (Dark Cyber Visor & Eyes)
            pygame.draw.rect(self.screen, (10, 15, 25), (30, 21, 24, 16), border_radius=4)
            # Robot Eyes (Bright Cyan Neon Lenses)
            draw_aa_circle(self.screen, (0, 242, 254), (36, 29), 2.5)
            draw_aa_circle(self.screen, (0, 242, 254), (48, 29), 2.5)
            # Antenna
            pygame.draw.line(self.screen, (10, 15, 25), (42, 15), (42, 21), 2)
            draw_aa_circle(self.screen, (0, 242, 254), (42, 15), 2.0)

            # Main Title (22pt Crystal White) & Subtitle (14pt Luminous Lab Blue)
            txt_title = self.font_title.render("LeRobot 2D PushT Teleop Simulator", True, COLOR_TEXT_MAIN)
            self.screen.blit(txt_title, (72, 7))
            txt_subtitle = self.font_subtitle.render("Real-time Mouse Teleoperation & Demonstration Data Collector | HWIHWA LAB", True, COLOR_TEXT_SUBTITLE)
            self.screen.blit(txt_subtitle, (72, 33))

            # Badge: v2.0 Live & Status
            badge_r = pygame.Rect(WINDOW_WIDTH - 290, 14, 266, 30)
            draw_aa_rounded_rect(self.screen, (10, 24, 38), (0, 230, 118), badge_r, radius=15)
            draw_aa_circle(self.screen, COLOR_GREEN, (WINDOW_WIDTH - 275, 29), 4.5)
            txt_status = self.font_badge.render("60 FPS Physics Engine Active", True, COLOR_GREEN)
            self.screen.blit(txt_status, (WINDOW_WIDTH - 262, 21))

            # 1. Left Canvas Card (580x615)
            draw_aa_rounded_rect(self.screen, (13, 17, 26), COLOR_BORDER, canvas_rect, radius=12)

            # Canvas Grid
            grid_size = int(32 * SCALE)
            for gx in range(canvas_rect.left, canvas_rect.right, grid_size):
                pygame.draw.line(self.screen, (25, 35, 50), (gx, canvas_rect.top), (gx, canvas_rect.bottom))
            for gy in range(canvas_rect.top, canvas_rect.bottom, grid_size):
                pygame.draw.line(self.screen, (25, 35, 50), (canvas_rect.left, gy), (canvas_rect.right, gy))

            # Canvas Goal
            canvas_surf = self.screen.subsurface(canvas_rect)
            goal_color = (0, 70, 80) if not self.success else (0, 100, 60)
            goal_border = COLOR_CYAN if not self.success else COLOR_GREEN
            self.draw_t_block(canvas_surf, self.goal_x, self.goal_y, self.goal_angle, goal_color, goal_border)

            # Canvas Trail (Smooth Line)
            if len(self.agent_trail) > 1:
                trail_color = COLOR_RED if self.is_recording else COLOR_CYAN
                pygame.draw.lines(canvas_surf, trail_color, False, self.agent_trail, 2)

            # Canvas Active T-Block
            block_border = COLOR_GREEN if self.success else (56, 189, 248)
            self.draw_t_block(canvas_surf, self.block_x, self.block_y, self.block_angle, (30, 41, 59), block_border)

            # Target Line & Cursor
            ax = int(self.agent_x * SCALE)
            ay = int(self.agent_y * SCALE)
            tx = int(self.target_x * SCALE)
            ty = int(self.target_y * SCALE)
            pygame.draw.line(canvas_surf, (180, 190, 205), (ax, ay), (tx, ty), 1)
            draw_aa_circle(canvas_surf, COLOR_CYAN, (tx, ty), 4)

            # Agent Robot (Smooth Core)
            agent_bg = COLOR_RED if self.is_recording else COLOR_BLUE
            draw_aa_circle(canvas_surf, agent_bg, (ax, ay), int(self.agent_radius * SCALE))
            draw_aa_circle(canvas_surf, (255, 255, 255), (ax, ay), 4)

            # Canvas Overlay Pills (Left: Mode Indicator, Right: Goal)
            mode_txt = "MODE: AI AUTOPILOT (Press 'M')" if self.is_ai_autopilot else "MODE: TELEOP (Press 'M')"
            mode_color = COLOR_PURPLE if self.is_ai_autopilot else COLOR_GREEN
            txt_mode = self.font_small.render(mode_txt, True, mode_color)
            mw = txt_mode.get_width() + 20
            draw_aa_rounded_rect(canvas_surf, (10, 13, 20), mode_color, (14, 14, mw, 30), radius=6)
            canvas_surf.blit(txt_mode, (24, 20))

            txt_goal = self.font_small.render("Goal: 256, 256 (0°)", True, COLOR_TEXT_MUTED)
            gw = txt_goal.get_width() + 20
            draw_aa_rounded_rect(canvas_surf, (10, 13, 20), COLOR_BORDER, (CANVAS_SIZE - gw - 14, 14, gw, 30), radius=6)
            canvas_surf.blit(txt_goal, (CANVAS_SIZE - gw - 4, 20))

            # Pause Overlay
            if self.is_paused:
                pause_surf = pygame.Surface((CANVAS_SIZE, 615), pygame.SRCALPHA)
                pause_surf.fill((10, 13, 20, 200))
                
                pbox_r = pygame.Rect(CANVAS_SIZE // 2 - 160, 260, 320, 90)
                draw_aa_rounded_rect(pause_surf, (18, 24, 38), COLOR_CYAN, pbox_r, radius=12)
                
                ptxt1 = self.font_main.render("⏸️  SIMULATION PAUSED", True, (255, 255, 255))
                ptxt2 = self.font_small.render("Press [Space] to Resume Simulation", True, COLOR_CYAN)
                pause_surf.blit(ptxt1, (CANVAS_SIZE // 2 - ptxt1.get_width() // 2, 280))
                pause_surf.blit(ptxt2, (CANVAS_SIZE // 2 - ptxt2.get_width() // 2, 312))
                canvas_surf.blit(pause_surf, (0, 0))

            # Draw Toolbar Buttons
            for b in self.buttons:
                b.draw(self.screen, self.font_main)

            # ================= 2. Right Dashboard Panel =================
            right_x = 635
            right_w = 700

            # 4 High-Tech HUD Metric Cards with RL Rewards (2x2 Grid)
            agent_spd = math.hypot(self.agent_vx, self.agent_vy)
            blk_deg = (self.block_angle * 180 / math.pi) % 360
            cov_pct = int(self.coverage * 100)

            hud_cards = [
                ("GOAL COVERAGE", f"{cov_pct}%", f"Peak {int(self.peak_coverage*100)}%", COLOR_CYAN, f"Reward: {self.current_reward:+.4f}", "progress"),
                ("EPISODE FRAMES", f"{self.active_steps} / 500", "60 Hz", COLOR_TEXT_MAIN, f"Return: {self.cumulative_return:.2f}", "frame_bar"),
                ("ROBOT END-EFFECTOR", f"({int(self.agent_x)}, {int(self.agent_y)})", "PD Spring", COLOR_PURPLE, f"Speed: {agent_spd:.1f} px/f", None),
                ("T-BLOCK POSE", f"({int(self.block_x)}, {int(self.block_y)})", "Rigid 2D", COLOR_GREEN, f"Angle: {blk_deg:.1f}°", None)
            ]
            
            for i, (label, val, badge_txt, col, subtext, bar_type) in enumerate(hud_cards):
                cx = right_x + (i % 2) * 355
                cy = 70 + (i // 2) * 95
                card_r = pygame.Rect(cx, cy, 345, 85)
                
                # Success border glow on Card 0
                border_col = COLOR_GREEN if (i == 0 and self.success) else COLOR_BORDER
                draw_aa_rounded_rect(self.screen, COLOR_CARD, border_col, card_r, radius=10)

                # Header: Label (13pt Bold) + Badge (12pt)
                lbl_s = self.font_small.render(label, True, COLOR_TEXT_MUTED)
                self.screen.blit(lbl_s, (cx + 14, cy + 10))

                badge_col = COLOR_GREEN if "Hz" in badge_txt else (190, 210, 235)
                badge_s = self.font_badge.render(badge_txt, True, badge_col)
                bw = badge_s.get_width() + 12
                draw_aa_rounded_rect(self.screen, (25, 38, 56), (60, 90, 130), (cx + 345 - 14 - bw, cy + 9, bw, 22), radius=4)
                self.screen.blit(badge_s, (cx + 345 - 14 - bw + 6, cy + 12))

                # Large Metric Value (28pt)
                val_s = self.font_metric.render(val, True, col)
                self.screen.blit(val_s, (cx + 14, cy + 28))

                # Subtext (Reward / Return / Speed / Angle)
                sub_s = self.font_mono.render(subtext, True, COLOR_TEXT_MUTED)
                self.screen.blit(sub_s, (cx + 14, cy + 62))

                # Extra Mini Progress Bars for Card 0 & 1
                if bar_type == "progress":
                    pb_r = pygame.Rect(cx + 160, cy + 68, 170, 4)
                    draw_aa_rounded_rect(self.screen, (30, 41, 59), None, pb_r, radius=2)
                    fill_w = int(170 * self.coverage)
                    if fill_w > 0:
                        draw_aa_rounded_rect(self.screen, COLOR_CYAN if not self.success else COLOR_GREEN, None, (cx + 160, cy + 68, fill_w, 4), radius=2)
                elif bar_type == "frame_bar":
                    pb_r = pygame.Rect(cx + 160, cy + 68, 170, 4)
                    draw_aa_rounded_rect(self.screen, (30, 41, 59), None, pb_r, radius=2)
                    fill_w = int(170 * (self.active_steps / 500.0))
                    if fill_w > 0:
                        draw_aa_rounded_rect(self.screen, COLOR_PURPLE, None, (cx + 160, cy + 68, fill_w, 4), radius=2)

            # Realtime Coverage Graph Card with 90% Threshold Guide & Gradient Area
            chart_r = pygame.Rect(right_x, 270, right_w, 130)
            draw_aa_rounded_rect(self.screen, COLOR_CARD, COLOR_BORDER, chart_r, radius=10)
            chart_lbl = self.font_small.render("Realtime Coverage Trajectory Curve", True, COLOR_TEXT_MUTED)
            self.screen.blit(chart_lbl, (right_x + 14, 278))

            target_lbl = self.font_badge.render("Target 90% Success Line", True, COLOR_GREEN)
            draw_aa_circle(self.screen, COLOR_GREEN, (right_x + right_w - 170, 287), 3.5)
            self.screen.blit(target_lbl, (right_x + right_w - 160, 280))

            # 90% Line (Dashed appearance)
            gy_base = 388
            gh = 80
            line_90_y = int(gy_base - 0.90 * gh)
            for dx in range(right_x + 20, right_x + right_w - 20, 10):
                pygame.draw.line(self.screen, (0, 160, 80), (dx, line_90_y), (dx + 5, line_90_y), 1)

            if len(self.coverage_history) > 1:
                gx_start = right_x + 20
                gw = right_w - 40
                step_x = gw / max(1, len(self.coverage_history) - 1)
                points = []
                poly_points = [(gx_start, gy_base)]
                for idx, c in enumerate(self.coverage_history):
                    px = int(gx_start + idx * step_x)
                    py = int(gy_base - c * gh)
                    points.append((px, py))
                    poly_points.append((px, py))
                poly_points.append((gx_start + (len(self.coverage_history) - 1) * step_x, gy_base))

                if len(points) > 1:
                    # Semi-transparent Gradient Area Fill
                    area_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                    pygame.draw.polygon(area_surf, (0, 242, 254, 55), poly_points)
                    self.screen.blit(area_surf, (0, 0))

                    # Neon Curve Line
                    pygame.draw.lines(self.screen, COLOR_CYAN, False, points, 2)
                    # Live Pulse Head Dot
                    draw_aa_circle(self.screen, COLOR_CYAN, points[-1], 4.5)

            # Controls & Keyboard Hotkeys Guide Box (100% Matched with Web)
            guide_r = pygame.Rect(right_x, 412, right_w, 98)
            draw_aa_rounded_rect(self.screen, (13, 26, 44), (0, 180, 210), guide_r, radius=10)
            
            # Header with Hotkeys Badges (100% Matched with Web)
            g1 = self.font_small.render("🎮 TELEOPERATION & KEYBOARD CONTROLS:", True, COLOR_CYAN)
            hotkeys_txt = self.font_mono.render("[Space] Pause | [M] AI Autopilot | [R] Reset | [S] Record", True, COLOR_CYAN_LIGHT)
            self.screen.blit(g1, (right_x + 14, 418))
            self.screen.blit(hotkeys_txt, (right_x + right_w - hotkeys_txt.get_width() - 14, 420))

            g2 = self.font_guide.render("1. Move mouse on canvas to teleoperate circle robot with dynamic spring force.", True, COLOR_TEXT_GUIDE)
            g3 = self.font_guide.render("2. Push T-block into translucent target goal zone (≥90% for success).", True, COLOR_TEXT_GUIDE)
            
            # Line 3 with Uniform Cyan Highlighted Tokens: [• Record], [S], [• Export]
            l3_p1 = self.font_guide.render("3. Click ", True, COLOR_TEXT_GUIDE)
            l3_rec = self.font_small.render("[• Record]", True, COLOR_CYAN)
            l3_p2 = self.font_guide.render(" or press ", True, COLOR_TEXT_GUIDE)
            l3_s = self.font_small.render("[S]", True, COLOR_CYAN)
            l3_p3 = self.font_guide.render(" to collect trajectories, and ", True, COLOR_TEXT_GUIDE)
            l3_exp = self.font_small.render("[• Export]", True, COLOR_CYAN)
            l3_p4 = self.font_guide.render(" to save!", True, COLOR_TEXT_GUIDE)

            # Line 4 with Uniform Cyan Highlighted Tokens: [M], [• Autopilot]
            l4_p1 = self.font_guide.render("4. Press ", True, COLOR_TEXT_GUIDE)
            l4_m = self.font_small.render("[M]", True, COLOR_CYAN)
            l4_p2 = self.font_guide.render(" or click ", True, COLOR_TEXT_GUIDE)
            l4_ai = self.font_small.render("[• Autopilot]", True, COLOR_CYAN)
            l4_p3 = self.font_guide.render(" to toggle AI Expert Policy demonstration.", True, COLOR_TEXT_GUIDE)

            self.screen.blit(g2, (right_x + 14, 438))
            self.screen.blit(g3, (right_x + 14, 456))
            
            cur_x = right_x + 14
            self.screen.blit(l3_p1, (cur_x, 474)); cur_x += l3_p1.get_width()
            self.screen.blit(l3_rec, (cur_x, 473)); cur_x += l3_rec.get_width()
            self.screen.blit(l3_p2, (cur_x, 474)); cur_x += l3_p2.get_width()
            self.screen.blit(l3_s, (cur_x, 473)); cur_x += l3_s.get_width()
            self.screen.blit(l3_p3, (cur_x, 474)); cur_x += l3_p3.get_width()
            self.screen.blit(l3_exp, (cur_x, 473)); cur_x += l3_exp.get_width()
            self.screen.blit(l3_p4, (cur_x, 474))

            cur4_x = right_x + 14
            self.screen.blit(l4_p1, (cur4_x, 491)); cur4_x += l4_p1.get_width()
            self.screen.blit(l4_m, (cur4_x, 490)); cur4_x += l4_m.get_width()
            self.screen.blit(l4_p2, (cur4_x, 491)); cur4_x += l4_p2.get_width()
            self.screen.blit(l4_ai, (cur4_x, 490)); cur4_x += l4_ai.get_width()
            self.screen.blit(l4_p3, (cur4_x, 491))

            # Episode Table Section (Bright Crisp Text)
            table_r = pygame.Rect(right_x, 520, right_w, 220)
            draw_aa_rounded_rect(self.screen, COLOR_CARD, COLOR_BORDER, table_r, radius=10)
            
            # Table Header Bar (Dot + Title)
            draw_aa_circle(self.screen, COLOR_CYAN, (right_x + 20, 534), 3.5)
            tbl_title = self.font_small.render("Collected Demonstration Episodes", True, COLOR_TEXT_MAIN)
            self.screen.blit(tbl_title, (right_x + 30, 526))

            # Table Header Columns
            th_y = 552
            draw_aa_rounded_rect(self.screen, (28, 38, 58), (50, 75, 110), (right_x + 10, th_y, right_w - 20, 28), radius=4)
            self.screen.blit(self.font_badge.render("EP ID", True, COLOR_TEXT_MUTED), (right_x + 20, th_y + 6))
            self.screen.blit(self.font_badge.render("FRAMES", True, COLOR_TEXT_MUTED), (right_x + 130, th_y + 6))
            self.screen.blit(self.font_badge.render("PEAK COVERAGE", True, COLOR_TEXT_MUTED), (right_x + 270, th_y + 6))
            self.screen.blit(self.font_badge.render("STATUS", True, COLOR_TEXT_MUTED), (right_x + 450, th_y + 6))
            self.screen.blit(self.font_badge.render("ACTION", True, COLOR_TEXT_MUTED), (right_x + 590, th_y + 6))

            # Table Rows
            if not self.episodes:
                no_data = self.font_guide.render("No demonstration episodes recorded yet. Click [• Record] to collect your first trajectory!", True, COLOR_TEXT_MUTED)
                self.screen.blit(no_data, (right_x + 50, 610))
            else:
                for idx, ep in enumerate(self.episodes[:3]):
                    tr_y = 586 + idx * 34
                    self.screen.blit(self.font_main.render(f"#{ep['id']}", True, COLOR_TEXT_MAIN), (right_x + 20, tr_y))
                    self.screen.blit(self.font_main.render(f"{ep['length']} frames", True, COLOR_TEXT_MAIN), (right_x + 130, tr_y))
                    self.screen.blit(self.font_main.render(f"{int(ep['maxCoverage']*100)}%", True, COLOR_CYAN), (right_x + 270, tr_y))
                    status_col = COLOR_GREEN if ep['success'] else COLOR_RED
                    status_str = "SUCCESS" if ep['success'] else "INCOMPLETE"
                    self.screen.blit(self.font_main.render(status_str, True, status_col), (right_x + 450, tr_y))
                    self.screen.blit(self.font_guide.render("📁 Auto-Saved", True, COLOR_CYAN), (right_x + 590, tr_y))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = PushTPygameDashboard()
    app.run()
