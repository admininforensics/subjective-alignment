import type { AuthUser, LoginResponse } from "@/lib/types";

const ACCESS_KEY = "sa_access";
const REFRESH_KEY = "sa_refresh";
const USER_KEY = "sa_user";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(REFRESH_KEY);
}

export function getUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
}

export function setAuth(login: LoginResponse) {
  window.localStorage.setItem(ACCESS_KEY, login.access);
  window.localStorage.setItem(REFRESH_KEY, login.refresh);
  window.localStorage.setItem(USER_KEY, JSON.stringify(login.user));
}

export function setAccessToken(access: string) {
  window.localStorage.setItem(ACCESS_KEY, access);
}

export function clearAuth() {
  window.localStorage.removeItem(ACCESS_KEY);
  window.localStorage.removeItem(REFRESH_KEY);
  window.localStorage.removeItem(USER_KEY);
}

