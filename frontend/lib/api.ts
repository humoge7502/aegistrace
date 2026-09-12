import { cookies } from "next/headers";

export const BACKEND_URL =
  process.env.AEGISTRACE_API_URL ?? "http://127.0.0.1:8420";

export const KEY_COOKIE = "at_key";

export async function apiKeyOrNull(): Promise<string | null> {
  const store = await cookies();
  const key = store.get(KEY_COOKIE)?.value;
  return key && key.length > 8 ? key : null;
}

export type ApiError = { status: number; message: string };

export async function apiFetch<T>(
  path: string,
  init?: RequestInit & { key?: string },
): Promise<T> {
  const key = init?.key ?? (await apiKeyOrNull());
  if (!key) {
    throw { status: 401, message: "not signed in" } as ApiError;
  }
  const res = await fetch(`${BACKEND_URL}${path}`, {
    ...init,
    headers: {
      "X-API-Key": key,
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    let message = res.statusText;
    try {
      const body = await res.json();
      message = typeof body.detail === "string" ? body.detail : JSON.stringify(body);
    } catch {
      /* keep statusText */
    }
    throw { status: res.status, message } as ApiError;
  }
  return res.json() as Promise<T>;
}
