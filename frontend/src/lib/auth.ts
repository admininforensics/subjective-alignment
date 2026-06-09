import type { AuthUser, LoginResponse } from "@/lib/types";
import { useSyncExternalStore } from "react";

const ACCESS_KEY = "sa_access";
const REFRESH_KEY = "sa_refresh";
const USER_KEY = "sa_user";
const AUTH_CHANGE_EVENT = "sa-auth-change";

type AuthSnapshot = {
  accessToken: string | null;
  user: AuthUser | null;
};

const SERVER_AUTH_SNAPSHOT: AuthSnapshot = { accessToken: null, user: null };
let cachedAuthSnapshot: AuthSnapshot = SERVER_AUTH_SNAPSHOT;

function usersEqual(a: AuthUser | null, b: AuthUser | null): boolean {
  if (a === b) return true;
  if (!a || !b) return false;
  return (
    a.id === b.id &&
    a.email === b.email &&
    a.role === b.role &&
    a.organisation_id === b.organisation_id &&
    a.allow_survey_simulation === b.allow_survey_simulation
  );
}

function snapshotsEqual(a: AuthSnapshot, b: AuthSnapshot): boolean {
  return a.accessToken === b.accessToken && usersEqual(a.user, b.user);
}

function notifyAuthChange() {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event(AUTH_CHANGE_EVENT));
}

export function subscribeAuth(onStoreChange: () => void) {
  if (typeof window === "undefined") return () => {};
  window.addEventListener(AUTH_CHANGE_EVENT, onStoreChange);
  return () => window.removeEventListener(AUTH_CHANGE_EVENT, onStoreChange);
}

export function getAuthState(): AuthSnapshot {
  const next: AuthSnapshot = {
    accessToken: getAccessToken(),
    user: getUser(),
  };
  if (snapshotsEqual(cachedAuthSnapshot, next)) {
    return cachedAuthSnapshot;
  }
  cachedAuthSnapshot = next;
  return cachedAuthSnapshot;
}

export function useAuth() {
  return useSyncExternalStore(subscribeAuth, getAuthState, () => SERVER_AUTH_SNAPSHOT);
}

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
  notifyAuthChange();
}

export function setAccessToken(access: string) {
  window.localStorage.setItem(ACCESS_KEY, access);
  notifyAuthChange();
}

export function clearAuth() {
  window.localStorage.removeItem(ACCESS_KEY);
  window.localStorage.removeItem(REFRESH_KEY);
  window.localStorage.removeItem(USER_KEY);
  notifyAuthChange();
}

