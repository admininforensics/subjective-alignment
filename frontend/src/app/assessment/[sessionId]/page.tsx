"use client";

import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import type { SessionDetailResponse } from "@/lib/types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { useMemo, useState, useSyncExternalStore } from "react";

const QUESTIONS_PER_PAGE = 5;

export default function AssessmentPage() {
  const router = useRouter();
  const params = useParams<{ sessionId: string }>();
  const sessionId = Number(params.sessionId);
  const qc = useQueryClient();
  const [page, setPage] = useState<number>(0);

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
  const pageCount = Math.max(1, Math.ceil(questionCount / QUESTIONS_PER_PAGE));
  const currentPage =
    session.isSuccess && questionCount > 0 ? Math.min(Math.max(page, 0), pageCount - 1) : 0;
  const pageStart = currentPage * QUESTIONS_PER_PAGE;
  const pageQuestions = questions.slice(pageStart, pageStart + QUESTIONS_PER_PAGE);
  const pageEnd = pageStart + pageQuestions.length;

  const pageAllAnswered = pageQuestions.every((question) => responsesByQuestion.has(question.id));
  const allAnswered =
    questionCount > 0 && questions.every((question) => responsesByQuestion.has(question.id));

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

  const saveAnswer = (question_id: number, raw_likert_score: number) => {
    if (save.isPending || session.data?.session.status === "COMPLETED") return;
    save.mutate({ question_id, raw_likert_score });
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
  if (questionCount === 0) {
    return (
      <p className="p-6 text-sm text-destructive">
        This assessment has no questions yet. Ask an admin to run the data seed on the server.
      </p>
    );
  }

  const progress = (session.data.session.progress ?? 0) * 100;
  const isCompleted = session.data.session.status === "COMPLETED";
  const isLastPage = currentPage === pageCount - 1;

  return (
    <AppShell
      title="Assessment"
      description={`Page ${currentPage + 1} of ${pageCount} · Questions ${pageStart + 1}–${pageEnd} of ${questionCount}`}
    >
      <div className="mx-auto max-w-3xl">
      <div className="grid gap-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">
            Questions {pageStart + 1}–{pageEnd} of {questionCount}
          </span>
          <span className="font-medium">{Math.round(progress)}%</span>
        </div>
        <Progress value={progress} />
      </div>

      <div className="mt-6 grid gap-4">
        {pageQuestions.map((question, i) => {
          const selected = responsesByQuestion.get(question.id) ?? null;
          return (
            <Card key={question.id}>
              <CardHeader className="pb-3">
                <p className="text-xs text-muted-foreground">
                  Question {pageStart + i + 1} · {question.area} · {question.subarea}
                </p>
                <CardTitle className="text-base font-medium">{question.text}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-5 gap-2">
                  {[1, 2, 3, 4, 5].map((v) => (
                    <Button
                      key={v}
                      variant={selected === v ? "default" : "secondary"}
                      className="transition-ui"
                      onClick={() => saveAnswer(question.id, v)}
                      disabled={save.isPending || isCompleted}
                    >
                      {v}
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {!pageAllAnswered && !isCompleted && (
        <p className="mt-4 text-sm text-muted-foreground">
          Answer every question on this page to continue.
        </p>
      )}

      <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            onClick={() => setPage((p) => Math.max(p - 1, 0))}
            disabled={currentPage === 0}
          >
            Back
          </Button>
          {!isCompleted ? (
            <Button variant="secondary" onClick={() => router.push("/dashboard")}>
              Save and exit
            </Button>
          ) : null}
        </div>

        <div className="flex items-center gap-2">
          {isLastPage ? (
            <Button
              onClick={() => complete.mutate()}
              disabled={complete.isPending || !allAnswered || isCompleted}
            >
              Complete
            </Button>
          ) : (
            <Button
              onClick={() => setPage((p) => Math.min(p + 1, pageCount - 1))}
              disabled={!pageAllAnswered}
            >
              Next
            </Button>
          )}
        </div>
      </div>

      <p className="mt-3 text-xs text-muted-foreground">
        {save.isPending
          ? "Saving…"
          : "Selections are saved automatically. Use Save and exit to continue later from the dashboard."}
      </p>
      </div>
    </AppShell>
  );
}
