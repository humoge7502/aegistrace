import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { BACKEND_URL, KEY_COOKIE } from "@/lib/api";

// exact first-segment allowlist (no prefix tricks, no dot-segment escapes)
const ALLOWED_ROOTS = new Set([
  "components", "certificates", "incidents", "policies",
  "auth", "baselines", "executions",
]);

async function proxy(req: Request, segments: string[], search: string) {
  const store = await cookies();
  const key = store.get(KEY_COOKIE)?.value;
  if (!key) return NextResponse.json({ error: "not signed in" }, { status: 401 });

  if (
    segments.length === 0 ||
    !ALLOWED_ROOTS.has(segments[0]) ||
    segments.some((s) => s === ".." || s === "." || s.includes("%2e%2e") || s.includes(".."))
  ) {
    return NextResponse.json({ error: "path not allowed" }, { status: 403 });
  }

  const backendRes = await fetch(`${BACKEND_URL}/api/v1/${segments.map(encodeURIComponent).join("/")}${search}`, {
    method: req.method,
    headers: { "X-API-Key": key, "Content-Type": "application/json" },
    body: req.method === "GET" || req.method === "HEAD" ? undefined : await req.text(),
    cache: "no-store",
  });
  const text = await backendRes.text();
  return new NextResponse(text, {
    status: backendRes.status,
    headers: { "Content-Type": backendRes.headers.get("content-type") ?? "application/json" },
  });
}

type Ctx = { params: Promise<{ path: string[] }> };

export async function GET(req: Request, ctx: Ctx) {
  const url = new URL(req.url);
  return proxy(req, (await ctx.params).path, url.search);
}
export async function POST(req: Request, ctx: Ctx) {
  const url = new URL(req.url);
  return proxy(req, (await ctx.params).path, url.search);
}
export async function PUT(req: Request, ctx: Ctx) {
  const url = new URL(req.url);
  return proxy(req, (await ctx.params).path, url.search);
}
export async function PATCH(req: Request, ctx: Ctx) {
  const url = new URL(req.url);
  return proxy(req, (await ctx.params).path, url.search);
}
