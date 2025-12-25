(() => {
  const canvas = document.getElementById('zx-dotwave');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const rootStyles = getComputedStyle(document.documentElement);
  const accent = rootStyles.getPropertyValue('--accent').trim() || '#39ff14';

  const settings = {
    dotColor: accent,
    dotRadius: 1.2,
    gridGap: 26,
    waveSpeed: 0.002,
    waveAmplitude: 10,
    waveFrequency: 0.02,
    glowRadius: 10,
    repelRadius: 90,
    repelStrength: 32,
  };

  let width = 0;
  let height = 0;
  let dots = [];
  let time = 0;
  const mouse = { x: -9999, y: -9999 };
  let needsRebuild = true;

  function resize() {
    const ratio = window.devicePixelRatio || 1;
    width = Math.floor(window.innerWidth);
    height = Math.floor(window.innerHeight);
    canvas.width = width * ratio;
    canvas.height = height * ratio;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    needsRebuild = true;
  }

  function buildGrid() {
    dots = [];
    const gap = settings.gridGap;
    const offsetX = (width % gap) * 0.5;
    const offsetY = (height % gap) * 0.5;
    for (let y = offsetY; y < height; y += gap) {
      for (let x = offsetX; x < width; x += gap) {
        dots.push({ x, y, baseY: y, baseX: x });
      }
    }
    needsRebuild = false;
  }

  function updateMouse(event) {
    const rect = canvas.getBoundingClientRect();
    mouse.x = event.clientX - rect.left;
    mouse.y = event.clientY - rect.top;
  }

  function clearMouse() {
    mouse.x = -9999;
    mouse.y = -9999;
  }

  function drawDot(dot, offsetY, glow) {
    ctx.beginPath();
    ctx.arc(dot.x, dot.y + offsetY, settings.dotRadius + glow * 0.8, 0, Math.PI * 2);
    ctx.fill();
  }

  function animate() {
    if (needsRebuild) {
      buildGrid();
    }
    time += settings.waveSpeed;

    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = settings.dotColor;
    ctx.shadowColor = settings.dotColor;

    for (let i = 0; i < dots.length; i += 1) {
      const dot = dots[i];
      const wave = Math.sin((dot.x + time * 200) * settings.waveFrequency) * settings.waveAmplitude;
      const wave2 = Math.cos((dot.y + time * 200) * settings.waveFrequency) * (settings.waveAmplitude * 0.6);
      let offsetY = wave + wave2;

      const dx = dot.x - mouse.x;
      const dy = dot.y + offsetY - mouse.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      let glow = 0;

      if (dist < settings.repelRadius) {
        const force = (1 - dist / settings.repelRadius) * settings.repelStrength;
        offsetY += (dy / (dist || 1)) * force;
        glow = 1 - dist / settings.repelRadius;
      }

      ctx.shadowBlur = settings.glowRadius * glow;
      ctx.globalAlpha = 0.65 + glow * 0.35;
      drawDot(dot, offsetY, glow);
    }

    ctx.shadowBlur = 0;
    ctx.globalAlpha = 1;
    requestAnimationFrame(animate);
  }

  window.addEventListener('resize', resize);
  window.addEventListener('mousemove', updateMouse);
  window.addEventListener('mouseleave', clearMouse);
  window.addEventListener('blur', clearMouse);

  resize();
  requestAnimationFrame(animate);
})();
