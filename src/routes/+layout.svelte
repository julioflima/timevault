<script lang="ts">
	import type { Snippet } from 'svelte';
	import '$lib/styles/global.scss';

	let { children }: { children: Snippet } = $props();
</script>

<div class="bg-ambient"></div>
<div class="bg-image"></div>
{@render children()}
