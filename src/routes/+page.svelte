<script lang="ts">
	import StepFlow from '$lib/components/StepFlow.svelte';

	let current = $state(0);
	let unlockDate = $state('');
	let secretType = $state<'phrase' | 'file' | null>(null);
	let phrase = $state('');
	let file = $state<File | null>(null);

	// Computed from date
	let yearsFromNow = $derived(() => {
		if (!unlockDate) return 0;
		const target = new Date(unlockDate).getFullYear();
		const now = new Date().getFullYear();
		return Math.max(target - now, 0);
	});

	let nBits = $derived(() => {
		const T = yearsFromNow();
		if (T <= 0) return 67;
		return 67 + Math.floor(Math.log2(T));
	});

	let costDisplay = $derived(() => {
		const T = yearsFromNow();
		if (T <= 0) return '$1,000,000';
		const cost = 1_000_000 * T;
		return '$' + cost.toLocaleString('en-US');
	});

	function selectType(type: 'phrase' | 'file') {
		secretType = type;
		current = 4; // jump to step 5 (input)
	}

	function handleFileDrop(e: DragEvent) {
		e.preventDefault();
		const f = e.dataTransfer?.files[0];
		if (f) file = f;
	}

	function handleFileSelect(e: Event) {
		const input = e.target as HTMLInputElement;
		if (input.files?.[0]) file = input.files[0];
	}
</script>

<StepFlow bind:current steps={[step1, step2, step3, step4, step5, step6, step7]} />

{#snippet step1()}
	<div class="hero text-center">
		<h1 class="hero__title">Time Vault</h1>
		<p class="hero__sub">Encrypt a secret for the future</p>
		<p class="hero__hint">&#9660; Press down to begin</p>
	</div>
{/snippet}

{#snippet step2()}
	<div class="card step-card text-center">
		<h2>When should this secret be unlockable?</h2>
		<input
			type="date"
			class="input date-input"
			bind:value={unlockDate}
			min={new Date().toISOString().split('T')[0]}
		/>
		{#if yearsFromNow() > 0}
			<p class="hint">{yearsFromNow()} years from now</p>
		{/if}
	</div>
{/snippet}

{#snippet step3()}
	<div class="card step-card text-center">
		<p class="cost-label">Today it costs</p>
		<h2 class="cost-value">{costDisplay()}</h2>
		<p class="cost-label">to break this vault</p>
		<div class="cost-meta mono">
			<span>{nBits()} bits</span>
			<span>&bull;</span>
			<span>{yearsFromNow() || 1} year{yearsFromNow() > 1 ? 's' : ''} target</span>
		</div>
	</div>
{/snippet}

{#snippet step4()}
	<div class="card step-card text-center">
		<h2>What do you want to encrypt?</h2>
		<div class="type-buttons">
			<button class="btn btn--large" onclick={() => selectType('phrase')}>Phrase</button>
			<button class="btn btn--large btn--outline" onclick={() => selectType('file')}>File</button>
		</div>
	</div>
{/snippet}

{#snippet step5()}
	<div class="card step-card text-center">
		{#if secretType === 'phrase'}
			<h2>Type your secret phrase</h2>
			<textarea class="input" placeholder="Your secret..." bind:value={phrase}></textarea>
		{:else}
			<h2>Drop your file here</h2>
			<!-- svelte-ignore a11y_no_static_element_interactions -->
			<div class="dropzone" ondrop={handleFileDrop} ondragover={(e) => e.preventDefault()}>
				{#if file}
					<p class="mono">{file.name}</p>
				{:else}
					<p>Drag & drop or click to browse</p>
					<input type="file" class="dropzone__input" onchange={handleFileSelect} />
				{/if}
			</div>
		{/if}
	</div>
{/snippet}

{#snippet step6()}
	<div class="card step-card text-center">
		<h2>Support the project</h2>
		<p class="hint">Bitcoin bounty & donation — coming soon</p>
		<div class="qr-placeholder">
			<span class="mono">QR</span>
		</div>
	</div>
{/snippet}

{#snippet step7()}
	<div class="card step-card text-center">
		<h2>Your vault is ready</h2>
		<p class="hint">Encryption result will appear here</p>
		<div class="result-placeholder mono">
			<p>C = ...</p>
			<p>V = ...</p>
			<p>n = {nBits()} bits</p>
		</div>
		<a href="/timevault/decrypt" class="btn btn--outline">Go to Decrypt</a>
	</div>
{/snippet}

<style lang="scss">
	@use '$lib/styles/variables' as *;

	.hero {
		max-width: 600px;
	}

	.hero__title {
		font-size: clamp(3rem, 8vw, 6rem);
		font-weight: 800;
		letter-spacing: -0.02em;
		line-height: 1;
		margin-bottom: 0.5rem;
	}

	.hero__sub {
		font-size: clamp(1rem, 2.5vw, 1.5rem);
		color: $color-white-60;
		margin-bottom: 2rem;
	}

	.hero__hint {
		font-size: 0.875rem;
		color: $color-white-20;
		animation: pulse 2s infinite;
	}

	@keyframes pulse {
		0%, 100% { opacity: 0.3; }
		50% { opacity: 0.8; }
	}

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

	.date-input {
		max-width: 250px;
		text-align: center;
		color-scheme: dark;
	}

	.hint {
		font-size: 0.875rem;
		color: $color-white-60;
	}

	.cost-value {
		font-size: clamp(2rem, 5vw, 3.5rem);
		font-weight: 800;
	}

	.cost-label {
		font-size: 1rem;
		color: $color-white-60;
	}

	.cost-meta {
		display: flex;
		gap: 0.75rem;
		font-size: 0.875rem;
		color: $color-white-60;
	}

	.type-buttons {
		display: flex;
		gap: 1rem;
	}

	.dropzone {
		@include glass(12px, $color-white-10, $color-white-20);
		width: 100%;
		min-height: 150px;
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
		cursor: pointer;

		p {
			color: $color-white-60;
		}
	}

	.dropzone__input {
		position: absolute;
		inset: 0;
		opacity: 0;
		cursor: pointer;
	}

	.qr-placeholder {
		@include glass(12px, $color-white-10, $color-white-20);
		width: 180px;
		height: 180px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 2rem;
		color: $color-white-20;
	}

	.result-placeholder {
		@include glass(12px, $color-white-10, $color-white-20);
		width: 100%;
		padding: 1.5rem;
		text-align: left;
		font-size: 0.875rem;
		color: $color-white-60;
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}
</style>
