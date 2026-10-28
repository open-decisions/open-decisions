import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const pages = ["/", "/gesetze/", "/gesetze/AT-XXVIII-I-69/", "/gesetze/AT-XXVIII-I-657/", "/massnahmen/at-2025-klimabonus/", "/massnahmen/at-2025-klimabonus/zahl-zuerst/", "/methodik/", "/korrekturen/", "/ueber/", "/impressum/"];

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

test("tracker opens on what is happening now and filters all bills", async ({ page }) => {
  await page.goto("/gesetze/");
  await expect(page.getByRole("heading", { name: /Demnächst auf der Tagesordnung/ })).toBeVisible();
  await page.getByRole("button", { name: /^Alle \d+ Vorhaben/ }).click();
  const rows = page.locator("ul.all > li");
  await expect(rows).toHaveCount(311);
  await page.getByRole("button", { name: /^Familie und Gleichstellung/ }).click();
  expect(await rows.count()).toBeLessThan(40);
  await page.getByRole("button", { name: /^Alle$/ }).first().click();
  await page.getByLabel("Suche").fill("Budgetbegleitgesetz 2025");
  await expect(rows).toHaveCount(1);
  await expect(rows.first().getByRole("link", { name: /Was heißt das für dich: Der Klimabonus/ })).toBeVisible();
});

test("tracker filters by relation to EU law", async ({ page }) => {
  await page.goto("/gesetze/");
  await page.getByRole("button", { name: /^Alle \d+ Vorhaben/ }).click();
  await page.getByText("Weitere Filter").click();
  await page.getByRole("button", { name: /^Setzt EU-Vorgaben um/ }).click();
  expect(await page.locator("ul.all > li").count()).toBeGreaterThan(40);
});

test("bill page shows headline, plain status, EU relation and links to the card", async ({ page }) => {
  await page.goto("/gesetze/AT-XXVIII-I-69/");
  await expect(page.locator("h1")).not.toHaveText("Budgetbegleitgesetz 2025");
  await expect(page.getByText(/Offizieller Titel: Budgetbegleitgesetz 2025/)).toBeVisible();
  await expect(page.getByRole("heading", { name: "Kommt das aus der EU" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Der Klimabonus wird nicht mehr ausgezahlt" })).toBeVisible();
});

test("battery law links its EU regulation", async ({ page }) => {
  await page.goto("/gesetze/AT-XXVIII-I-657/");
  await expect(page.getByRole("link", { name: "Verordnung 2023/1542" })).toHaveAttribute("href", /CELEX:32023R1542/);
});
