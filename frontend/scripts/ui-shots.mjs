// Renders AegisTrace pages to PNG for visual acceptance review.
// Captures desktop + mobile + paper theme + full-page landing.
// Usage: node scripts/ui-shots.mjs
import { chromium } from "playwright";
import { mkdirSync } from "node:fs";

const BASE = process.env.FRONTEND_URL ?? "http://localhost:3000";
const API = process.env.AEGISTRACE_API_URL ?? "http://127.0.0.1:8420";
const KEY = process.env.AEGISTRACE_KEY ?? "at_demo_bootstrap_key_do_not_use_in_prod";
const OUT = new URL("../docs-ui-shots/", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1");

mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();

async function newPage(viewport) {
  const ctx = await browser.newContext({ viewport });
  const page = await ctx.newPage();
  return { ctx, page };
}

async function shot(page, name, { fullPage = false } = {}) {
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(450);
  await page.screenshot({ path: `${OUT}${name}.png`, fullPage });
  console.log(`saved ${name}.png`);
}

// ---------- desktop ----------
const { ctx: dctx, page: d } = await newPage({ width: 1440, height: 900 });

// landing full page
await d.goto(`${BASE}/`);
await d.waitForLoadState("domcontentloaded");
await d.waitForTimeout(1000);
await shot(d, "01-landing-full", { fullPage: true });
await shot(d, "02-landing-hero");

// login
await d.goto(`${BASE}/login`);
await d.waitForLoadState("domcontentloaded");
await d.waitForTimeout(700);
await shot(d, "03-login");

// login → console
await d.fill("#apiKey", KEY);
await d.click("button[type=submit]");
await d.waitForURL("**/app", { timeout: 15000 });
await d.waitForTimeout(1100);
await shot(d, "04-overview");

await d.goto(`${BASE}/app/executions`);
await d.waitForLoadState("domcontentloaded");
await d.waitForTimeout(800);
await shot(d, "05-executions");

const execs = await (await fetch(`${API}/api/v1/executions`, { headers: { "X-API-Key": KEY } })).json();
const pick = execs.find((e) => e.trust_state === "UNTRUSTED") ?? execs[0] ?? null;
if (pick) {
  await d.goto(`${BASE}/app/executions/${pick.id}`);
  await d.waitForLoadState("domcontentloaded");
  await d.waitForTimeout(1100);
  await shot(d, "06-execution-detail");
}

for (const [path, name] of [
  ["/app/components", "07-components"],
  ["/app/incidents", "08-incidents"],
  ["/app/certificates", "09-certificates"],
  ["/app/attackbench", "10-attackbench"],
  ["/app/settings", "11-settings"],
]) {
  await d.goto(`${BASE}${path}`);
  await d.waitForLoadState("domcontentloaded");
  await d.waitForTimeout(700);
  await shot(d, name);
}

// paper theme (console)
await d.evaluate(() => {
  document.documentElement.dataset.theme = "paper";
  localStorage.setItem("aegistrace-theme", "paper");
});
await d.goto(`${BASE}/app`);
await d.waitForLoadState("domcontentloaded");
await d.waitForTimeout(900);
await shot(d, "12-overview-paper");

// 404
await d.goto(`${BASE}/definitely-not-a-page`);
await d.waitForLoadState("domcontentloaded");
await d.waitForTimeout(500);
await shot(d, "13-not-found");
await dctx.close();

// ---------- mobile ----------
const { ctx: mctx, page: m } = await newPage({ width: 390, height: 844 });
await m.goto(`${BASE}/`);
await m.waitForLoadState("domcontentloaded");
await m.waitForTimeout(900);
await shot(m, "14-mobile-landing", { fullPage: true });

await m.goto(`${BASE}/login`);
await m.waitForLoadState("domcontentloaded");
await m.waitForTimeout(600);
await shot(m, "15-mobile-login");

await m.fill("#apiKey", KEY);
await m.click("button[type=submit]");
await m.waitForURL("**/app", { timeout: 15000 });
await m.waitForTimeout(1000);
await shot(m, "16-mobile-overview");

// open mobile nav
await m.click("button[aria-label='Open navigation']");
await m.waitForTimeout(400);
await shot(m, "17-mobile-nav");

// horizontal overflow check
const overflow = await m.evaluate(
  () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
);
console.log(`mobile horizontal overflow: ${overflow}px`);
await mctx.close();

await browser.close();
console.log("DONE");
