<script lang="ts">
  import { onMount } from "svelte";
  import StepFlow from "$lib/components/StepFlow.svelte";
  import { preload, decryptVault } from "$lib/pyodide";

  let current = $state(0);
  let seedHex = $state("");
  let vaultInput = $state("");
  let decrypting = $state(false);
  let decryptedText = $state("");
  let error = $state("");

  async function startDecrypt() {
    if (decrypting || !vaultInput || !seedHex) return;
    decrypting = true;
    error = "";
    try {
      decryptedText = await decryptVault(vaultInput, seedHex.trim());
    } catch (err) {
      error = err instanceof Error ? err.message : "Decryption failed";
    } finally {
      decrypting = false;
    }
  }

  onMount(() => {
    preload();
  });
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
    <textarea
      class="input"
      placeholder="Paste vault JSON here..."
      bind:value={vaultInput}
    ></textarea>
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
    {#if decrypting}
      <h2>Decrypting...</h2>
      <div class="spinner"></div>
    {:else if error}
      <h2>Decryption failed</h2>
      <p class="error">{error}</p>
      <button
        class="btn btn--outline"
        onclick={() => {
          error = "";
          current = 2;
        }}>Try again</button
      >
    {:else if decryptedText}
      <h2>Decrypted secret</h2>
      <div class="result mono">{decryptedText}</div>
    {:else}
      <h2>Decrypt</h2>
      <button class="btn btn--large" onclick={startDecrypt}>Decrypt now</button>
    {/if}
  </div>
{/snippet}

<style lang="scss">
  @use "$lib/styles/variables" as *;

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
    word-break: break-all;
  }

  .error {
    color: #ff6b6b;
    font-size: 0.875rem;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid $color-white-20;
    border-top-color: $color-white;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
