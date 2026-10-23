<script lang="ts">
  type Amount = { value: string; label: string; sub: string; tone: string; lo: number | null; hi: number | null };
  type Row = { id: string; short: string; description: string; shortTerm: Amount; longTerm: Amount; note?: string | null };

  let { rows, years, variant = "chips" }: { rows: Row[]; years: { short: number; long: number }; variant?: "chips" | "select" } = $props();
  let picked = $state(rows[0]?.id);
  let sel = $derived(rows.find((r) => r.id === picked) ?? rows[0]);
  const max = Math.max(1, ...rows.map((r) => Math.max(Math.abs(r.shortTerm.lo ?? 0), Math.abs(r.shortTerm.hi ?? 0))));
  const hasBars = rows.some((r) => (r.shortTerm.hi ?? 0) !== 0);
  const anyRange = rows.some((r) => r.shortTerm.lo !== r.shortTerm.hi);
  function bar(a: Amount) {
    const lo = Math.abs(a.lo ?? 0), hi = Math.abs(a.hi ?? 0);
    return { solid: (Math.min(lo, hi) / max) * 100, range: (Math.abs(hi - lo) / max) * 100 };
  }
</script>

<div class="result">
  {#if variant === "select"}
    <label for="hh-select">Mein Haushalt ist am ähnlichsten</label>
    <select id="hh-select" bind:value={picked}>
      {#each rows as r (r.id)}<option value={r.id}>{r.short}</option>{/each}
    </select>
  {:else}
    <span class="label" id="hh-label">Beispielhaushalt</span>
    <div class="chips" role="group" aria-labelledby="hh-label">
      {#each rows as r (r.id)}
        <button type="button" class="chip" aria-pressed={r.id === picked} onclick={() => (picked = r.id)}>{r.short}</button>
      {/each}
    </div>
  {/if}
  <p class="muted desc">{sel.description}</p>
  <div class="years" aria-live="polite">
    <div>
      <div class="muted small">Im Jahr {years.short}</div>
      <div class={`big tone-${sel.shortTerm.tone}`}>{sel.shortTerm.value}</div>
      <div class="muted small">{#if sel.shortTerm.sub}{sel.shortTerm.sub} · {/if}{sel.shortTerm.label}</div>
    </div>
    {#if variant === "chips"}
      <div>
        <div class="muted small">Im Jahr {years.long}</div>
        <div class={`big tone-${sel.longTerm.tone}`}>{sel.longTerm.value}</div>
        <div class="muted small">{#if sel.longTerm.sub}{sel.longTerm.sub} · {/if}{sel.longTerm.label}</div>
      </div>
    {/if}
  </div>
  {#if sel.note}<p class="muted note">{sel.note}</p>{/if}
</div>

<h3>Alle Beispielhaushalte im Vergleich</h3>
<ul class="compare">
  {#each rows as r (r.id)}
    {@const b = bar(r.shortTerm)}
    <li class:on={r.id === picked}>
      <span class="name">{r.short}</span>
      {#if hasBars}
        <span class="track" aria-hidden="true">
          <span class={`solid ${r.shortTerm.tone}`} style={`width:${b.solid}%`}></span><span class={`range ${r.shortTerm.tone}`} style={`width:${b.range}%`}></span>
        </span>
      {/if}
      <span class="val">{r.shortTerm.value}</span>
    </li>
  {/each}
</ul>
<p class="muted small">
  Im Jahr {years.short}, pro Jahr und Haushalt, gerundet.
  {#if hasBars && anyRange}Dunkel: sicherer Teil. Hell: Spanne, weil eine Annahme dahintersteht.{/if}
</p>

<style>
  .result { border: 2px solid var(--ink); border-radius: 12px; padding: 22px 24px; margin-bottom: 20px; }
  .label, label { display: block; font-size: 14px; font-weight: 600; color: var(--muted); margin-bottom: 8px; }
  select { width: 100%; min-height: 48px; padding: 10px 12px; border: 2px solid var(--control); border-radius: 8px; background: var(--bg); font-size: 16px; }
  .desc { margin: 16px 0 14px; font-size: 15px; }
  .years { display: flex; flex-wrap: wrap; gap: 16px 48px; }
  .big { font-size: 32px; font-weight: 800; letter-spacing: -0.01em; line-height: 1.2; }
  .big.tone-nq { font-size: 22px; }
  .small { font-size: 15px; }
  .note { margin: 16px 0 0; font-size: 15px; }
  h3 { margin: 0 0 10px; font-size: 16px; font-weight: 700; }
  .compare { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 12px; }
  .compare li { display: flex; flex-wrap: wrap; gap: 4px 16px; align-items: center; }
  .name { flex: 0 0 230px; font-size: 15px; color: var(--muted); }
  .on .name { font-weight: 700; color: var(--ink); }
  .track { flex: 999 1 200px; display: flex; height: 14px; background: var(--surface); border-radius: 4px; overflow: hidden; }
  .solid.minus { background: var(--minus-soft); } .on .solid.minus { background: var(--minus); }
  .solid.plus { background: var(--plus-soft); } .on .solid.plus { background: var(--plus); }
  .range { background: var(--range); }
  .range.plus { background: #C9D6F6; }
  .val { flex: 0 0 190px; text-align: right; font-size: 15px; font-weight: 600; }
</style>
