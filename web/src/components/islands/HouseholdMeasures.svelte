<script lang="ts">
  type Value = { value: string; label: string; tone: string };
  type Household = { id: string; short: string; description: string };
  type Measure = { id: string; title: string; status: string; year: number; href: string; values: Record<string, Value> };

  let { households, measures }: { households: Household[]; measures: Measure[] } = $props();
  let picked = $state(households[0]?.id);
  let selected = $derived(households.find((h) => h.id === picked));
</script>

<div class="panel">
  <div class="picker">
    <h2>Welcher Haushalt ist deinem am ähnlichsten?</h2>
    <p class="muted">Wähle einen Beispielhaushalt. Die Liste darunter zeigt, was sich für ihn ändert.</p>
    <div class="chips" role="group" aria-label="Beispielhaushalt wählen">
      {#each households as h (h.id)}
        <button type="button" class="chip" aria-pressed={h.id === picked} onclick={() => (picked = h.id)}>{h.short}</button>
      {/each}
    </div>
    <p class="muted desc" aria-live="polite">{selected?.description}</p>
  </div>
  <ul>
    {#each measures as m (m.id)}
      {@const v = m.values[picked]}
      <li>
        <a href={m.href}>
          <span class="what">
            <span class="title">{m.title}</span>
            <span class="muted small">{m.status}</span>
          </span>
          <span class="effect">
            <span class="muted xsmall">Im Jahr {m.year}</span>
            <span class={`value tone-${v.tone}`}>{v.value}</span>
            <span class="muted small">{v.label}</span>
          </span>
        </a>
      </li>
    {/each}
  </ul>
  <p class="muted small foot">Beträge pro Jahr für den ganzen Haushalt, gerundet. Die Karten zeigen beide Zeitpunkte: das erste volle Jahr und das fünfte Jahr.</p>
</div>

<style>
  .panel { border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }
  .picker { background: var(--surface); padding: 20px 24px; border-bottom: 1px solid var(--line); }
  h2 { margin: 0 0 4px; font-size: 18px; font-weight: 700; }
  .picker > p { margin: 0 0 16px; font-size: 15px; }
  .desc { margin: 14px 0 0 !important; font-size: 14px !important; }
  ul { list-style: none; margin: 0; padding: 0; }
  li { border-bottom: 1px solid var(--line); }
  li a { display: flex; flex-wrap: wrap; gap: 8px 32px; align-items: baseline; justify-content: space-between; padding: 20px 24px; text-decoration: none; color: var(--ink); }
  li a:hover { background: var(--surface); }
  .what { flex: 999 1 420px; min-width: 0; }
  .title { display: block; font-size: 19px; font-weight: 700; line-height: 1.3; }
  .effect { flex: 1 1 260px; text-align: right; }
  .effect > span { display: block; }
  .value { font-size: 22px; font-weight: 800; }
  .tone-nq { font-size: 18px; font-weight: 600; }
  .small { font-size: 14px; }
  .xsmall { font-size: 13px; }
  .foot { margin: 0; padding: 16px 24px; }
</style>
