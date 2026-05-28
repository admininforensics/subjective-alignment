"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiFetch } from "@/lib/api";
import type { ResultsResponse } from "@/lib/types";
import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import {
  Legend,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

import { Button } from "@/components/ui/button";

export default function ResultsPage() {
  const router = useRouter();
  const params = useParams<{ sessionId: string }>();
  const sessionId = Number(params.sessionId);

  const results = useQuery({
    queryKey: ["results", sessionId],
    queryFn: () => apiFetch<ResultsResponse>(`/results/${sessionId}/`),
  });

  if (results.isLoading) return <p className="p-6 text-sm text-muted-foreground">Loading…</p>;
  if (results.error) return <p className="p-6 text-sm text-destructive">{results.error.message}</p>;
  if (!results.data) return <p className="p-6 text-sm text-muted-foreground">No results data.</p>;

  const data = results.data.domain_results.map((d) => ({
    domain: d.domain,
    score: d.score,
    threshold: d.threshold,
  }));

  return (
    <div className="mx-auto w-full max-w-5xl px-6 py-10">
      <div className="flex items-start justify-between gap-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Results</h1>
          <p className="text-sm text-muted-foreground">
            Completed: {results.data.session.completed_at ?? "—"}
          </p>
        </div>
        <Button variant="secondary" onClick={() => router.push("/dashboard")}>
          Back to dashboard
        </Button>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Domain scores</CardTitle>
          </CardHeader>
          <CardContent className="h-[420px] rounded-lg bg-muted/30 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={data} outerRadius="80%" margin={{ left: 16, right: 16, top: 16, bottom: 16 }}>
                <PolarGrid />
                <PolarAngleAxis dataKey="domain" tick={{ fontSize: 12 }} />
                <PolarRadiusAxis angle={30} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Radar
                  dataKey="score"
                  name="Score"
                  stroke="var(--chart-1)"
                  fill="var(--chart-1)"
                  fillOpacity={0.5}
                  strokeWidth={2}
                />
                <Radar
                  dataKey="threshold"
                  name="Threshold"
                  stroke="var(--chart-2)"
                  strokeDasharray="6 4"
                  fill="var(--chart-2)"
                  fillOpacity={0.22}
                  strokeWidth={1.5}
                />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Triggered domains</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2">
            {results.data.domain_results.filter((d) => d.triggered).length ? (
              results.data.domain_results
                .filter((d) => d.triggered)
                .map((d) => (
                  <div key={d.domain} className="text-sm">
                    <span className="font-medium">{d.domain}</span>{" "}
                    <span className="text-muted-foreground">
                      ({Math.round(d.score)} / {Math.round(d.threshold)})
                    </span>
                  </div>
                ))
            ) : (
              <p className="text-sm text-muted-foreground">No triggered domains.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Flags & insights</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            {results.data.flags.length ? (
              results.data.flags.map((f) => (
                <div key={f.flag} className="rounded-lg border p-3">
                  <div className="text-sm font-medium">{f.flag}</div>
                  <div className="mt-1 text-sm text-muted-foreground">{f.insight}</div>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">No flags triggered.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

