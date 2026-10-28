<script lang="ts">
  import BillRow from "../BillRow.svelte";

  type Bill = {
    id: string; slug: string; citation: string; title: string; headline: string; type: string; kind: string; stage: string;
    step: number; stage_text: string; areas: { id: string; label: string }[]; happening: string[];
    next: { date: string; text: string } | null; introduced: string;
    eu: { group: string; label: string | null }; cards: { title: string; href: string }[]; href: string;
  };
  type Filter = { id: string; label: string; count: number };

  let { bills, stages, types, eus, areas, total }: { bills: Bill[]; stages: Filter[]; types: Filter[]; eus: Filter[]; areas: Filter[]; total: number } = $props();
  let view = $state<"now" | "all">("now");
  let stage = $state("all");
  let type = $state("all");
  let eu = $state("all");
  let area = $state("all");
  let query = $state("");

  const upcoming = bills.filter((b) => b.happening.includes("upcoming")).sort((a, b) => (a.next?.date ?? "").localeCompare(b.next?.date ?? ""));
  const decided = bills.filter((b) => b.happening.includes("decided") && !b.happening.includes("upcoming"));
  const fresh = bills.filter((b) => b.happening.includes("new") && !b.happening.includes("upcoming"));

  let rows = $derived.by(() => {
    const q = query.trim().toLowerCase();
    return bills.filter(
      (b) =>
        (stage === "all" || b.stage === stage) &&
        (type === "all" || b.type === type) &&
        (eu === "all" || b.eu.group === eu) &&
        (area === "all" || b.areas.some((a) => a.id === area)) &&
        (!q || b.headline.toLowerCase().includes(q) || b.title.toLowerCase().includes(q) || b.citation.toLowerCase().includes(q)),
    );
  });
  const more = $derived([stage, type, eu].filter((x) => x !== "all").length);
</script>

<div class="switch" role="group" aria-label="Ansicht">
  <button type="button" aria-pressed={view === "now"} onclick={() => (view = "now")}>Was gerade passiert</button>
  <button type="button" aria-pressed={view === "all"} onclick={() => (view = "all")}>Alle {total} Vorhaben</button>
</div>

{#if view === "now"}
  <section aria-labelledby="h-up" class="group">
    <h3 id="h-up">Demnächst auf der Tagesordnung <span class="n">{upcoming.length}</span></h3>
    {#if upcoming.length}<ul class="list">{#each upcoming as b (b.id)}<BillRow {b} />{/each}</ul>{:else}<p class="muted empty">Derzeit keine Termine in den Daten.</p>{/if}
  </section>
  <section aria-labelledby="h-dec" class="group">
    <h3 id="h-dec">In den letzten 30 Tagen beschlossen <span class="n">{decided.length}</span></h3>
    {#if decided.length}<ul class="list">{#each decided as b (b.id)}<BillRow {b} />{/each}</ul>{:else}<p class="muted empty">Keine Beschlüsse in den letzten 30 Tagen.</p>{/if}
  </section>
  <section aria-labelledby="h-new" class="group">
    <h3 id="h-new">Neu eingebracht <span class="n">{fresh.length}</span></h3>
    {#if fresh.length}<ul class="list">{#each fresh as b (b.id)}<BillRow {b} />{/each}</ul>{:else}<p class="muted empty">In den letzten drei Wochen nichts Neues.</p>{/if}
  </section>
{:else}
  <div class="filters">
    <div>
      <label for="q">Suche</label>
      <input id="q" type="search" bind:value={query} placeholder="zum Beispiel Familienbeihilfe" autocomplete="off" />
    </div>
    <div>
      <span class="flabel" id="area-label">Lebensbereich</span>
      <div class="chips" role="group" aria-labelledby="area-label">
        <button type="button" class="chip" aria-pressed={area === "all"} onclick={() => (area = "all")}>Alle</button>
        {#each areas as a (a.id)}<button type="button" class="chip" aria-pressed={area === a.id} onclick={() => (area = a.id)}>{a.label} <span class="n">{a.count}</span></button>{/each}
      </div>
    </div>
    <details>
      <summary>Weitere Filter{#if more} ({more} aktiv){/if}</summary>
      <div class="more">
        <span class="flabel" id="stage-label">Stand</span>
        <div class="chips" role="group" aria-labelledby="stage-label">
          <button type="button" class="chip" aria-pressed={stage === "all"} onclick={() => (stage = "all")}>Alle</button>
          {#each stages as s (s.id)}<button type="button" class="chip" aria-pressed={stage === s.id} onclick={() => (stage = s.id)}>{s.label} <span class="n">{s.count}</span></button>{/each}
        </div>
        <span class="flabel" id="eu-label">Bezug zur EU</span>
        <div class="chips" role="group" aria-labelledby="eu-label">
          <button type="button" class="chip" aria-pressed={eu === "all"} onclick={() => (eu = "all")}>Alle</button>
          {#each eus as e (e.id)}<button type="button" class="chip" aria-pressed={eu === e.id} onclick={() => (eu = e.id)}>{e.label} <span class="n">{e.count}</span></button>{/each}
        </div>
        <span class="flabel" id="type-label">Wer hat es eingebracht</span>
        <div class="chips" role="group" aria-labelledby="type-label">
          <button type="button" class="chip" aria-pressed={type === "all"} onclick={() => (type = "all")}>Alle</button>
          {#each types as t (t.id)}<button type="button" class="chip" aria-pressed={type === t.id} onclick={() => (type = t.id)}>{t.label} <span class="n">{t.count}</span></button>{/each}
        </div>
      </div>
    </details>
  </div>
  <p class="muted count" aria-live="polite">{rows.length} von {total} Vorhaben</p>
  <ul class="list all">{#each rows as b (b.id)}<BillRow {b} />{/each}</ul>
{/if}

<style>
  .switch { display: inline-grid; grid-template-columns: 1fr 1fr; gap: 4px; padding: 4px; background: var(--surface); border-radius: 12px; margin-bottom: 24px; max-width: 100%; }
  .switch button { min-height: 44px; padding: 8px 16px; border-radius: 9px; border: 0; background: transparent; font-size: 16px; font-weight: 500; cursor: pointer; color: var(--muted); }
  .switch button[aria-pressed="true"] { background: var(--bg); color: var(--ink); font-weight: 700; box-shadow: 0 0 0 1px var(--line); }
  .group { margin-bottom: 32px; }
  h3 { margin: 0 0 10px; font-size: 18px; font-weight: 800; }
  .n { opacity: 0.7; font-weight: 500; }
  .list { list-style: none; margin: 0; padding: 0; border: 1px solid var(--line); border-radius: 12px; }
  .empty { margin: 0; font-size: 15px; }
  .filters { display: flex; flex-direction: column; gap: 16px; margin-bottom: 16px; }
  label, .flabel { display: block; font-size: 14px; font-weight: 600; margin-bottom: 6px; }
  input { width: 100%; max-width: 480px; min-height: 44px; padding: 10px 14px; border: 2px solid var(--control); border-radius: 8px; font-size: 16px; background: var(--bg); }
  details summary { cursor: pointer; font-weight: 600; min-height: 44px; display: flex; align-items: center; }
  .more { display: flex; flex-direction: column; gap: 6px; padding-top: 8px; }
  .more .chips { margin-bottom: 10px; }
  .count { margin: 0 0 10px; font-size: 14px; }
</style>
