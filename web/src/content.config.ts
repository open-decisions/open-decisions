import { defineCollection } from "astro:content";
import { file, glob } from "astro/loaders";
import { z } from "astro/zod";

const amount = z.object({
  main: z.string(),
  sub: z.string(),
  value: z.string(),
  label: z.enum(["gerechnet", "übernommen", "geschätzt", "nicht bezifferbar"]),
  tone: z.enum(["minus", "plus", "zero", "nq"]),
  lo: z.number().nullable(),
  hi: z.number().nullable(),
});

const link = z.object({ title: z.string(), url: z.url(), ref: z.string() });

const cards = defineCollection({
  loader: glob({ pattern: "*.json", base: "./src/generated/cards" }),
  schema: z.object({
    id: z.string(),
    lang: z.string(),
    title: z.string(),
    status: z.string(),
    status_parts: z.object({ state: z.string(), bill_title: z.string(), citation: z.string(), article: z.string() }),
    topic: z.string(),
    approved: z.boolean(),
    said: z.object({ quote: z.string(), speaker: z.string(), role: z.string(), date: z.string(), sources: z.array(link) }),
    law: z.string(),
    years: z.object({ short: z.number(), long: z.number() }),
    households: z.array(
      z.object({
        id: z.string(),
        label: z.string(),
        short: amount,
        long: amount,
        share: z.string().nullable(),
        note: z.string().nullable().optional(),
        detail_short: z.string(),
        detail_long: z.string(),
      }),
    ),
    unclear: z.array(z.string()).min(1),
    follow_up: z.object({ date: z.string(), iso: z.string(), what: z.string() }),
    vote: z
      .object({
        date: z.string(),
        yes: z.object({ seats: z.number(), parties: z.array(z.string()) }),
        no: z.object({ seats: z.number(), parties: z.array(z.string()) }),
        share_yes: z.number(),
      })
      .nullable(),
    path: z.array(z.object({ label: z.string(), detail: z.string() })),
    detail: z.looseObject({
      parameters: z.array(z.object({ name: z.string(), old: z.string(), new: z.string(), applies_from: z.string(), sources: z.array(link) })),
      affected: z.object({ who: z.string(), condition: z.string().nullable().optional(), count: z.string() }),
      assumptions: z.array(z.object({ id: z.string(), what: z.string(), why: z.string(), alternative: z.string() })),
      aggregate: z.array(z.object({ description: z.string(), text: z.string() })),
      distribution: z.object({ description: z.string() }).loose().nullable().optional(),
      distribution_label: z.string().nullable(),
      contradictions: z.array(z.string()),
      open_questions: z.array(z.string()),
      sources: z.array(
        z.looseObject({ id: z.string(), title: z.string(), url: z.url(), role_label: z.string(), retrieved: z.string(), archive: z.string().nullable() }),
      ),
      changelog: z.array(z.object({ date: z.string(), change: z.string(), reason: z.string() })),
    }),
  }),
});

const bills = defineCollection({
  loader: file("./src/generated/bills.json"),
  schema: z.object({
    id: z.string(),
    slug: z.string(),
    citation: z.string(),
    title: z.string(),
    type: z.enum(["government_bill", "members_bill"]),
    kind: z.string(),
    introduced: z.string(),
    introduced_text: z.string(),
    stage: z.enum(["pre_parliamentary", "introduced", "committee", "passed_first_chamber", "passed_second_chamber", "published"]),
    step: z.number().int().min(0).max(5),
    step_label: z.string(),
    measures: z.array(z.string()),
    parliament_url: z.url(),
    eu: z.object({
      group: z.enum(["eu_law", "eu_scope", "national", "not_stated"]),
      label: z.string().nullable(),
      goes_beyond: z.boolean(),
      goes_beyond_text: z.string().nullable(),
      acts: z.array(z.object({ label: z.string(), url: z.url(), role: z.enum(["transposed", "implemented"]) })),
      checked: z.boolean(),
    }),
  }),
});

const households = defineCollection({
  loader: file("./src/generated/households.json"),
  schema: z.object({ id: z.string(), short: z.string(), label: z.string(), description: z.string() }),
});

export const collections = { cards, bills, households };
