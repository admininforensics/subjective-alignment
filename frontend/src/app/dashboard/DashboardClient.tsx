"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { DashboardResponse } from "@/lib/types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function DashboardClient() {
  const router = useRouter();
  const qc = useQueryClient();
  const [licenceCode, setLicenceCode] = useState("");
  const { accessToken } = useAuth();

  useEffect(() => {
    if (!accessToken) {
      qc.removeQueries({ queryKey: ["dashboard"] });
      router.replace("/login");
    }
  }, [accessToken, qc, router]);

  const dashboard = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => apiFetch<DashboardResponse>("/dashboard/"),
    enabled: Boolean(accessToken),
    retry: false,
  });

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

  const purchase = useMutation({
    mutationFn: async () =>
      apiFetch<{ purchased: boolean; licence: { id: number; status: string } }>("/licences/purchase/", {
        method: "POST",
      }),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  const activate = useMutation({
    mutationFn: async () =>
      apiFetch<{ activated: boolean; licence: { id: number; status: string } }>("/licences/activate/", {
        method: "POST",
        body: JSON.stringify({ code: licenceCode.trim() }),
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

  const simulateComplete = useMutation({
    mutationFn: async () =>
      apiFetch<{ session_id: number; questions_answered: number }>("/sessions/simulate-complete/", {
        method: "POST",
        body: JSON.stringify({}),
      }),
    onSuccess: async (data) => {
      await qc.invalidateQueries({ queryKey: ["dashboard"] });
      router.push(`/results/${data.session_id}`);
    },
  });

  if (!accessToken) return null;

  const showSimulateButton = Boolean(dashboard.data?.can_simulate_survey);
  const hasLicence = Boolean(dashboard.data?.assigned_licence);
  const showLicenceOptions = dashboard.isSuccess && !hasLicence;
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
            {showLicenceOptions ? (
              <div className="grid gap-4 rounded-lg border border-border bg-muted/30 p-4">
                <p className="text-sm text-muted-foreground">
                  Purchase a licence or enter a code you received to start the assessment.
                </p>
                <Button
                  onClick={() => purchase.mutate()}
                  disabled={purchase.isPending || activate.isPending}
                >
                  {purchase.isPending ? "Processing…" : "Purchase licence"}
                </Button>
                <div className="relative py-1">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-border" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase tracking-wide">
                    <span className="bg-muted/30 px-2 text-muted-foreground">or enter a code</span>
                  </div>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="licenceCode">Licence code</Label>
                  <Input
                    id="licenceCode"
                    value={licenceCode}
                    onChange={(e) => setLicenceCode(e.target.value)}
                    placeholder="Enter your licence code"
                    autoComplete="off"
                    disabled={activate.isPending || purchase.isPending}
                  />
                </div>
                <Button
                  variant="secondary"
                  onClick={() => activate.mutate()}
                  disabled={activate.isPending || purchase.isPending || !licenceCode.trim()}
                >
                  {activate.isPending ? "Activating…" : "Enter licence code"}
                </Button>
                {purchase.error ? <p className="text-sm text-destructive">{purchase.error.message}</p> : null}
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
              {start.error ? <p className="text-sm text-destructive">{start.error.message}</p> : null}
              {restart.error ? <p className="text-sm text-destructive">{restart.error.message}</p> : null}
              {deleteCompleted.error ? (
                <p className="text-sm text-destructive">{deleteCompleted.error.message}</p>
              ) : null}
              {simulateComplete.error ? (
                <p className="text-sm text-destructive">{simulateComplete.error.message}</p>
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
            {showSimulateButton ? (
              <Button
                variant="outline"
                disabled={simulateComplete.isPending}
                onClick={() => {
                  if (
                    !window.confirm(
                      "Simulate answering all 132 questions with random scores (1–5) and complete the assessment? " +
                        "Report generation may take up to a minute."
                    )
                  ) {
                    return;
                  }
                  simulateComplete.mutate();
                }}
              >
                {simulateComplete.isPending ? "Simulating survey…" : "Simulate survey completion (dev)"}
              </Button>
            ) : null}
            <p className="text-xs text-muted-foreground">Your responses are autosaved as you progress.</p>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
