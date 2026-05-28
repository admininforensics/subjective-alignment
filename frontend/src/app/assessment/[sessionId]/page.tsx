"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { apiFetch } from "@/lib/api";
import type { SessionDetailResponse } from "@/lib/types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { useMemo, useState } from "react";

export default function AssessmentPage() {
  const router = useRouter();
  const params = useParams<{ sessionId: string }>();
  const sessionId = Number(params.sessionId);
  const qc = useQueryClient();
  const [cursor, setCursor] = useState<number>(0);

  const session = useQuery({
    queryKey: ["session", sessionId],
    queryFn: () => apiFetch<SessionDetailResponse>(`/sessions/${sessionId}/`),
  });

  const responsesByQuestion = useMemo(() => {
    const m = new Map<number, number>();
    for (const r of session.data?.responses ?? []) m.set(r.question_id, r.raw_likert_score);
    return m;
  }, [session.data?.responses]);

  const firstUnansweredIdx = useMemo(() => {
    const qs = session.data?.questions ?? [];
    const idx = qs.findIndex((q) => !responsesByQuestion.has(q.id));
    return idx === -1 ? 0 : idx;
  }, [responsesByQuestion, session.data?.questions]);

  const currentIdx = session.isSuccess ? Math.min(Math.max(cursor || 0, 0), session.data.questions.length - 1) : 0;

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

  const answerAndAdvance = (raw_likert_score: number) => {
    if (save.isPending || session.data?.session.status === "COMPLETED") return;

    const isLastQuestion = currentIdx === questions.length - 1;
    const alreadyAnswered = responsesByQuestion.has(q.id);
    const answeredCountAfter = responsesByQuestion.size + (alreadyAnswered ? 0 : 1);
    const willBeAllAnswered = answeredCountAfter === questions.length;

    save.mutate(
      { question_id: q.id, raw_likert_score },
      {
        onSuccess: async () => {
          await qc.invalidateQueries({ queryKey: ["session", sessionId] });
          if (isLastQuestion && willBeAllAnswered) {
            complete.mutate();
            return;
          }
          setCursor((i) => Math.min(i + 1, questions.length - 1));
        },
      }
    );
  };

  const complete = useMutation({
    mutationFn: async () => apiFetch(`/sessions/${sessionId}/complete/`, { method: "POST" }),
    onSuccess: () => router.replace(`/results/${sessionId}`),
  });

  if (session.isLoading) return <p className="p-6 text-sm text-muted-foreground">Loading…</p>;
  if (session.error) return <p className="p-6 text-sm text-destructive">{session.error.message}</p>;
  if (!session.data) return <p className="p-6 text-sm text-muted-foreground">No session data.</p>;

  const questions = session.data.questions;
  const q = questions[currentIdx];
  const selected = responsesByQuestion.get(q.id) ?? null;

  const progress = session.data.session.progress * 100;

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
            Question {currentIdx + 1} of {questions.length}
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
              <Button
                variant="secondary"
                onClick={() => setCursor(firstUnansweredIdx)}
              >
                Jump to first unanswered
              </Button>
              {currentIdx === questions.length - 1 ? (
                <Button
                  onClick={() => complete.mutate()}
                  disabled={complete.isPending || (session.data.responses.length !== questions.length)}
                >
                  Complete
                </Button>
              ) : (
                <Button onClick={() => setCursor((i) => Math.min(i + 1, questions.length - 1))}>
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

