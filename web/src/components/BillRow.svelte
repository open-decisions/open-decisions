<script lang="ts">
  type Row = {
    slug: string; citation: string; title: string; headline: string; kind: string; stage_text: string; step: number;
    areas: { id: string; label: string }[]; eu: { group: string; label: string | null };
    cards: { title: string; href: string }[]; next: { text: string } | null; href: string;
  };
  let { b }: { b: Row } = $props();
</script>

<li class="row">
  <a class="headline" href={b.href}>{b.headline}</a>
  {#if b.headline !== b.title}<div class="official muted">{b.title} · <span class="mono">{b.citation}</span></div>{:else}<div class="official muted"><span class="mono">{b.citation}</span> · {b.kind}</div>{/if}
  <div class="stage">
    <span class="steps" aria-hidden="true">{#each [1, 2, 3, 4, 5] as n}<span class:done={b.step >= n}></span>{/each}</span>
    <span>{b.stage_text}</span>
  </div>
  {#if b.next}<div class="next">Nächster Termin: {b.next.text}</div>{/if}
  <div class="tags">
    {#each b.areas as a}<span class="tag">{a.label}</span>{/each}
    {#if b.eu.label}<span class={`tag eu ${b.eu.group}`}>{b.eu.label}</span>{/if}
    {#each b.cards as c}<a class="tag card" href={c.href}>Was heißt das für dich: {c.title}</a>{/each}
  </div>
</li>

<style>
  .row { padding: 18px 20px; border-top: 1px solid var(--line); }
  .row:first-child { border-top: 0; }
  .headline { font-size: 18px; font-weight: 700; line-height: 1.35; color: var(--ink); text-decoration: none; }
  .headline:hover { text-decoration: underline; }
  .official { font-size: 14px; margin-top: 4px; }
  .stage { display: flex; flex-wrap: wrap; gap: 6px 12px; align-items: center; margin-top: 10px; font-size: 15px; }
  .steps { display: inline-flex; gap: 3px; width: 90px; }
  .steps span { flex: 1; height: 6px; border-radius: 3px; background: var(--line); }
  .steps span.done { background: var(--ink); }
  .next { margin-top: 6px; font-size: 14px; font-weight: 600; }
  .tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
  .tag { font-size: 13px; padding: 3px 10px; border-radius: 999px; background: var(--surface); border: 1px solid var(--line); }
  .tag.eu_law { border-color: var(--ink); }
  .tag.card { border-color: var(--ink); background: var(--bg); font-weight: 600; text-decoration: none; color: var(--ink); }
</style>
