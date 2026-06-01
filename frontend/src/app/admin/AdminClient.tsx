"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect, useSyncExternalStore } from "react";

export default function AdminClient() {
  const router = useRouter();
  const hydrated = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false
  );
  const token = hydrated ? getAccessToken() : null;

  useEffect(() => {
    if (!hydrated) return;
    if (!token) router.replace("/login");
  }, [hydrated, router, token]);

  const respondents = useQuery({
    queryKey: ["org-respondents"],
    queryFn: () => apiFetch<Array<{ id: number; email: string; role: string }>>("/organisation/respondents/"),
    enabled: Boolean(token) && hydrated,
  });

  if (!hydrated || !token) return null;

  return (
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
            <div key={r.id} className="rounded-md border border-border px-3 py-2 text-sm transition-ui hover:bg-muted/50">
              <span className="font-medium">{r.email}</span>{" "}
              <span className="text-muted-foreground">{r.role}</span>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
