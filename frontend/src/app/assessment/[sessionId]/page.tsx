"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import type { SessionDetailResponse } from "@/lib/types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { useMemo, useState, useSyncExternalStore } from "react";

export default function AssessmentPage() {
  const router = useRouter();
  const params = useParams<{ sessionId: string }>();
  const sessionId = Number(params.sessionId);
  const qc = useQueryClient();
  const [cursor, setCursor] = useState<number>(0);

  const hydrated = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false
  );
  const token = useMemo(() => (hydrated ? getAccessToken() : null), [hydrated]);
  const sessionIdValid = Number.isFinite(sessionId) && sessionId > 0;

  const session = useQuery({
    queryKey: ["session", sessionId],
    queryFn: () => apiFetch<SessionDetailResponse>(`/sessions/${sessionId}/`),
    enabled: hydrated && Boolean(token) && sessionIdValid,
  });

  const responsesByQuestion = useMemo(() => {
    const m = new Map<number, number>();
    for (const r of session.data?.responses ?? []) m.set(r.question_id, r.raw_likert_score);
    return m;
  }, [session.data?.responses]);

  const questions = session.data?.questions ?? [];
  const questionCount = questions.length;
  const currentIdx =
    session.isSuccess && questionCount > 0
      ? Math.min(Math.max(cursor, 0), questionCount - 1)
      : 0;
  const q = questions[currentIdx];

  const firstUnansweredIdx = useMemo(() => {
    const idx = questions.findIndex((question) => !responsesByQuestion.has(question.id));
    return idx === -1 ? 0 : idx;
  }, [questions, responsesByQuestion]);

  const save = useMutation({
    mutationFn: async (payload: { question_id: number; raw_likert_score: number }) =>
      apiFetch(`/sessions/${sessionId}/responses/`, {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["session", sessionId] });
    },
  });

  const complete = useMutation({
    mutationFn: async () => apiFetch(`/sessions/${sessionId}/complete/`, { method: "POST" }),
    onSuccess: () => router.replace(`/results/${sessionId}`),
  });

  const answerAndAdvance = (raw_likert_score: number) => {
    if (!q || save.isPending || session.data?.session.status === "COMPLETED") return;

    const isLastQuestion = currentIdx === questionCount - 1;
    const alreadyAnswered = responsesByQuestion.has(q.id);
    const answeredCountAfter = responsesByQuestion.size + (alreadyAnswered ? 0 : 1);
    const willBeAllAnswered = answeredCountAfter === questionCount;

    save.mutate(
      { question_id: q.id, raw_likert_score },
      {
        onSuccess: async () => {
          await qc.invalidateQueries({ queryKey: ["session", sessionId] });
          if (isLastQuestion && willBeAllAnswered) {
            complete.mutate();
            return;
          }
          setCursor((i) => Math.min(i + 1, questionCount - 1));
        },
      }
    );
  };

  if (!hydrated) return <p className="p-6 text-sm text-muted-foreground">Loading…</p>;
  if (!sessionIdValid) {
    return <p className="p-6 text-sm text-destructive">Invalid session link.</p>;
  }
  if (!token) {
    router.replace("/login");
    return null;
  }
  if (session.isLoading) return <p className="p-6 text-sm text-muted-foreground">Loading…</p>;
  if (session.error) return <p className="p-6 text-sm text-destructive">{session.error.message}</p>;
  if (!session.data) return <p className="p-6 text-sm text-muted-foreground">No session data.</p>;
  if (!q) {
    return (
      <p className="p-6 text-sm text-destructive">
        This assessment has no questions yet. Ask an admin to run the data seed on the server.
      </p>
    );
  }

  const selected = responsesByQuestion.get(q.id) ?? null;
  const progress = (session.data.session.progress ?? 0) * 100;

  return (
    <div className="mx-auto w-full max-w-3xl px-6 py-10">
      <div className="flex items-start justify-between gap-6">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Assessment</h1>
          <p className="text-sm text-muted-foreground">
            {q.area} · {q.subarea}
          </p>
        </div>
        <Button variant="secondary" onClick={() => router.push("/dashboard")}>
          Back to dashboard
        </Button>
      </div>

      <div className="mt-6 grid gap-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">
            Question {currentIdx + 1} of {questionCount}
          </span>
          <span className="font-medium">{Math.round(progress)}%</span>
        </div>
        <Progress value={progress} />
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-base font-medium">{q.text}</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="grid grid-cols-5 gap-2">
            {[1, 2, 3, 4, 5].map((v) => (
              <Button
                key={v}
                variant={selected === v ? "default" : "secondary"}
                onClick={() => answerAndAdvance(v)}
                disabled={save.isPending || session.data.session.status === "COMPLETED"}
              >
                {v}
              </Button>
            ))}
          </div>

          <div className="flex items-center justify-between">
            <Button
              variant="secondary"
              onClick={() => setCursor((i) => Math.max(i - 1, 0))}
              disabled={currentIdx === 0}
            >
              Back
            </Button>

            <div className="flex items-center gap-2">
              <Button variant="secondary" onClick={() => setCursor(firstUnansweredIdx)}>
                Jump to first unanswered
              </Button>
              {currentIdx === questionCount - 1 ? (
                <Button
                  onClick={() => complete.mutate()}
                  disabled={complete.isPending || session.data.responses.length !== questionCount}
                >
                  Complete
                </Button>
              ) : (
                <Button onClick={() => setCursor((i) => Math.min(i + 1, questionCount - 1))}>
                  Next
                </Button>
              )}
            </div>
          </div>

          <p className="text-xs text-muted-foreground">
            {save.isPending ? "Saving…" : "Autosave on selection."}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
