<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		steps,
		current = $bindable(0)
	}: {
		steps: Snippet[];
		current?: number;
	} = $props();

	function go(dir: number) {
		const next = current + dir;
		if (next >= 0 && next < steps.length) current = next;
	}

	function onKeydown(e: KeyboardEvent) {
		if (e.key === 'ArrowDown' || e.key === 'Enter') {
			e.preventDefault();
			go(1);
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			go(-1);
		}
	}
</script>

<svelte:window on:keydown={onKeydown} />

<div class="step-flow">
	<div class="step-track" style="transform: translateY(-{current * 100}vh)">
		{#each steps as step, i}
			<div class="step" class:active={i === current}>
				{@render step()}
			</div>
		{/each}
	</div>

	<nav class="step-nav" aria-label="Step navigation">
		<button
			class="step-nav__btn"
			onclick={() => go(-1)}
			disabled={current === 0}
			aria-label="Previous step"
		>
			&#9650;
		</button>
		<span class="step-nav__count">{current + 1}/{steps.length}</span>
		<button
			class="step-nav__btn"
			onclick={() => go(1)}
			disabled={current === steps.length - 1}
			aria-label="Next step"
		>
			&#9660;
		</button>
	</nav>
</div>

<style lang="scss">
	@use '$lib/styles/variables' as *;

	.step-flow {
		position: fixed;
		inset: 0;
		overflow: hidden;
	}

	.step-track {
		transition: transform $transition-slide;
		will-change: transform;
	}

	.step {
		height: 100vh;
		width: 100vw;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 2rem;
	}

	.step-nav {
		position: fixed;
		bottom: 2rem;
		right: 2rem;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
		z-index: 10;
	}

	.step-nav__btn {
		width: 40px;
		height: 40px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.9rem;
		color: $color-white;
		background: $color-black-50;
		border: 1px solid $color-white-20;
		border-radius: 50%;
		cursor: pointer;
		transition: background $transition-fast;

		&:hover:not(:disabled) {
			background: $color-black-80;
		}

		&:disabled {
			opacity: 0.3;
			cursor: default;
		}
	}

	.step-nav__count {
		font-size: 0.75rem;
		color: $color-white-60;
		font-family: $font-mono;
	}
</style>
