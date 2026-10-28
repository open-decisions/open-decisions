<script lang="ts">
  type Bill = {
    id: string; citation: string; title: string; type: string; kind: string; introduced_text: string;
    stage: string; step: number; step_label: string; parliament_url: string;
    cards: { title: string; href: string }[];
    eu: { group: string; label: string | null; goes_beyond_text: string | null; acts: { label: string; url: string }[] };
  };
  type Filter = { id: string; label: string; count: number };

  let { bills, stages, types, eus, total }: { bills: Bill[]; stages: Filter[]; types: Filter[]; eus: Filter[]; total: number } = $props();
  let stage = $state("all");
  let type = $state("all");
  let query = $state("");
  let eu = $state("all");
  let rows = $derived.by(() => {
    const q = query.trim().toLowerCase();
    return bills.filter((b) => (stage === "all" || b.stage === stage) && (type === "all" || b.type === type) && (eu === "all" || b.eu.group === eu) && (!q || b.title.toLowerCase().includes(q) || b.citation.toLowerCase().includes(q)));
  });
</script>

<div class="filters">
  <div>
    <label for="q">Suche in Titel und Nummer</label>
    <input id="q" type="search" bind:value={query} placeholder="zum Beispiel Familienbeihilfe" autocomplete="off" />
  </div>
  <div class="chips" role="group" aria-label="Stand">
    <button type="button" class="chip" aria-pressed={stage === "all"} onclick={() => (stage = "all")}>Alle <span class="n">{total}</span></button>
    {#each stages as s (s.id)}
      <button type="button" class="chip" aria-pressed={stage === s.id} onclick={() => (stage = s.id)}>{s.label} <span class="n">{s.count}</span></button>
    {/each}
  </div>
  <div class="chips" role="group" aria-label="Art">
    <button type="button" class="chip" aria-pressed={type === "all"} onclick={() => (type = "all")}>Alle Arten <span class="n">{total}</span></button>
    {#each types as t (t.id)}
      <button type="button" class="chip" aria-pressed={type === t.id} onclick={() => (type = t.id)}>{t.label} <span class="n">{t.count}</span></button>
    {/each}
  </div>
  <div class="chips" role="group" aria-label="Bezug zum EU-Recht">
    <button type="button" class="chip" aria-pressed={eu === "all"} onclick={() => (eu = "all")}>EU-Bezug egal <span class="n">{total}</span></button>
    {#each eus as e (e.id)}
      <button type="button" class="chip" aria-pressed={eu === e.id} onclick={() => (eu = e.id)}>{e.label} <span class="n">{e.count}</span></button>
    {/each}
  </div>
</div>

<p class="muted count" aria-live="polite">{rows.length} von {total} Vorhaben</p>

<div class="table-wrap" tabindex="0" role="region" aria-label="Liste der Gesetzesvorhaben">
  <table>
    <thead>
      <tr>
        <th scope="col" class="c-nr">Nummer</th>
        <th scope="col">Vorhaben</th>
        <th scope="col" class="c-weg">Weg</th>
        <th scope="col" class="c-karten">Karten</th>
      </tr>
    </thead>
    <tbody>
      {#each rows as b (b.id)}
        <tr>
          <td class="mono muted nr">{b.citation}</td>
          <td>
            <a class="title" href={b.parliament_url}>{b.title}</a>
            <div class="muted meta">{b.kind} · eingebracht {b.introduced_text}</div>
            {#if b.eu.label}
              <div class="eu">
                <span class={`eu-tag ${b.eu.group}`}>{b.eu.label}</span>
                {#each b.eu.acts as a}<a class="eu-act" href={a.url}>{a.label}</a>{/each}
                {#if b.eu.goes_beyond_text}<span class="eu-beyond">{b.eu.goes_beyond_text}</span>{/if}
              </div>
            {/if}
          </td>
          <td>
            <div class="steps" role="img" aria-label={b.step_label}>
              {#each [1, 2, 3, 4, 5] as n}<span class:done={b.step >= n}></span>{/each}
            </div>
            <div class="muted meta">{b.step_label}</div>
          </td>
          <td class="meta">
            {#if b.cards.length}
              {#each b.cards as c}<a class="card-link" href={c.href}>{c.title}</a>{/each}
            {:else}<span class="muted">keine</span>{/if}
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>

<style>
  .filters { display: flex; flex-direction: column; gap: 14px; margin-bottom: 16px; }
  label { display: block; font-size: 14px; font-weight: 600; margin-bottom: 6px; }
  input { width: 100%; max-width: 480px; min-height: 44px; padding: 10px 14px; border: 2px solid var(--control); border-radius: 8px; font-size: 16px; background: var(--bg); }
  .n { opacity: 0.75; }
  .count { margin: 0 0 10px; font-size: 14px; }
  table { min-width: 760px; }
  td { padding: 14px 16px; }
  th { padding: 12px 16px; }
  .c-nr { width: 110px; } .c-weg { width: 200px; } .c-karten { width: 200px; }
  .nr { font-size: 14px; }
  .title { font-weight: 600; line-height: 1.35; color: var(--ink); text-decoration-color: var(--control); }
  .meta { font-size: 14px; margin-top: 3px; }
  .steps { display: flex; gap: 4px; margin: 4px 0 6px; }
  .steps span { flex: 1 1 0; height: 8px; border-radius: 4px; background: var(--line); }
  .steps span.done { background: var(--ink); }
  .card-link { display: block; font-weight: 600; margin-bottom: 4px; }
  .eu { display: flex; flex-wrap: wrap; gap: 6px 10px; align-items: center; margin-top: 6px; font-size: 13px; }
  .eu-tag { padding: 2px 8px; border-radius: 999px; border: 1px solid var(--line); background: var(--surface); font-weight: 600; }
  .eu-tag.eu_law { border-color: var(--ink); }
  .eu-act { font-weight: 500; }
  .eu-beyond { color: var(--muted); }
</style>
