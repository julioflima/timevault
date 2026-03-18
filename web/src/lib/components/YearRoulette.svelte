<script lang="ts">
  let {
    value = $bindable(new Date().getFullYear()),
    minYear = new Date().getFullYear(),
    maxYear,
    label = "Unlock year",
  }: {
    value?: number;
    minYear?: number;
    maxYear?: number | undefined;
    label?: string;
  } = $props();

  const count = 18;
  const size = 340;
  const cx = size / 2;
  const cy = size / 2;
  const outerR = size * 0.46;
  const innerR = size * 0.2;
  const labelR = innerR + (outerR - innerR) * 0.55;
  const sliceAngle = (Math.PI * 2) / count;
  const sliceDeg = 360 / count;
  const maxStep =
    typeof maxYear === "number"
      ? Math.max(0, maxYear - minYear)
      : Number.POSITIVE_INFINITY;

  let rotation = $state(0);
  let dragging = $state(false);
  let lastAngle = 0;
  let velocity = 0;
  let animFrame = 0;
  let svgEl: SVGSVGElement;

  function arcPath(a1: number, a2: number, rO: number, rI: number): string {
    const x1o = cx + Math.cos(a1) * rO,
      y1o = cy + Math.sin(a1) * rO;
    const x2o = cx + Math.cos(a2) * rO,
      y2o = cy + Math.sin(a2) * rO;
    const x1i = cx + Math.cos(a2) * rI,
      y1i = cy + Math.sin(a2) * rI;
    const x2i = cx + Math.cos(a1) * rI,
      y2i = cy + Math.sin(a1) * rI;
    const lrg = a2 - a1 > Math.PI ? 1 : 0;
    return `M${x1o} ${y1o} A${rO} ${rO} 0 ${lrg} 1 ${x2o} ${y2o} L${x1i} ${y1i} A${rI} ${rI} 0 ${lrg} 0 ${x2i} ${y2i} Z`;
  }

  // Spiral line from center outward (the helicoid seen from top)
  const spiralPath = (() => {
    const turns = 4;
    const pts = 300;
    let d = "";
    for (let i = 0; i <= pts; i++) {
      const t = i / pts;
      const angle = t * turns * Math.PI * 2 - Math.PI / 2;
      const r = innerR + t * (outerR - innerR);
      const x = cx + Math.cos(angle) * r;
      const y = cy + Math.sin(angle) * r;
      d += (i === 0 ? "M" : "L") + ` ${x} ${y}`;
    }
    return d;
  })();

  type Sector = {
    path: string;
    lx: number;
    ly: number;
    lAngle: number;
    depth: number;
  };

  const sectors: Sector[] = Array.from({ length: count }, (_, i) => {
    // Shift by half slice so the indicator points to the center of a step.
    const a1 = i * sliceAngle - Math.PI / 2 - sliceAngle / 2;
    const a2 = a1 + sliceAngle;
    const mid = a1 + sliceAngle / 2;
    const lx = cx + Math.cos(mid) * labelR;
    const ly = cy + Math.sin(mid) * labelR;
    let lAngle = (mid * 180) / Math.PI + 90;
    if (lAngle > 90 && lAngle < 270) lAngle += 180;
    // Depth: sectors get progressively darker around the spiral
    const depth = i / count;
    return { path: arcPath(a1, a2, outerR, innerR), lx, ly, lAngle, depth };
  });

  // Riser lines at each sector boundary
  const risers = Array.from({ length: count }, (_, i) => {
    const angle = i * sliceAngle - Math.PI / 2 - sliceAngle / 2;
    return {
      x1: cx + Math.cos(angle) * innerR,
      y1: cy + Math.sin(angle) * innerR,
      x2: cx + Math.cos(angle) * outerR,
      y2: cy + Math.sin(angle) * outerR,
    };
  });

  // Which sector is at indicator
  const minRotation = Number.isFinite(maxStep)
    ? -maxStep * sliceDeg
    : Number.NEGATIVE_INFINITY;
  const maxRotation = 0;

  function clampStep(step: number): number {
    if (Number.isFinite(maxStep)) {
      return Math.max(0, Math.min(maxStep, step));
    }
    return Math.max(0, step);
  }

  function clampRotation(r: number): number {
    return Math.max(minRotation, Math.min(maxRotation, r));
  }

  let selectedStep = $derived.by(() => {
    return clampStep(Math.round(-rotation / sliceDeg));
  });

  let selectedIndex = $derived.by(() => {
    return ((selectedStep % count) + count) % count;
  });

  function stepForSector(i: number): number {
    return selectedStep + (i - selectedIndex);
  }

  function yearForSector(i: number): number | null {
    const step = stepForSector(i);
    if (step < 0) return null;
    if (Number.isFinite(maxStep) && step > maxStep) return null;
    return minYear + step;
  }

  $effect(() => {
    if (!dragging) {
      value = minYear + selectedStep;
    }
  });

  $effect(() => {
    if (!dragging) {
      const desiredStep = clampStep((value ?? minYear) - minYear);
      const target = -desiredStep * sliceDeg;
      if (Math.abs(rotation - target) > 0.0001) {
        rotation = clampRotation(target);
      }
    }
  });

  function sectorFill(i: number, depth: number): string {
    const year = yearForSector(i);
    if (year === null) return "rgba(255,255,255,0.04)";
    if (i === selectedIndex) return "rgba(20, 20, 20, 0.92)";
    // Alternating light/dark with depth gradient
    const base = i % 2 === 0 ? 28 : 18;
    const l = base + depth * 14;
    return `hsl(0, 0%, ${l}%)`;
  }

  function getAngle(e: PointerEvent): number {
    const rect = svgEl.getBoundingClientRect();
    return Math.atan2(
      e.clientY - rect.top - rect.height / 2,
      e.clientX - rect.left - rect.width / 2,
    );
  }

  function onPointerDown(e: PointerEvent) {
    cancelAnimationFrame(animFrame);
    dragging = true;
    velocity = 0;
    lastAngle = getAngle(e);
    svgEl.setPointerCapture(e.pointerId);
  }

  function onPointerMove(e: PointerEvent) {
    if (!dragging) return;
    const angle = getAngle(e);
    let delta = ((angle - lastAngle) * 180) / Math.PI;
    if (delta > 180) delta -= 360;
    if (delta < -180) delta += 360;
    rotation = clampRotation(rotation + delta);
    velocity = delta;
    lastAngle = angle;
  }

  function onPointerUp(e: PointerEvent) {
    if (!dragging) return;
    dragging = false;
    svgEl.releasePointerCapture(e.pointerId);
    spin();
  }

  function spin() {
    if (Math.abs(velocity) < 0.15) {
      snapToNearest();
      return;
    }
    rotation = clampRotation(rotation + velocity);
    if (rotation === minRotation || rotation === maxRotation) {
      velocity = 0;
      snapToNearest();
      return;
    }
    velocity *= 0.96;
    animFrame = requestAnimationFrame(spin);
  }

  function snapToNearest() {
    const step = clampStep(Math.round(-rotation / sliceDeg));
    const target = -step * sliceDeg;
    animateSnap(target, 300);
  }

  function animateSnap(target: number, duration: number) {
    const start = rotation;
    const safeTarget = clampRotation(target);
    const t0 = performance.now();
    function frame(now: number) {
      const t = Math.min((now - t0) / duration, 1);
      const ease = 1 - Math.pow(1 - t, 3);
      rotation = clampRotation(start + (safeTarget - start) * ease);
      if (t < 1) animFrame = requestAnimationFrame(frame);
    }
    animFrame = requestAnimationFrame(frame);
  }

  function handleWheel(e: WheelEvent) {
    e.preventDefault();
    if (Math.abs(e.deltaY) < 4) return;
    rotation = clampRotation(rotation + (e.deltaY > 0 ? -sliceDeg : sliceDeg));
    snapToNearest();
  }
</script>

<div class="roulette">
  <div class="roulette__header">
    <span class="roulette__label">{label}</span>
    <span class="roulette__value mono">{value}</span>
  </div>

  <div class="roulette__container">
    <!-- Indicator -->
    <div class="roulette__indicator">▼</div>

    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <svg
      bind:this={svgEl}
      width={size}
      height={size}
      viewBox="0 0 {size} {size}"
      class="roulette__svg"
      class:roulette__svg--dragging={dragging}
      onpointerdown={onPointerDown}
      onpointermove={onPointerMove}
      onpointerup={onPointerUp}
      onpointercancel={onPointerUp}
      onwheel={handleWheel}
      role="spinbutton"
      tabindex="0"
      aria-label={label}
      aria-valuemin={minYear}
      aria-valuemax={typeof maxYear === "number" ? maxYear : undefined}
      aria-valuenow={value}
    >
      <defs>
        <radialGradient id="heli-fade" cx="50%" cy="50%" r="50%">
          <stop offset="70%" stop-color="white" stop-opacity="0" />
          <stop offset="100%" stop-color="white" stop-opacity="0.6" />
        </radialGradient>
        <mask id="heli-mask">
          <rect width={size} height={size} fill="white" />
          <rect width={size} height={size} fill="url(#heli-fade)" />
        </mask>
      </defs>

      <!-- Spinning group -->
      <g transform="rotate({rotation}, {cx}, {cy})" mask="url(#heli-mask)">
        <!-- Sectors -->
        {#each sectors as s, i}
          <path
            d={s.path}
            fill={sectorFill(i, s.depth)}
            stroke="rgba(255,255,255,0.08)"
            stroke-width="0.5"
          />
        {/each}

        <!-- Riser lines -->
        {#each risers as r}
          <line
            x1={r.x1}
            y1={r.y1}
            x2={r.x2}
            y2={r.y2}
            stroke="rgba(255,255,255,0.12)"
            stroke-width="0.8"
          />
        {/each}

        <!-- Spiral line (helicoid curve) -->
        <path
          d={spiralPath}
          fill="none"
          stroke="rgba(255,255,255,0.18)"
          stroke-width="1.5"
        />

        <!-- Labels -->
        {#each sectors as s, i}
          {@const year = yearForSector(i)}
          <text
            x={s.lx}
            y={s.ly}
            text-anchor="middle"
            dominant-baseline="central"
            transform="rotate({s.lAngle}, {s.lx}, {s.ly})"
            fill={year === null
              ? "rgba(255,255,255,0.16)"
              : i === selectedIndex
                ? "white"
                : "rgba(255,255,255,0.75)"}
            font-size={Math.max(10, size * 0.042)}
            font-weight={i === selectedIndex && year !== null ? "800" : "500"}
            font-family="monospace"
            style="pointer-events:none;user-select:none"
          >{year ?? ""}</text
          >
        {/each}
      </g>

      <!-- Center hole -->
      <circle {cx} {cy} r={innerR} fill="white" fill-opacity="0.9" />
      <circle
        {cx}
        {cy}
        r={innerR}
        fill="none"
        stroke="rgba(0,0,0,0.1)"
        stroke-width="1"
      />

      <!-- Center label -->
      <text
        x={cx}
        y={cy}
        text-anchor="middle"
        dominant-baseline="central"
        fill="rgba(0,0,0,0.85)"
        font-size={size * 0.065}
        font-weight="800"
        font-family="monospace"
        style="pointer-events:none">{value}</text
      >
    </svg>
  </div>
</div>

<style lang="scss">
  @use "$lib/styles/variables" as *;

  .roulette {
    width: min(100%, 24rem);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.9rem;
  }

  .roulette__header {
    display: flex;
    width: 100%;
    align-items: baseline;
    justify-content: space-between;
    gap: 1rem;
  }

  .roulette__label {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: $color-black-60;
  }

  .roulette__value {
    font-size: 1.75rem;
    line-height: 1;
    color: $color-black;
  }

  .roulette__container {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    touch-action: none;
  }

  .roulette__indicator {
    position: absolute;
    top: -12px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
    font-size: 1.2rem;
    color: rgba(0, 0, 0, 0.7);
  }

  .roulette__svg {
    display: block;
    cursor: grab;
    user-select: none;
    outline: none;
  }

  .roulette__svg--dragging {
    cursor: grabbing;
  }
</style>
