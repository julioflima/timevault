<script lang="ts">
  import { onDestroy } from "svelte";
  import { tick } from "svelte";

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

  function upperBound(): number {
    return typeof maxYear === "number"
      ? Math.max(minYear, maxYear)
      : Number.POSITIVE_INFINITY;
  }

  function clamp(next: number): number {
    const max = upperBound();
    if (Number.isFinite(max)) {
      return Math.max(minYear, Math.min(max, next));
    }
    return Math.max(minYear, next);
  }

  function setYear(next: number) {
    value = clamp(next);
  }

  function decrease() {
    setYear(value - 1);
  }
  function increase() {
    setYear(value + 1);
  }

  // --- hold-to-repeat ---
  let holdTimeout: ReturnType<typeof setTimeout> | null = null;
  let holdInterval: ReturnType<typeof setInterval> | null = null;

  function clearHoldTimers() {
    if (holdTimeout) {
      clearTimeout(holdTimeout);
      holdTimeout = null;
    }
    if (holdInterval) {
      clearInterval(holdInterval);
      holdInterval = null;
    }
  }

  function startHold(dir: "up" | "down") {
    const ok = dir === "up" ? canIncrease : canDecrease;
    if (!ok) return;
    const step = dir === "up" ? increase : decrease;
    step();
    clearHoldTimers();
    holdTimeout = setTimeout(() => {
      holdInterval = setInterval(() => {
        const still = dir === "up" ? canIncrease : canDecrease;
        if (!still) {
          clearHoldTimers();
          return;
        }
        step();
      }, 85);
    }, 260);
  }

  function stopHold() {
    clearHoldTimers();
  }
  onDestroy(() => {
    clearHoldTimers();
  });

  function onKeydown(e: KeyboardEvent) {
    if (e.key === "ArrowDown" || e.key === "ArrowLeft") {
      e.preventDefault();
      decrease();
    } else if (e.key === "ArrowUp" || e.key === "ArrowRight") {
      e.preventDefault();
      increase();
    }
  }

  const canDecrease = $derived(value > minYear);
  const canIncrease = $derived(() => {
    const max = upperBound();
    return !Number.isFinite(max) || value < max;
  });

  // --- split-flap digit animation ---
  const FLIP_MS = 300;

  function toDigits(y: number): string[] {
    return String(y).padStart(4, "0").split("");
  }

  // Always derive current digits directly from value — no lag, no flicker.
  let displayDigits = $derived(toDigits(value));

  let prevDigits = $state(toDigits(value));
  let flipping = $state([false, false, false, false]);
  let flipTimer: ReturnType<typeof setTimeout> | null = null;

  $effect(() => {
    const next = toDigits(value);
    const prev = prevDigits.slice();

    const changed: number[] = [];
    for (let i = 0; i < 4; i++) {
      if (next[i] !== prev[i]) changed.push(i);
    }

    // Always keep prevDigits in sync even when nothing changed.
    if (changed.length === 0) {
      prevDigits = next;
      return;
    }

    // Cancel any pending previous flip timer so rapid clicks don't conflict.
    if (flipTimer) clearTimeout(flipTimer);

    flipping = [false, false, false, false].map((_, i) => changed.includes(i));

    flipTimer = setTimeout(() => {
      prevDigits = next;
      flipping = [false, false, false, false];
      flipTimer = null;
    }, FLIP_MS);
  });
</script>

<div class="sf">
  <div class="sf__board" role="group" aria-label={label}>
    {#each displayDigits as digit, i}
      <div class="sf__cell">
        <!-- Static bottom: shows OLD digit during flip (covered by bottom flap landing) -->
        <div class="sf__half sf__half--bottom">
          <span class="sf__char">{flipping[i] ? prevDigits[i] : digit}</span>
        </div>

        <!-- Static top: shows NEW digit during flip (revealed as top flap falls) -->
        <div class="sf__half sf__half--top">
          <span class="sf__char">{digit}</span>
        </div>

        <!-- Flipping top flap: old digit folds down first -->
        {#if flipping[i]}
          <div
            class="sf__flap sf__flap--top"
            style="animation-duration:{FLIP_MS / 2}ms"
          >
            <span class="sf__char">{prevDigits[i]}</span>
          </div>

          <!-- Flipping bottom flap: new digit folds up after top finishes -->
          <div
            class="sf__flap sf__flap--bottom"
            style="animation-duration:{FLIP_MS / 2}ms;animation-delay:{FLIP_MS /
              2}ms"
          >
            <span class="sf__char">{digit}</span>
          </div>
        {/if}

        <!-- Horizontal split line + hinge dots -->
        <div class="sf__split" aria-hidden="true">
          <span class="sf__hinge sf__hinge--l"></span>
          <span class="sf__hinge sf__hinge--r"></span>
        </div>
      </div>
    {/each}
  </div>

  <div class="sf__controls">
    <button
      class="sf__btn"
      disabled={!canIncrease}
      aria-label="Next year"
      onpointerdown={() => startHold("up")}
      onpointerup={stopHold}
      onpointercancel={stopHold}
      onpointerleave={stopHold}
      onkeydown={(e) => {
        if (e.key === " " || e.key === "Enter") {
          e.preventDefault();
          startHold("up");
        }
      }}
      onkeyup={stopHold}
      onblur={stopHold}>&#9650;</button
    >

    <button
      class="sf__btn"
      disabled={!canDecrease}
      aria-label="Previous year"
      onpointerdown={() => startHold("down")}
      onpointerup={stopHold}
      onpointercancel={stopHold}
      onpointerleave={stopHold}
      onkeydown={(e) => {
        if (e.key === " " || e.key === "Enter") {
          e.preventDefault();
          startHold("down");
        }
      }}
      onkeyup={stopHold}
      onblur={stopHold}>&#9660;</button
    >
  </div>

  <!-- Hidden spinbutton for accessibility / keyboard -->
  <div
    class="sf__a11y"
    role="spinbutton"
    tabindex="0"
    aria-label={label}
    aria-valuemin={minYear}
    aria-valuemax={Number.isFinite(upperBound()) ? upperBound() : undefined}
    aria-valuenow={value}
    onkeydown={onKeydown}
  ></div>
</div>

<style>
  /* ── layout ── */
  .sf {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    user-select: none;
  }

  .sf__board {
    display: flex;
    gap: 0.35rem;
  }

  /* ── single digit cell ── */
  .sf__cell {
    position: relative;
    width: clamp(3rem, 10vw, 4.4rem);
    height: clamp(4.2rem, 14vw, 6.2rem);
    border-radius: 0.5rem;
    background: #1a1a1a;
    box-shadow:
      0 4px 12px rgba(0, 0, 0, 0.5),
      inset 0 1px 0 rgba(255, 255, 255, 0.06);
    perspective: 260px;
    /* No overflow:hidden — it kills 3D perspective transforms */
  }

  /* ── static halves ── */
  .sf__half {
    position: absolute;
    left: 0;
    right: 0;
    height: 50%;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .sf__half--top {
    top: 0;
    background: linear-gradient(180deg, #2a2a2a 0%, #1f1f1f 100%);
    border-radius: 0.5rem 0.5rem 0 0;
  }

  .sf__half--bottom {
    bottom: 0;
    background: linear-gradient(180deg, #181818 0%, #222 100%);
    border-radius: 0 0 0.5rem 0.5rem;
  }

  .sf__half--top .sf__char {
    transform: translateY(50%);
  }

  .sf__half--bottom .sf__char {
    transform: translateY(-50%);
  }

  /* ── digit text ── */
  .sf__char {
    font-family: "SF Mono", "Fira Code", "Cascadia Code", "Consolas", monospace;
    font-size: clamp(1.8rem, 7vw, 3rem);
    font-weight: 800;
    color: #fff;
    line-height: 1;
    letter-spacing: 0.02em;
  }

  /* ── animated flaps ── */
  .sf__flap {
    position: absolute;
    left: 0;
    right: 0;
    height: 50%;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    backface-visibility: hidden;
    transform-style: preserve-3d;
  }

  .sf__flap--top {
    top: 0;
    transform-origin: bottom center;
    background: linear-gradient(180deg, #2a2a2a 0%, #1f1f1f 100%);
    border-radius: 0.5rem 0.5rem 0 0;
    animation: flap-top-down ease-in forwards;
    z-index: 4;
  }

  .sf__flap--bottom {
    bottom: 0;
    transform-origin: top center;
    background: linear-gradient(180deg, #181818 0%, #222 100%);
    border-radius: 0 0 0.5rem 0.5rem;
    animation: flap-bottom-up ease-out forwards;
    transform: rotateX(90deg);
    z-index: 3;
  }

  .sf__flap--top .sf__char {
    transform: translateY(50%);
  }

  .sf__flap--bottom .sf__char {
    transform: translateY(-50%);
  }

  @keyframes flap-top-down {
    0% {
      transform: rotateX(0deg);
    }
    100% {
      transform: rotateX(-90deg);
    }
  }

  @keyframes flap-bottom-up {
    0% {
      transform: rotateX(90deg);
    }
    100% {
      transform: rotateX(0deg);
    }
  }

  /* ── horizontal split line + hinges ── */
  .sf__split {
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 0;
    z-index: 5;
    border-top: 1.5px solid rgba(0, 0, 0, 0.7);
    box-shadow: 0 0.5px 0 rgba(255, 255, 255, 0.06);
  }

  .sf__hinge {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #333;
    border: 1px solid #444;
    box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.5);
  }

  .sf__hinge--l {
    left: -3px;
  }
  .sf__hinge--r {
    right: -3px;
  }

  /* ── arrow buttons ── */
  .sf__controls {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .sf__btn {
    display: grid;
    place-items: center;
    width: 2.4rem;
    height: 2.4rem;
    border: 1.5px solid rgba(255, 255, 255, 0.15);
    border-radius: 0.45rem;
    background: #1a1a1a;
    color: #fff;
    font-size: 0.9rem;
    cursor: pointer;
    transition:
      background 100ms ease,
      transform 80ms ease;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  }

  .sf__btn:hover:not(:disabled) {
    background: #2c2c2c;
  }

  .sf__btn:active:not(:disabled) {
    transform: scale(0.93);
    background: #333;
  }

  .sf__btn:disabled {
    opacity: 0.25;
    cursor: not-allowed;
  }

  /* ── accessibility hidden spinbutton ── */
  .sf__a11y {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
  }
</style>
