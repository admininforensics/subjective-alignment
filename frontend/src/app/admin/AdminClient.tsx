"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiFetch } from "@/lib/api";
import { getUser } from "@/lib/auth";
import type { AuthUser } from "@/lib/types";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useMemo, useSyncExternalStore } from "react";

export default function AdminClient() {
  const router = useRouter();
  const hydrated = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false
  );

  const user = useMemo(() => (hydrated ? (getUser() as AuthUser | null) : null), [hydrated]);

  const respondents = useQuery({
    queryKey: ["org-respondents"],
    queryFn: () => apiFetch<Array<{ id: number; email: string; role: string }>>("/organisation/respondents/"),
    enabled: Boolean(user) && hydrated,
  });

  if (!hydrated) return null;

  return (
    <div className="mx-auto w-full max-w-5xl px-6 py-10">
      <div className="flex items-start justify-between gap-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Admin</h1>
          <p className="text-sm text-muted-foreground">Organisation management</p>
        </div>
        <Button variant="secondary" onClick={() => router.push("/dashboard")}>
          Back to dashboard
        </Button>
      </div>

      <div className="mt-8 grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Respondents</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2">
            {respondents.isLoading ? (
              <p className="text-sm text-muted-foreground">Loading…</p>
            ) : respondents.error ? (
              <p className="text-sm text-destructive">{respondents.error.message}</p>
            ) : (
              respondents.data?.slice(0, 50).map((r) => (
                <div key={r.id} className="text-sm">
                  <span className="font-medium">{r.email}</span>{" "}
                  <span className="text-muted-foreground">{r.role}</span>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

