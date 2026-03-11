<script lang="ts">
  import type { Snippet } from "svelte";
  import { base } from "$app/paths";
  import "$lib/styles/global.scss";

  let { children }: { children: Snippet } = $props();
</script>

<nav class="site-nav">
  <a href="{base}/" class="site-nav__brand">Time Vault</a>
  <div class="site-nav__links">
    <a href="{base}/">Encrypt</a>
    <a href="{base}/decrypt">Decrypt</a>
    <a href="{base}/article">Article</a>
    <a href="{base}/whitepaper.pdf" target="_blank" rel="noopener">Whitepaper</a
    >
  </div>
</nav>

<div class="bg-ambient"></div>
<div class="bg-image"></div>
{@render children()}

<style lang="scss">
  @use "$lib/styles/variables" as *;

  .site-nav {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1.5rem;
    @include glass(16px, rgba(255, 255, 255, 0.08), $color-white-10);
    border-radius: 0;
    border-top: none;
    border-left: none;
    border-right: none;
  }

  .site-nav__brand {
    font-family: "Kalam", cursive;
    font-size: 1.25rem;
    font-weight: 700;
    color: $color-black;
    text-decoration: none;
  }

  .site-nav__links {
    display: flex;
    gap: 1.5rem;

    a {
      font-size: 0.85rem;
      font-weight: 500;
      color: $color-black-80;
      text-decoration: none;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      transition: color $transition-fast;

      &:hover {
        color: $color-black;
      }
    }
  }
</style>
