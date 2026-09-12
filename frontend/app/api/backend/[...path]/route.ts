import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { BACKEND_URL, KEY_COOKIE } from "@/lib/api";

const ALLOWED_PREFIXES = ["components/", "certificates/", "incidents/", "policies", "auth/keys", "baselines", "executions/"];

async function proxy(req: Request, path: string[]) {
  const store = await cookies();
  const key = store.get(KEY_COOKIE)?.value;
  if (!key) return NextResponse.json({ error: "not signed in" }, { status: 401 });

  const joined = path.join("/");
  if (!ALLOWED_PREFIXES.some((p) => joined.startsWith(p))) {
    return NextResponse.json({ error: "path not allowed" }, { status: 403 });
  }

  const backendRes = await fetch(`${BACKEND_URL}/api/v1/${joined}`, {
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
  return proxy(req, (await ctx.params).path);
}
export async function POST(req: Request, ctx: Ctx) {
  return proxy(req, (await ctx.params).path);
}
export async function PUT(req: Request, ctx: Ctx) {
  return proxy(req, (await ctx.params).path);
}
export async function PATCH(req: Request, ctx: Ctx) {
  return proxy(req, (await ctx.params).path);
}
