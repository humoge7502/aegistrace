import { NextResponse } from "next/server";
import { cookies } from "next/headers";

import { KEY_COOKIE } from "@/lib/api";

export async function POST(req: Request) {
  const store = await cookies();
  store.delete(KEY_COOKIE);
  return NextResponse.redirect(new URL("/login", req.url), { status: 303 });
}
