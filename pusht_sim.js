/**
 * LeRobot 2D PushT Interactive Teleoperation Simulator
 * Hybrid Architecture: WebSocket Python Backend Sync + Zero-Downtime Standalone Fallback
 */

class PushTHybridSimulator {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    
    // Virtual Dimensions (512x512)
    this.simWidth = 512;
    this.simHeight = 512;
    this.scale = this.canvas.width / this.simWidth;

    // State Variables (Synced from Python or Fallback JS Engine)
    this.agent = { x: 256, y: 100, targetX: 256, targetY: 100, radius: 18 };
    this.tBlock = {
      x: 256, y: 320, angle: 0.4,
      topBar: { w: 150, h: 40, ox: 0, oy: -35 },
      stemBar: { w: 40, h: 110, ox: 0, oy: 40 }
    };
    this.goal = { x: 256, y: 256, angle: 0.0 };

    this.stepCount = 0;
    this.coverage = 0.0;
    this.success = false;
    this.isRecording = false;
    this.isAiAutopilot = false;
    this.agentTrail = [];
    this.coverageHistory = [];
    this.episodes = [];

    // Mode: Backend-driven or Standalone
    this.backendConnected = false;
    this.ws = null;

    // Initialize
    this.initWebSocket();
    this.initEventListeners();
    this.fetchSavedEpisodes();
  }

  initWebSocket() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.backendConnected = true;
        this.updateHeaderStatus("🟢 Python FastAPI Backend Connected (60Hz)", true);
        console.log("[PushT] WebSocket Connected to Python Backend!");
      };

      this.ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === "telemetry") {
          this.stepCount = msg.step;
          this.agent.x = msg.agent[0];
          this.agent.y = msg.agent[1];
          this.agent.targetX = msg.target[0];
          this.agent.targetY = msg.target[1];
          this.tBlock.x = msg.block[0];
          this.tBlock.y = msg.block[1];
          this.tBlock.angle = msg.block[2];
          this.coverage = msg.coverage;
          this.success = msg.success;
          this.isRecording = msg.is_recording;
          this.isAiAutopilot = msg.is_ai_autopilot;
          this.agentTrail = msg.trail || [];
          this.coverageHistory = msg.history || [];
          this.syncUI();
        } else if (msg.type === "episode_saved") {
          console.log("[PushT] Episode Auto-Saved by Python Engine:", msg.episode);
          this.episodes.unshift(msg.episode);
          this.updateEpisodeTable();
        }
      };

      this.ws.onclose = () => {
        this.backendConnected = false;
        this.updateHeaderStatus("🔵 Standalone Client Mode (Static)", false);
        console.log("[PushT] WebSocket Disconnected. Running in Standalone JS Mode.");
      };

      this.ws.onerror = () => {
        this.backendConnected = false;
        this.updateHeaderStatus("🔵 Standalone Client Mode (Static)", false);
      };
    } catch (e) {
      this.backendConnected = false;
      this.updateHeaderStatus("🔵 Standalone Client Mode (Static)", false);
    }
  }

  updateHeaderStatus(text, isLive) {
    const badge = document.getElementById('engineStatusBadge');
    if (badge) {
      badge.innerHTML = `
        <span class="status-dot" style="${isLive ? '' : 'background: #4facfe; box-shadow: 0 0 10px #4facfe;'}"></span>
        <span>${text}</span>
      `;
    }
  }

  initEventListeners() {
    const updateMouse = (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const clientX = e.clientX || (e.touches && e.touches[0].clientX);
      const clientY = e.clientY || (e.touches && e.touches[0].clientY);
      if (clientX === undefined) return;

      const scaleX = this.simWidth / rect.width;
      const scaleY = this.simHeight / rect.height;
      const x = Math.max(10, Math.min(this.simWidth - 10, (clientX - rect.left) * scaleX));
      const y = Math.max(10, Math.min(this.simHeight - 10, (clientY - rect.top) * scaleY));

      this.agent.targetX = x;
      this.agent.targetY = y;

      if (this.backendConnected && this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: "mouse_move", x: x, y: y }));
      }
    };

    this.canvas.addEventListener('mousemove', updateMouse);
    this.canvas.addEventListener('touchmove', (e) => { e.preventDefault(); updateMouse(e); }, { passive: false });
  }

  sendAction(actionType) {
    if (this.backendConnected && this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: actionType }));
    }
  }

  async fetchSavedEpisodes() {
    try {
      const res = await fetch('/api/episodes');
      if (res.ok) {
        const data = await res.json();
        if (data.episodes && data.episodes.length > 0) {
          this.episodes = data.episodes;
          this.updateEpisodeTable();
        }
      }
    } catch (e) {
      // Offline fallback
    }
  }

  syncUI() {
    const modePill = document.getElementById('modePill');
    const pauseOverlay = document.getElementById('pauseOverlay');
    const coverageVal = document.getElementById('coverageVal');
    const progressBar = document.getElementById('progressBar');
    const peakBadge = document.getElementById('peakBadge');
    const cardCoverage = document.getElementById('cardCoverage');
    const metricSteps = document.getElementById('metricSteps');
    const frameProgressBar = document.getElementById('frameProgressBar');
    const metricAgentPos = document.getElementById('metricAgentPos');
    const metricAgentSpeed = document.getElementById('metricAgentSpeed');
    const metricBlockPos = document.getElementById('metricBlockPos');
    const metricBlockAngle = document.getElementById('metricBlockAngle');
    const metricReward = document.getElementById('metricReward');
    const metricReturn = document.getElementById('metricReturn');
    const btnRecord = document.getElementById('btnRecord');
    const btnAi = document.getElementById('btnAi');

    // RL Reward & Return Calculation
    if (!this.cumulativeReturn) this.cumulativeReturn = 0.0;
    const distToBlock = Math.hypot(this.agent.x - this.tBlock.x, this.agent.y - this.tBlock.y);
    const stepReward = Math.max(-0.1, (this.coverage * 1.0) - (distToBlock / 1000.0));
    this.currentReward = stepReward;

    // Peak Coverage Tracking
    this.peakCoverage = Math.max(this.peakCoverage || 0, this.coverage || 0);

    // Active frame counter (0~500)
    if (!this.activeSteps) this.activeSteps = 0;
    if (!this.isPaused && (this.isRecording || this.isAiAutopilot || Math.hypot(this.agent.vx, this.agent.vy) > 0.5)) {
      this.activeSteps = (this.activeSteps + 1) % 501;
      this.cumulativeReturn += stepReward;
    }

    const covPct = Math.round((this.coverage || 0) * 100);
    const peakPct = Math.round(this.peakCoverage * 100);

    if (modePill) {
      if (this.isAiAutopilot) {
        modePill.innerText = "MODE: AI AUTOPILOT (Press 'M')";
        modePill.className = "overlay-badge mode-pill autopilot";
      } else {
        modePill.innerText = "MODE: TELEOP (Press 'M')";
        modePill.className = "overlay-badge mode-pill";
      }
    }

    if (pauseOverlay) {
      pauseOverlay.style.display = this.isPaused ? "flex" : "none";
    }

    if (coverageVal) coverageVal.innerText = `${covPct}%`;
    if (progressBar) progressBar.style.width = `${covPct}%`;
    if (peakBadge) peakBadge.innerText = `Peak ${peakPct}%`;
    if (metricReward) metricReward.innerText = `Reward: ${stepReward >= 0 ? '+' : ''}${stepReward.toFixed(4)}`;
    if (metricReturn) metricReturn.innerText = `Return: ${this.cumulativeReturn.toFixed(2)}`;

    if (cardCoverage) {
      if (this.coverage >= 0.90) cardCoverage.classList.add('success-glow');
      else cardCoverage.classList.remove('success-glow');
    }

    if (metricSteps) metricSteps.innerHTML = `${this.activeSteps} <span class="metric-sub-val">/ 500</span>`;
    if (frameProgressBar) frameProgressBar.style.width = `${Math.min(100, (this.activeSteps / 500) * 100)}%`;

    if (metricAgentPos) metricAgentPos.innerText = `(${Math.round(this.agent.x)}, ${Math.round(this.agent.y)})`;
    if (metricAgentSpeed) {
      const speed = Math.hypot(this.agent.vx || 0, this.agent.vy || 0);
      metricAgentSpeed.innerText = `Speed: ${speed.toFixed(1)} px/f`;
    }

    if (metricBlockPos) metricBlockPos.innerText = `(${Math.round(this.tBlock.x)}, ${Math.round(this.tBlock.y)})`;
    if (metricBlockAngle) {
      const deg = ((this.tBlock.angle * 180 / Math.PI) % 360).toFixed(1);
      metricBlockAngle.innerText = `Angle: ${deg}°`;
    }

    if (btnRecord) {
      if (this.isRecording) {
        btnRecord.classList.add('recording');
        btnRecord.innerHTML = '<span class="btn-dot dot-red"></span>Stop';
      } else {
        btnRecord.classList.remove('recording');
        btnRecord.innerHTML = '<span class="btn-dot dot-red"></span>Record';
      }
    }

    if (btnAi) {
      if (this.isAiAutopilot) {
        btnAi.classList.add('active');
        btnAi.innerHTML = '<span class="btn-dot dot-green"></span>Autopilot ON';
      } else {
        btnAi.classList.remove('active');
        btnAi.innerHTML = '<span class="btn-dot dot-purple"></span>Autopilot';
      }
    }
  }

  updateEpisodeTable() {
    const episodesTbody = document.getElementById('episodesTbody');
    if (!episodesTbody) return;
    episodesTbody.innerHTML = '';

    if (this.episodes.length === 0) {
      episodesTbody.innerHTML = `
        <tr>
          <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 16px;">
            No demonstration episodes recorded yet. Click <strong>[• Record]</strong> to collect your first trajectory!
          </td>
        </tr>
      `;
      return;
    }

    this.episodes.forEach((ep) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>#${ep.id}</td>
        <td>${ep.length} frames</td>
        <td>${Math.round(ep.maxCoverage * 100)}%</td>
        <td><span class="badge ${ep.success ? 'badge-success' : 'badge-fail'}">${ep.success ? 'SUCCESS' : 'INCOMPLETE'}</span></td>
        <td><span style="font-size:0.72rem; color:var(--accent-cyan);">📁 Auto-Saved</span></td>
      `;
      episodesTbody.appendChild(tr);
    });
  }

  // Draw T-Block at any pose
  drawTBlock(ctx, x, y, angle, fillStyle, strokeStyle, alpha = 1.0) {
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.translate(x, y);
    ctx.rotate(angle);

    ctx.fillStyle = fillStyle;
    ctx.strokeStyle = strokeStyle;
    ctx.lineWidth = 3;

    // Top Bar
    const tb = this.tBlock.topBar;
    ctx.beginPath();
    ctx.roundRect(tb.ox - tb.w / 2, tb.oy - tb.h / 2, tb.w, tb.h, 6);
    ctx.fill();
    ctx.stroke();

    // Stem Bar
    const sb = this.tBlock.stemBar;
    ctx.beginPath();
    ctx.roundRect(sb.ox - sb.w / 2, sb.oy - sb.h / 2, sb.w, sb.h, 6);
    ctx.fill();
    ctx.stroke();

    // Center of Mass Dot
    ctx.fillStyle = '#ff3366';
    ctx.beginPath();
    ctx.arc(0, 0, 4, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  }

  // Client-Side 2D Physics Step (Runs when standalone or for zero-lag tracking)
  stepPhysics() {
    if (this.isPaused) return;

    if (!this.backendConnected) {
      // 1. Agent Dynamics
      if (this.isAiAutopilot) {
        this.aiTimer = (this.aiTimer || 0) + 0.03;
        const targetX = this.goal.x + Math.sin(this.aiTimer * 1.5) * 80;
        const targetY = this.goal.y + Math.cos(this.aiTimer * 1.2) * 60;
        this.agent.targetX = targetX;
        this.agent.targetY = targetY;
      }

      const ax = (this.agent.targetX - this.agent.x) * 0.28;
      const ay = (this.agent.targetY - this.agent.y) * 0.28;
      this.agent.vx = (this.agent.vx || 0) * 0.88 + ax;
      this.agent.vy = (this.agent.vy || 0) * 0.88 + ay;
      
      const spd = Math.hypot(this.agent.vx, this.agent.vy);
      if (spd > 16.0) {
        this.agent.vx = (this.agent.vx / spd) * 16.0;
        this.agent.vy = (this.agent.vy / spd) * 16.0;
      }

      this.agent.x += this.agent.vx;
      this.agent.y += this.agent.vy;
      this.agent.x = Math.max(this.agent.radius, Math.min(this.simWidth - this.agent.radius, this.agent.x));
      this.agent.y = Math.max(this.agent.radius, Math.min(this.simHeight - this.agent.radius, this.agent.y));

      // 2. Collision with T-Block
      if (!this.tBlock.vx) this.tBlock.vx = 0;
      if (!this.tBlock.vy) this.tBlock.vy = 0;
      if (!this.tBlock.omega) this.tBlock.omega = 0;

      const cosA = Math.cos(this.tBlock.angle);
      const sinA = Math.sin(this.tBlock.angle);

      [this.tBlock.topBar, this.tBlock.stemBar].forEach(rect => {
        const rcx = this.tBlock.x + rect.ox * cosA - rect.oy * sinA;
        const rcy = this.tBlock.y + rect.ox * sinA + rect.oy * cosA;

        const relX = this.agent.x - rcx;
        const relY = this.agent.y - rcy;
        const localX = relX * cosA + relY * sinA;
        const localY = -relX * sinA + relY * cosA;

        const hw = rect.w / 2;
        const hh = rect.h / 2;
        const clampedX = Math.max(-hw, Math.min(hw, localX));
        const clampedY = Math.max(-hh, Math.min(hh, localY));

        const dx = localX - clampedX;
        const dy = localY - clampedY;
        const distSq = dx * dx + dy * dy;

        if (distSq < this.agent.radius * this.agent.radius) {
          const dist = Math.sqrt(distSq);
          const penetration = this.agent.radius - dist;
          const nx = dist > 0.0001 ? dx / dist : 0;
          const ny = dist > 0.0001 ? dy / dist : -1;

          const wnx = nx * cosA - ny * sinA;
          const wny = nx * sinA + ny * cosA;

          this.agent.x += wnx * penetration * 0.4;
          this.agent.y += wny * penetration * 0.4;
          this.tBlock.vx -= wnx * penetration * 0.55;
          this.tBlock.vy -= wny * penetration * 0.55;

          const contactX = rcx + clampedX * cosA - clampedY * sinA;
          const contactY = rcy + clampedX * sinA + clampedY * cosA;
          const rx = contactX - this.tBlock.x;
          const ry = contactY - this.tBlock.y;
          this.tBlock.omega += (rx * (-wny) - ry * (-wnx)) * penetration * 0.025;
        }
      });

      // 3. Integrate Block Physics
      this.tBlock.x += this.tBlock.vx;
      this.tBlock.y += this.tBlock.vy;
      this.tBlock.angle += this.tBlock.omega;
      this.tBlock.vx *= 0.88;
      this.tBlock.vy *= 0.88;
      this.tBlock.omega *= 0.86;

      this.tBlock.x = Math.max(30, Math.min(this.simWidth - 30, this.tBlock.x));
      this.tBlock.y = Math.max(30, Math.min(this.simHeight - 30, this.tBlock.y));

      // 4. Calculate IoU Coverage
      const dx = this.tBlock.x - this.goal.x;
      const dy = this.tBlock.y - this.goal.y;
      const dist = Math.hypot(dx, dy);
      let diffAngle = Math.abs((this.tBlock.angle - this.goal.angle) % (Math.PI * 2));
      if (diffAngle > Math.PI) diffAngle = Math.PI * 2 - diffAngle;

      const posScore = Math.max(0, 1.0 - dist / 140.0);
      const rotScore = Math.max(0, 1.0 - diffAngle / 1.2);
      const rawCoverage = (posScore * 0.65 + rotScore * 0.35) * (posScore > 0.3 ? 1.0 : posScore * 2.0);
      this.coverage = Math.min(1.0, Math.max(0, rawCoverage));
      this.success = (this.coverage >= 0.90);

      this.stepCount++;
      if (this.stepCount % 2 === 0) {
        this.agentTrail.push([Math.round(this.agent.x), Math.round(this.agent.y)]);
        if (this.agentTrail.length > 45) this.agentTrail.shift();
      }

      this.syncUI();
    }

    // Always record history for smooth 60FPS real-time chart tracking
    this.coverageHistory.push(this.coverage || 0);
    if (this.coverageHistory.length > 100) {
      this.coverageHistory.shift();
    }
  }

  // Main Render Loop
  render() {
    this.stepPhysics();

    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    ctx.save();
    ctx.scale(this.scale, this.scale);

    // 1. Grid
    ctx.strokeStyle = 'rgba(64, 93, 140, 0.12)';
    ctx.lineWidth = 1;
    const gridSize = 32;
    for (let x = 0; x <= this.simWidth; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, this.simHeight);
      ctx.stroke();
    }
    for (let y = 0; y <= this.simHeight; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(this.simWidth, y);
      ctx.stroke();
    }

    // 2. Goal Area (Translucent Cyan/Green)
    const goalFill = this.success ? 'rgba(0, 230, 118, 0.25)' : 'rgba(0, 242, 254, 0.18)';
    const goalStroke = this.success ? 'rgba(0, 230, 118, 0.8)' : 'rgba(0, 242, 254, 0.6)';
    this.drawTBlock(ctx, this.goal.x, this.goal.y, this.goal.angle, goalFill, goalStroke, 0.7);

    // 3. Agent Trajectory Trail
    if (this.agentTrail.length > 1) {
      ctx.beginPath();
      ctx.moveTo(this.agentTrail[0][0], this.agentTrail[0][1]);
      for (let i = 1; i < this.agentTrail.length; i++) {
        ctx.lineTo(this.agentTrail[i][0], this.agentTrail[i][1]);
      }
      ctx.strokeStyle = this.isRecording ? 'rgba(255, 51, 102, 0.45)' : 'rgba(0, 242, 254, 0.3)';
      ctx.lineWidth = 3;
      ctx.lineCap = 'round';
      ctx.stroke();
    }

    // 4. Active T-Block
    const blockFill = '#1e293b';
    const blockStroke = this.success ? '#00e676' : '#38bdf8';
    this.drawTBlock(ctx, this.tBlock.x, this.tBlock.y, this.tBlock.angle, blockFill, blockStroke, 1.0);

    // 5. Spring / Target Line from Agent to Target
    ctx.beginPath();
    ctx.moveTo(this.agent.x, this.agent.y);
    ctx.lineTo(this.agent.targetX, this.agent.targetY);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.25)';
    ctx.setLineDash([4, 4]);
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.setLineDash([]);

    // 6. Target Cursor Marker
    ctx.beginPath();
    ctx.arc(this.agent.targetX, this.agent.targetY, 5, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0, 242, 254, 0.7)';
    ctx.fill();

    // 7. Agent (Circle Robot End-Effector)
    ctx.save();
    ctx.shadowColor = this.isRecording ? '#ff3366' : '#00f2fe';
    ctx.shadowBlur = 15;
    ctx.beginPath();
    ctx.arc(this.agent.x, this.agent.y, this.agent.radius, 0, Math.PI * 2);
    ctx.fillStyle = this.isRecording ? '#ff3366' : '#0284c7';
    ctx.fill();
    ctx.lineWidth = 3;
    ctx.strokeStyle = '#ffffff';
    ctx.stroke();

    // Inner Core
    ctx.beginPath();
    ctx.arc(this.agent.x, this.agent.y, 6, 0, Math.PI * 2);
    ctx.fillStyle = '#ffffff';
    ctx.fill();
    ctx.restore();

    ctx.restore();
  }
}

// Global Binding
document.addEventListener('DOMContentLoaded', () => {
  const sim = new PushTHybridSimulator('simCanvas');

  const btnReset = document.getElementById('btnReset');
  const btnRecord = document.getElementById('btnRecord');
  const btnAi = document.getElementById('btnAi');
  const btnExport = document.getElementById('btnExport');
  const chartCanvas = document.getElementById('chartCanvas');
  const chartCtx = chartCanvas ? chartCanvas.getContext('2d') : null;

  // Render Loop (Always updates chart, matching Python)
  function loop() {
    sim.render();
    if (chartCtx) {
      renderMiniChart(chartCtx, sim.coverageHistory);
    }
    requestAnimationFrame(loop);
  }

  function renderMiniChart(ctx, data) {
    const w = chartCanvas.width;
    const h = chartCanvas.height;
    ctx.clearRect(0, 0, w, h);

    const maxPts = 80;
    const displayData = data.slice(-maxPts);
    const plotH = h * 0.78;
    const baseY = h - 6;
    const targetY = baseY - (0.90 * plotH);

    // 1. Draw 90% Target Success Line (Crisp Dashed Green)
    ctx.save();
    ctx.strokeStyle = 'rgba(0, 230, 118, 0.8)';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(0, targetY);
    ctx.lineTo(w, targetY);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.restore();

    // 2. Base 0% Baseline
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, baseY);
    ctx.lineTo(w, baseY);
    ctx.stroke();

    if (displayData.length < 2) {
      // Idle Start Dot
      ctx.beginPath();
      ctx.arc(4, baseY, 3.5, 0, Math.PI * 2);
      ctx.fillStyle = '#00f2fe';
      ctx.fill();
      return;
    }

    const stepX = w / Math.max(1, displayData.length - 1);

    // 3. Rich Vibrant Area Fill (100% Exact Match with Python's pygame.draw.polygon)
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(0, baseY);
    displayData.forEach((val, i) => {
      const x = i * stepX;
      const y = baseY - (val * plotH);
      ctx.lineTo(x, y);
    });
    ctx.lineTo(w, baseY);
    ctx.closePath();

    // Solid Rich Cyan Fill + Subtle Top Gradient
    const grad = ctx.createLinearGradient(0, targetY, 0, baseY);
    grad.addColorStop(0, 'rgba(0, 242, 254, 0.40)');
    grad.addColorStop(1, 'rgba(0, 242, 254, 0.18)');
    ctx.fillStyle = grad;
    ctx.fill();
    ctx.restore();

    // 4. Solid Neon Stroke Line with Glow
    ctx.save();
    ctx.shadowColor = '#00f2fe';
    ctx.shadowBlur = 10;
    ctx.strokeStyle = '#00f2fe';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    displayData.forEach((val, i) => {
      const x = i * stepX;
      const y = baseY - (val * plotH);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
    ctx.restore();

    // 5. Live Pulse Head Dot at Last Position
    const lastVal = displayData[displayData.length - 1];
    const lastX = w;
    const lastY = baseY - (lastVal * plotH);

    ctx.save();
    ctx.shadowColor = '#00f2fe';
    ctx.shadowBlur = 14;
    ctx.beginPath();
    ctx.arc(lastX, lastY, 4.5, 0, Math.PI * 2);
    ctx.fillStyle = '#ffffff';
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = '#00f2fe';
    ctx.stroke();
    ctx.restore();
  }

  btnReset.addEventListener('click', () => {
    sim.activeSteps = 0;
    sim.peakCoverage = 0;
    sim.cumulativeReturn = 0.0;
    sim.sendAction("reset");
  });

  btnRecord.addEventListener('click', () => {
    if (!sim.isRecording) {
      sim.sendAction("record_start");
    } else {
      sim.sendAction("record_stop");
    }
  });

  btnAi.addEventListener('click', () => {
    sim.sendAction("toggle_ai");
  });

  btnExport.addEventListener('click', () => {
    if (sim.episodes.length === 0) {
      alert('No teleoperation episodes recorded yet. Please click [Record Teleop] first!');
      return;
    }
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(sim.episodes, null, 2));
    const dlAnchor = document.createElement('a');
    dlAnchor.setAttribute("href", dataStr);
    dlAnchor.setAttribute("download", `lerobot_pusht_dataset_${Date.now()}.json`);
    document.body.appendChild(dlAnchor);
    dlAnchor.click();
    dlAnchor.remove();
  });

  // Global Keyboard Shortcuts
  window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    
    if (e.code === 'Space') {
      e.preventDefault();
      sim.isPaused = !sim.isPaused;
      sim.syncUI();
    } else if (e.code === 'KeyM') {
      btnAi.click();
    } else if (e.code === 'KeyR') {
      btnReset.click();
    } else if (e.code === 'KeyS') {
      btnRecord.click();
    }
  });

  loop();
});
