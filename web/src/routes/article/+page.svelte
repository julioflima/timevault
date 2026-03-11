<script lang="ts">
  import { base } from "$app/paths";
</script>

<svelte:head>
  <title>Bitcoin is a Time Vault</title>
</svelte:head>

<article class="article">
  <div class="article__card card">
    <h1 class="article__title">Bitcoin is a Time Vault</h1>

    <p class="article__lead">
      Every Bitcoin wallet is, in essence, a time vault: a cryptographic secret
      protected by the computational difficulty of reversing elliptic curves.
      Today's hardware cannot derive a private key from a public key — but
      advances in quantum computing or classical hardware will eventually break
      that protection.
    </p>

    <h2>Satoshi's Wallets</h2>

    <p>
      Satoshi Nakamoto mined approximately 1.1 million BTC between 2009 and 2010
      using <strong>P2PK (Pay-to-Public-Key)</strong> addresses — the oldest
      Bitcoin format, where the <em>public key is exposed directly</em>
      in the transaction output script. Unlike modern formats (P2PKH, P2WPKH) that
      publish only a hash of the public key, P2PK addresses reveal the complete blueprint
      for an attack.
    </p>

    <p>
      Around 1.72 million BTC in legacy P2PK addresses — including Satoshi's —
      are vulnerable to a quantum attack. Anyone who builds a sufficiently
      powerful quantum computer could:
    </p>

    <ol>
      <li>
        Harvest the exposed public keys from the blockchain (they're public)
      </li>
      <li>Run Shor's algorithm to derive the private keys</li>
      <li>Transfer the funds</li>
    </ol>

    <p>
      Bitcoin developers proposed <strong>BIP-360</strong> for quantum-resistant
      address migration, acknowledging the threat is real — it's only a matter
      of <em>when</em>, not <em>if</em>.
    </p>

    <h2>Making It Intentional</h2>

    <p>
      The Time Vault protocol makes this pattern <strong
        >intentional and quantifiable</strong
      >. Instead of hoping encryption never breaks, we design secrets that are
      secure today but will become breakable as hardware improves — with a
      <em>predictable cost curve</em>.
    </p>

    <p>The cost to break a vault follows a simple formula:</p>

    <div class="article__formula">
      Cost(n, t₀) = $1M × 2<sup>(n − B(t₀))</sup>
    </div>

    <p>
      Where <em>n</em> is the seed length in bits, and <em>B(t₀)</em> is a
      benchmark of how many bits $1M in GPUs can brute-force in one year at time
      <em>t₀</em>. This benchmark is fitted to 80 years of hardware data — from
      ENIAC (1945) to RTX 5090 (2025) — using a logistic curve that captures the
      S-shaped trajectory of computational progress.
    </p>

    <h2>The Benchmark Plateau</h2>

    <p>
      Since ~2016, the cost-per-hash on GPUs has stagnated. GPUs get faster, but
      proportionally more expensive. The ceiling of ~67 bits per $1M/year has
      held stable for a decade. This plateau makes Time Vault predictions
      remarkably reliable in the near term.
    </p>

    <p>
      But nothing lasts forever. Quantum computing, novel architectures, or
      algorithmic breakthroughs could shatter the plateau — just as they could
      shatter Bitcoin's elliptic curve security.
    </p>

    <h2>Every Wallet Is a Time Vault</h2>

    <p>
      The difference is that Bitcoin wallets were designed to <em>never</em>
      be broken. Time Vault embraces the inevitable: encryption degrades, and that
      degradation can be turned into a feature. A secret encrypted today with a 10-year
      target will cost $8M to break now, but will become affordable as hardware catches
      up.
    </p>

    <p>
      On the Bitcoin blockchain, this creates a <strong
        >proof-of-crack ledger</strong
      >: a vault is created (V in OP_RETURN), a bounty is locked (P2WSH
      hashlock), and when the vault is broken, the seed S is permanently
      revealed in the spending transaction's witness data.
    </p>

    <div class="article__actions">
      <a
        class="btn"
        href="{base}/whitepaper.pdf"
        target="_blank"
        rel="noopener"
      >
        Read the Whitepaper (PDF)
      </a>
      <a class="btn btn--outline" href="{base}/"> Encrypt a Secret </a>
    </div>
  </div>
</article>

<style lang="scss">
  @use "$lib/styles/variables" as *;

  .article {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    padding: 4rem 1.5rem;
    position: relative;
    z-index: 1;
  }

  .article__card {
    max-width: 720px;
    width: 100%;
    padding: 3rem 2.5rem;

    h2 {
      font-size: 1.5rem;
      font-weight: 700;
      color: $color-black;
      margin: 2.5rem 0 1rem;
    }

    p {
      font-size: 1.1rem;
      line-height: 1.75;
      color: $color-black-80;
      margin-bottom: 1rem;
    }

    ol {
      margin: 0.5rem 0 1.5rem 1.5rem;
      color: $color-black-80;
      font-size: 1.05rem;
      line-height: 1.75;

      li {
        margin-bottom: 0.25rem;
      }
    }

    strong {
      color: $color-black;
    }

    em {
      font-style: italic;
    }
  }

  .article__title {
    font-family: "Kalam", cursive;
    font-size: clamp(2.2rem, 6vw, 3.5rem);
    font-weight: 700;
    line-height: 1.1;
    color: $color-black;
    margin-bottom: 1.5rem;
  }

  .article__lead {
    font-size: 1.2rem !important;
    color: $color-black !important;
    line-height: 1.8 !important;
    margin-bottom: 2rem !important;
  }

  .article__formula {
    @include glass(10px, $color-white-20, $color-white-20);
    padding: 1.25rem 1.5rem;
    font-family: $font-mono;
    font-size: 1.1rem;
    text-align: center;
    color: $color-black;
    margin: 1.5rem 0;

    sup {
      font-size: 0.75em;
    }
  }

  .article__actions {
    display: flex;
    gap: 1rem;
    margin-top: 3rem;
    flex-wrap: wrap;
  }

  .btn--outline {
    background: transparent;
    color: $color-black;
    border: 2px solid $color-black;

    &:hover {
      background: $color-black;
      color: $color-white;
    }
  }
</style>
