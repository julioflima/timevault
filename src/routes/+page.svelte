<script lang="ts">
  import { onMount } from "svelte";
  import StepFlow from "$lib/components/StepFlow.svelte";
  import {
    preload,
    calcParams,
    encryptPhrase,
    encryptFile,
    type VaultResult,
  } from "$lib/pyodide";
  import { publishVault, isTokenConfigured, type VaultFile } from "$lib/github";
  import {
    computeBitcoinInfo,
    isDonationConfigured,
    type BitcoinInfo,
  } from "$lib/bitcoin";

  let current = $state(0);
  let unlockDate = $state("");
  let secretType = $state<"phrase" | "file" | null>(null);
  let phrase = $state("");
  let file = $state<File | null>(null);

  let encrypting = $state(false);
  let vaultResult = $state<VaultResult | null>(null);
  let pyReady = $state(false);
  let pyLoading = $state(false);

  let publishing = $state(false);
  let published = $state(false);
  let publishError = $state("");

  let btcInfo = $state<BitcoinInfo | null>(null);

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
    if (T <= 0) return "$1,000,000";
    const cost = 1_000_000 * T;
    return "$" + cost.toLocaleString("en-US");
  });

  function selectType(type: "phrase" | "file") {
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

  async function startEncrypt() {
    if (encrypting) return;
    encrypting = true;
    pyLoading = !pyReady;

    try {
      const t0 = new Date().getFullYear();
      const T = yearsFromNow();

      if (secretType === "phrase") {
        vaultResult = await encryptPhrase(phrase, t0, T || 1);
      } else if (file) {
        const buf = new Uint8Array(await file.arrayBuffer());
        vaultResult = await encryptFile(buf, t0, T || 1);
      }
      pyReady = true;
      pyLoading = false;

      // Compute Bitcoin info if donation is configured
      if (vaultResult && isDonationConfigured()) {
        btcInfo = await computeBitcoinInfo(vaultResult.V, vaultResult.S);
      }
    } catch (err) {
      console.error("Encryption failed:", err);
    } finally {
      encrypting = false;
    }
  }

  function downloadVault() {
    if (!vaultResult) return;
    const { S, ...vault } = vaultResult;
    const blob = new Blob([JSON.stringify(vault, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `vault_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  async function publish() {
    if (!vaultResult || publishing || published) return;
    publishing = true;
    publishError = "";
    try {
      const { S, ...vault } = vaultResult;
      const result = await publishVault(vaultResult.V, vault as VaultFile);
      if (result.ok) {
        published = true;
      } else {
        publishError = result.message;
      }
    } catch (err) {
      publishError = err instanceof Error ? err.message : "Publish failed";
    } finally {
      publishing = false;
    }
  }

  onMount(() => {
    preload();
  });
</script>

<StepFlow
  bind:current
  steps={[step1, step2, step3, step4, step5, step6, step7]}
/>

{#snippet step1()}
  <div class="hero text-center">
    <h1 class="hero__title">Time Vault</h1>
    <p class="hero__sub">Encrypt a secret for the future</p>
    <button
      class="hero__arrow"
      onclick={() => (current = 1)}
      aria-label="Begin"
    >
      <span class="hero__arrow-icon">&#8595;</span>
      <span class="hero__arrow-text">press enter</span>
    </button>
  </div>
{/snippet}

{#snippet step2()}
  <div class="card step-card text-center">
    <h2>When should this secret be unlockable?</h2>
    <input
      type="date"
      class="input date-input"
      bind:value={unlockDate}
      min={new Date().toISOString().split("T")[0]}
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
      <span
        >{yearsFromNow() || 1} year{yearsFromNow() > 1 ? "s" : ""} target</span
      >
    </div>
  </div>
{/snippet}

{#snippet step4()}
  <div class="card step-card text-center">
    <h2>What do you want to encrypt?</h2>
    <div class="type-buttons">
      <button class="btn btn--large" onclick={() => selectType("phrase")}
        >Phrase</button
      >
      <button
        class="btn btn--large btn--outline"
        onclick={() => selectType("file")}>File</button
      >
    </div>
  </div>
{/snippet}

{#snippet step5()}
  <div class="card step-card text-center">
    {#if secretType === "phrase"}
      <h2>Type your secret phrase</h2>
      <textarea class="input" placeholder="Your secret..." bind:value={phrase}
      ></textarea>
    {:else}
      <h2>Drop your file here</h2>
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <div
        class="dropzone"
        ondrop={handleFileDrop}
        ondragover={(e) => e.preventDefault()}
      >
        {#if file}
          <p class="mono">{file.name}</p>
        {:else}
          <p>Drag & drop or click to browse</p>
          <input
            type="file"
            class="dropzone__input"
            onchange={handleFileSelect}
          />
        {/if}
      </div>
    {/if}
  </div>
{/snippet}

{#snippet step6()}
  <div class="card step-card text-center">
    <h2>Support the project</h2>
    {#if btcInfo?.qrDataURL}
      <p class="hint">Scan to fund the Bitcoin bounty for this vault</p>
      <img class="qr-img" src={btcInfo.qrDataURL} alt="Bitcoin QR code" />
      <p class="mono btc-addr">{btcInfo.p2wshAddress}</p>
      <p class="hint">P2WSH hashlock — anyone who cracks S can claim this bounty</p>
    {:else}
      <p class="hint">Bitcoin bounty — encrypt first, then fund</p>
      <div class="qr-placeholder">
        <span class="mono">QR</span>
      </div>
      {#if !isDonationConfigured()}
        <p class="hint">Donation address not configured yet</p>
      {/if}
    {/if}
  </div>
{/snippet}

{#snippet step7()}
  <div class="card step-card text-center">
    {#if encrypting}
      <h2>{pyLoading ? "Loading crypto engine..." : "Encrypting..."}</h2>
      <div class="spinner"></div>
    {:else if vaultResult}
      <h2>Your vault is ready</h2>
      <div class="result-box mono">
        <p><strong>n</strong> = {vaultResult.n} bits</p>
        <p class="truncate"><strong>V</strong> = {vaultResult.V}</p>
        <p class="truncate">
          <strong>C</strong> = {vaultResult.C.slice(0, 40)}...
        </p>
      </div>
      <div class="seed-box">
        <p class="seed-label">
          Save this seed — it is the <strong>only</strong> way to decrypt:
        </p>
        <code class="seed mono">{vaultResult.S}</code>
      </div>
      <div class="result-actions">
        <button class="btn" onclick={downloadVault}>Download vault</button>
        {#if isTokenConfigured()}
          {#if published}
            <span class="publish-ok">Published ✓</span>
          {:else}
            <button
              class="btn btn--outline"
              onclick={publish}
              disabled={publishing}
              >{publishing ? "Publishing..." : "Publish to GitHub"}</button
            >
          {/if}
        {/if}
        <a href="/timevault/decrypt" class="btn btn--outline">Go to Decrypt</a>
      </div>
      {#if publishError}
        <p class="publish-error">{publishError}</p>
      {/if}
    {:else}
      <h2>Your vault is ready</h2>
      <p class="hint">Press Enter or click below to encrypt</p>
      <button class="btn btn--large" onclick={startEncrypt}>Encrypt now</button>
    {/if}
  </div>
{/snippet}

<style lang="scss">
  @use "$lib/styles/variables" as *;

  .hero {
    max-width: 600px;
  }

  .hero__title {
    font-family: "Kalam", cursive;
    font-size: clamp(3rem, 8vw, 6rem);
    font-weight: 700;
    letter-spacing: -0.01em;
    line-height: 1;
    margin-bottom: 0.5rem;
    color: $color-black;
  }

  .hero__sub {
    font-size: clamp(1rem, 2.5vw, 1.5rem);
    color: $color-white-60;
    margin-bottom: 3rem;
  }

  .hero__arrow {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    background: none;
    border: none;
    cursor: pointer;
    color: $color-white-60;
    animation: bounce 2s infinite;
  }

  .hero__arrow-icon {
    font-size: 2rem;
    line-height: 1;
  }

  .hero__arrow-text {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-family: $font-mono;
  }

  @keyframes bounce {
    0%,
    20%,
    50%,
    80%,
    100% {
      transform: translateY(0);
    }
    40% {
      transform: translateY(-12px);
    }
    60% {
      transform: translateY(-6px);
    }
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

  .qr-img {
    width: 200px;
    height: 200px;
    border-radius: 8px;
  }

  .btc-addr {
    font-size: 0.65rem;
    color: $color-white-60;
    word-break: break-all;
    max-width: 100%;
  }

  .result-box {
    @include glass(12px, $color-white-10, $color-white-20);
    width: 100%;
    padding: 1.5rem;
    text-align: left;
    font-size: 0.875rem;
    color: $color-white-60;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;

    strong {
      color: $color-white;
    }
  }

  .truncate {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .seed-box {
    width: 100%;
    text-align: center;
  }

  .seed-label {
    font-size: 0.875rem;
    color: $color-white-60;
    margin-bottom: 0.5rem;
  }

  .seed {
    display: block;
    padding: 0.75rem 1rem;
    background: $color-white-10;
    border-radius: 8px;
    font-size: 0.75rem;
    word-break: break-all;
    user-select: all;
    color: $color-white;
  }

  .result-actions {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    justify-content: center;
  }

  .publish-ok {
    color: #4caf50;
    font-size: 0.875rem;
    font-weight: 600;
  }

  .publish-error {
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
