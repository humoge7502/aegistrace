// Renders every AegisTrace console page to PNG for visual acceptance review.
// Usage: node scripts/ui-shots.mjs  (backend on :8420, frontend on :3000)
import { chromium } from "playwright";
import { mkdirSync } from "node:fs";

const BASE = process.env.FRONTEND_URL ?? "http://localhost:3000";
const API = process.env.AEGISTRACE_API_URL ?? "http://127.0.0.1:8420";
const KEY = process.env.AEGISTRACE_KEY ?? "at_demo_bootstrap_key_do_not_use_in_prod";
const OUT = new URL("../docs-ui-shots/", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1");

mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

async function shot(name) {
  await page.waitForTimeout(400);
  await page.screenshot({ path: `${OUT}${name}.png`, fullPage: false });
  console.log(`saved ${name}.png`);
}

// 1. landing
await page.goto(`${BASE}/`);
await page.waitForLoadState("domcontentloaded");
await page.waitForTimeout(1200);
await shot("01-landing");

// 2. login
await page.goto(`${BASE}/login`);
await page.waitForLoadState("domcontentloaded");
await page.fill("#apiKey", KEY);
await page.click("button[type=submit]");
await page.waitForURL("**/app", { timeout: 15000 });
await page.waitForTimeout(1200);
await shot("02-overview");

// 3. executions list
await page.goto(`${BASE}/app/executions`);
await page.waitForLoadState("domcontentloaded");
await page.waitForTimeout(900);
await shot("03-executions");

// 4. first execution detail (trusted one if present)
const execs = await (await fetch(`${API}/api/v1/executions`, { headers: { "X-API-Key": KEY } })).json();
const pick =
  execs.find((e) => e.trust_state === "UNTRUSTED") ?? execs[0] ?? null;
if (pick) {
  await page.goto(`${BASE}/app/executions/${pick.id}`);
  await page.waitForLoadState("domcontentloaded");
  await page.waitForTimeout(1200);
  await shot("04-execution-detail-graph");
}

// 5. components
await page.goto(`${BASE}/app/components`);
await page.waitForLoadState("domcontentloaded");
await page.waitForTimeout(900);
await shot("05-components");

// 6. incidents
await page.goto(`${BASE}/app/incidents`);
await page.waitForLoadState("domcontentloaded");
await page.waitForTimeout(900);
await shot("06-incidents");

// 7. certificates
await page.goto(`${BASE}/app/certificates`);
await page.waitForLoadState("domcontentloaded");
await page.waitForTimeout(900);
await shot("07-certificates");

// 8. attackbench
await page.goto(`${BASE}/app/attackbench`);
await page.waitForLoadState("domcontentloaded");
await page.waitForTimeout(900);
await shot("08-attackbench");

// 9. settings
await page.goto(`${BASE}/app/settings`);
await page.waitForLoadState("domcontentloaded");
await page.waitForTimeout(900);
await shot("09-settings");

await browser.close();
console.log("DONE");
