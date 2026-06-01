"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { skipLicenceCheck } from "@/lib/features";
import type { DashboardResponse } from "@/lib/types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState, useSyncExternalStore } from "react";

export default function DashboardClient() {
  const router = useRouter();
  const qc = useQueryClient();
  const [licenceCode, setLicenceCode] = useState("");
  const hydrated = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false
  );

  const token = useMemo(() => (hydrated ? getAccessToken() : null), [hydrated]);
  useEffect(() => {
    if (!hydrated) return;
    if (!token) router.replace("/login");
  }, [hydrated, router, token]);

  const dashboard = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => apiFetch<DashboardResponse>("/dashboard/"),
    enabled: Boolean(token),
  });

  useEffect(() => {
    // apiFetch now attempts refresh-on-401. If we're still failing, auth was cleared.
    if (!token) router.replace("/login");
  }, [router, token]);

  const start = useMutation({
    mutationFn: async () => apiFetch<{ session_id: number }>("/sessions/start/", { method: "POST" }),
    onSuccess: (data) => {
      if (!data?.session_id) {
        throw new Error("Start session did not return a session id");
      }
      router.push(`/assessment/${data.session_id}`);
    },
  });

  const goToAssessment = () => {
    const existing = dashboard.data?.session?.id;
    if (existing) {
      router.push(`/assessment/${existing}`);
      return;
    }
    start.mutate();
  };

  const activate = useMutation({
    mutationFn: async () =>
      apiFetch<{ activated: boolean; licence: { id: number; status: string } }>("/licences/activate/", {
        method: "POST",
        body: JSON.stringify({ code: licenceCode }),
      }),
    onSuccess: async () => {
      setLicenceCode("");
      await qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  const restart = useMutation({
    mutationFn: async () =>
      apiFetch<{ session_id: number }>("/sessions/restart/", { method: "POST" }),
    onSuccess: async (data) => {
      await qc.invalidateQueries({ queryKey: ["dashboard"] });
      router.push(`/assessment/${data.session_id}`);
    },
  });

  const deleteCompleted = useMutation({
    mutationFn: async () =>
      apiFetch<{ deleted: boolean }>("/sessions/completed/", { method: "DELETE" }),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  if (!hydrated) return null;
  if (!token) return null;

  const hasLicence = skipLicenceCheck || Boolean(dashboard.data?.assigned_licence);
  const canGenerateReport = Boolean(dashboard.data?.latest_result?.session_id);
  const sessionStatus = dashboard.data?.session?.status;
  const hasInProgressSession =
    Boolean(dashboard.data?.session) &&
    sessionStatus !== "COMPLETED" &&
    sessionStatus !== "LOCKED";

  return (
    <>
      {dashboard.isLoading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : dashboard.error ? (
        <p className="text-sm text-destructive">{dashboard.error.message}</p>
      ) : null}

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Assessment</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4">
            {!skipLicenceCheck && !dashboard.data?.assigned_licence ? (
              <div className="grid gap-2">
                <p className="text-sm text-muted-foreground">You don’t have an active licence yet.</p>
                <div className="grid gap-2">
                  <Label htmlFor="licenceCode">Licence code</Label>
                  <Input
                    id="licenceCode"
                    value={licenceCode}
                    onChange={(e) => setLicenceCode(e.target.value)}
                    placeholder="Enter your licence code"
                    autoComplete="off"
                  />
                </div>
                <Button onClick={() => activate.mutate()} disabled={activate.isPending || !licenceCode.trim()}>
                  {activate.isPending ? "Activating…" : "Activate licence"}
                </Button>
                {activate.error ? <p className="text-sm text-destructive">{activate.error.message}</p> : null}
              </div>
            ) : null}

            <div className="grid gap-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Progress</span>
                <span className="font-medium">
                  {dashboard.data?.session?.progress != null
                    ? `${Math.round(dashboard.data.session.progress * 100)}%`
                    : "—"}
                </span>
              </div>
              <Progress
                value={
                  dashboard.data?.session?.progress != null ? dashboard.data.session.progress * 100 : 0
                }
              />
            </div>

            <div className="grid gap-2">
              <Button onClick={goToAssessment} disabled={start.isPending || !hasLicence}>
                {start.isPending ? "Starting…" : dashboard.data?.session ? "Continue" : "Start"}
              </Button>
              {hasInProgressSession ? (
                <Button
                  variant="secondary"
                  disabled={restart.isPending || start.isPending}
                  onClick={() => {
                    if (
                      !window.confirm(
                        "Restart will clear your current answers and start the assessment from the beginning. Continue?"
                      )
                    ) {
                      return;
                    }
                    restart.mutate();
                  }}
                >
                  {restart.isPending ? "Restarting…" : "Restart assessment"}
                </Button>
              ) : null}
              {canGenerateReport ? (
                <Button
                  variant="secondary"
                  disabled={deleteCompleted.isPending}
                  onClick={() => {
                    if (
                      !window.confirm(
                        "Delete your previous completed assessment and results? This cannot be undone."
                      )
                    ) {
                      return;
                    }
                    deleteCompleted.mutate();
                  }}
                >
                  {deleteCompleted.isPending ? "Deleting…" : "Delete previous assessment"}
                </Button>
              ) : null}
              {!skipLicenceCheck && !dashboard.data?.assigned_licence ? (
                <p className="text-sm text-muted-foreground">Activate a licence to start the assessment.</p>
              ) : null}
              {start.error ? <p className="text-sm text-destructive">{start.error.message}</p> : null}
              {restart.error ? <p className="text-sm text-destructive">{restart.error.message}</p> : null}
              {deleteCompleted.error ? (
                <p className="text-sm text-destructive">{deleteCompleted.error.message}</p>
              ) : null}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Latest result</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4">
            {dashboard.data?.latest_result ? (
              <Button onClick={() => router.push(`/results/${dashboard.data.latest_result?.session_id}`)}>
                Generate report
              </Button>
            ) : (
              <Button disabled>Generate report</Button>
            )}
            {!canGenerateReport ? (
              <p className="text-sm text-muted-foreground">Complete the assessment to generate your report.</p>
            ) : null}
            <p className="text-xs text-muted-foreground">Your responses are autosaved as you progress.</p>
          </CardContent>
        </Card>
      </div>
    </>
  );
}

