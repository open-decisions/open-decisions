import { getCollection } from "astro:content";
import meta from "../generated/meta.json";
import { showDrafts } from "./edition";

export { meta };

export async function getCards() {
  const all = await getCollection("cards");
  return all.map((c) => c.data).filter((c) => c.approved || showDrafts);
}

export async function getHouseholds() {
  const order = (id: string) => Number(id.replace(/\D/g, ""));
  return (await getCollection("households")).map((h) => h.data).sort((a, b) => order(a.id) - order(b.id));
}

export async function getBills() {
  const rows = (await getCollection("bills")).map((b) => b.data);
  return rows.sort((a, b) => (a.introduced < b.introduced ? 1 : a.introduced > b.introduced ? -1 : 0));
}
