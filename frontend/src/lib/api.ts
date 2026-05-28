import { clearAuth, getAccessToken, getRefreshToken, setAccessToken } from "@/lib/auth";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://localhost:8000/api";

const AUTH_PATHS = ["/auth/login/", "/auth/signup/", "/auth/refresh/"] as const;

function isAuthPath(path: string): boolean {
  return AUTH_PATHS.some((p) => path === p || path.startsWith(p));
}

async function fetchApi(path: string, init: RequestInit): Promise<Response> {
  try {
    return await fetch(`${API_URL}${path}`, { ...init, cache: "no-store" });
  } catch (err) {
    const msg = err instanceof Error ? err.message : "Network request failed";
    throw new Error(
      msg === "Load failed" || msg === "Failed to fetch"
        ? `Could not reach API at ${API_URL}. Check NEXT_PUBLIC_API_URL and CORS settings.`
        : msg
    );
  }
}

async function refreshAccessToken(): Promise<string | null> {
  const refresh = getRefreshToken();
  if (!refresh) return null;

  try {
    const res = await fetchApi("/auth/refresh/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });
    if (!res.ok) return null;
    const data = (await res.json()) as { access?: string };
    if (!data.access) return null;
    setAccessToken(data.access);
    return data.access;
  } catch {
    return null;
  }
}

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
  _retry = true
): Promise<T> {
  const authRequest = isAuthPath(path);
  const token = authRequest ? null : getAccessToken();
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetchApi(path, { ...init, headers });

  // Do not run refresh/retry logic on login/signup/refresh — avoids breaking sign-in.
  if (res.status === 401 && _retry && !authRequest) {
    const newAccess = await refreshAccessToken();
    if (newAccess) {
      const retryHeaders = new Headers(init.headers);
      retryHeaders.set("Content-Type", "application/json");
      retryHeaders.set("Authorization", `Bearer ${newAccess}`);
      const retryRes = await fetchApi(path, { ...init, headers: retryHeaders });
      if (retryRes.ok) {
        const retryText = await retryRes.text();
        return (retryText ? JSON.parse(retryText) : null) as T;
      }
    }
    clearAuth();
  }

  const text = await res.text();
  let data: unknown = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text || null;
  }
  if (!res.ok) {
    const message = (() => {
      if (typeof data === "string" && data.trim()) return data;
      if (typeof data !== "object" || data === null) return "Request failed";

      const obj = data as Record<string, unknown>;
      if (typeof obj.detail === "string" && obj.detail) return obj.detail;

      // DRF validation errors: {field: ["msg"]} or {non_field_errors: ["msg"]}
      for (const v of Object.values(obj)) {
        if (Array.isArray(v) && typeof v[0] === "string" && v[0]) return v[0];
        if (typeof v === "string" && v) return v;
      }

      return "Request failed";
    })();
    throw new Error(message);
  }
  return data as T;
}

