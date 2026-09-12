import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { BACKEND_URL, KEY_COOKIE } from "@/lib/api";

export async function POST(req: Request) {
  const body = await req.json().catch(() => null);
  const key = typeof body?.apiKey === "string" ? body.apiKey.trim() : "";
  if (!key.startsWith("at_")) {
    return NextResponse.json({ ok: false, error: "API keys start with at_" }, { status: 400 });
  }
  const res = await fetch(`${BACKEND_URL}/api/v1/auth/verify`, {
    method: "POST",
    headers: { "X-API-Key": key },
    cache: "no-store",
  });
  if (!res.ok) {
    return NextResponse.json(
      { ok: false, error: `backend rejected the key (HTTP ${res.status})` },
      { status: 401 },
    );
  }
  const info = await res.json();
  const store = await cookies();
  store.set(KEY_COOKIE, key, {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 8,
    secure: process.env.NODE_ENV === "production",
  });
  return NextResponse.json({ ok: true, role: info.role, tenant: info.tenant_id });
}

export async function DELETE() {
  const store = await cookies();
  store.delete(KEY_COOKIE);
  return NextResponse.json({ ok: true });
}
