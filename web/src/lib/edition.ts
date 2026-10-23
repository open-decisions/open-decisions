import at from "../../editions/at.json";

const editions = { at };
type EditionId = keyof typeof editions;

const id = (import.meta.env.EDITION ?? "at") as EditionId;
if (!(id in editions)) throw new Error(`Unknown edition: ${id}`);

export const edition = editions[id];
export type Edition = typeof at;

export const showDrafts = import.meta.env.SHOW_DRAFTS === "true" || import.meta.env.DEV;

export function url(path = ""): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, "");
  const clean = path.replace(/^\//, "");
  return `${base}/${clean}`;
}
