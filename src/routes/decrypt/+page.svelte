<script lang="ts">
	import StepFlow from '$lib/components/StepFlow.svelte';

	let current = $state(0);
	let seedHex = $state('');
	let vaultInput = $state('');
</script>

<StepFlow bind:current steps={[step1, step2, step3, step4]} />

{#snippet step1()}
	<div class="card step-card text-center">
		<h2>Select a vault</h2>
		<p class="hint">Public vaults from time-vault-secrets</p>
		<div class="vault-list">
			<p class="mono placeholder">Loading vaults...</p>
		</div>
		<p class="hint">Or paste vault JSON below &#9660;</p>
	</div>
{/snippet}

{#snippet step2()}
	<div class="card step-card text-center">
		<h2>Paste vault data</h2>
		<textarea class="input" placeholder="Paste vault JSON here..." bind:value={vaultInput}></textarea>
	</div>
{/snippet}

{#snippet step3()}
	<div class="card step-card text-center">
		<h2>Enter the seed S</h2>
		<p class="hint">The secret seed to decrypt this vault</p>
		<input class="input mono" placeholder="hex seed..." bind:value={seedHex} />
	</div>
{/snippet}

{#snippet step4()}
	<div class="card step-card text-center">
		<h2>Decrypted secret</h2>
		<div class="result mono">
			<p class="placeholder">Decrypted content will appear here</p>
		</div>
	</div>
{/snippet}

<style lang="scss">
	@use '$lib/styles/variables' as *;

	.step-card {
		max-width: 500px;
		width: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1.5rem;

		h2 {
			font-size: 1.5rem;
			font-weight: 600;
		}
	}

	.hint {
		font-size: 0.875rem;
		color: $color-white-60;
	}

	.vault-list {
		@include glass(12px, $color-white-10, $color-white-20);
		width: 100%;
		min-height: 200px;
		padding: 1rem;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.placeholder {
		color: $color-white-20;
	}

	.result {
		@include glass(12px, $color-white-10, $color-white-20);
		width: 100%;
		padding: 1.5rem;
		min-height: 100px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.875rem;
	}
</style>
