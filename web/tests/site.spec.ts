import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const pages = ["/", "/gesetze/", "/massnahmen/at-2025-klimabonus/", "/massnahmen/at-2025-klimabonus/zahl-zuerst/", "/methodik/", "/korrekturen/", "/ueber/", "/impressum/"];

for (const path of pages) {
  test(`no accessibility violations on ${path}`, async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto(path);
    const result = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
    expect(result.violations.map((v) => `${v.id}: ${v.nodes.length}`)).toEqual([]);
    expect(errors).toEqual([]);
  });
}

test("household picker on the start page changes the values", async ({ page }) => {
  await page.goto("/");
  const klimabonus = page.getByRole("link", { name: /Der Klimabonus wird nicht mehr ausgezahlt/ });
  await expect(klimabonus).toContainText("minus 220 €");
  await page.getByRole("button", { name: "Paar, 2 Kinder" }).click();
  await expect(klimabonus).toContainText("minus 590 bis 740 €");
});

test("card shows the seven elements in order and every number has a label", async ({ page }) => {
  await page.goto("/massnahmen/at-2025-klimabonus/");
  const headings = await page.locator("main h2.eyebrow").allTextContents();
  expect(headings).toEqual(["Was wurde gesagt", "Was steht im Gesetz", "Was heißt das für dich", "Was ist unklar", "Nachschauen"]);
  await page.getByRole("button", { name: "Pensionistin, Ausgleichszulage" }).first().click();
  await expect(page.locator(".result")).toContainText("minus 250 bis 290 €");
  await expect(page.locator(".result")).toContainText("geschätzt");
});

test("tracker filters by stage and search", async ({ page }) => {
  await page.goto("/gesetze/");
  const rows = page.locator("tbody tr");
  await expect(rows).toHaveCount(311);
  await page.getByRole("button", { name: /^Eingebracht/ }).click();
  await expect(rows).toHaveCount(3);
  await page.getByRole("button", { name: /^Alle \d/ }).click();
  await page.getByLabel("Suche in Titel und Nummer").fill("Budgetbegleitgesetz 2025");
  await expect(rows).toHaveCount(1);
  await expect(rows.first()).toContainText("4 Karten".replace("4 Karten", "Der Klimabonus wird nicht mehr ausgezahlt"));
});
