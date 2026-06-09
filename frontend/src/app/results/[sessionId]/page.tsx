"use client";

import { AppShell } from "@/components/layout/AppShell";
import { SubalWheel } from "@/components/report/SubalWheel";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import type { ResultsResponse } from "@/lib/types";
import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { Download } from "lucide-react";
import { useMemo, useSyncExternalStore } from "react";

/** Strain levels: higher strain is worse. */
function strainBadgeClass(level: string) {
  if (level === "High") return "bg-red-100 text-red-800";
  if (level === "Moderate") return "bg-amber-100 text-amber-900";
  return "bg-emerald-100 text-emerald-800";
}

/** Alignment levels: higher alignment is better. */
function alignmentBadgeClass(level: string) {
  if (level === "High") return "bg-emerald-100 text-emerald-800";
  if (level === "Moderate") return "bg-amber-100 text-amber-900";
  return "bg-red-100 text-red-800";
}

export default function ResultsPage() {
  const router = useRouter();
  const params = useParams<{ sessionId: string }>();
  const sessionId = Number(params.sessionId);
  const sessionIdValid = Number.isFinite(sessionId) && sessionId > 0;

  const hydrated = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false
  );
  const token = useMemo(() => (hydrated ? getAccessToken() : null), [hydrated]);

  const results = useQuery({
    queryKey: ["results", sessionId],
    queryFn: () => apiFetch<ResultsResponse>(`/results/${sessionId}/`),
    enabled: hydrated && Boolean(token) && sessionIdValid,
  });

  if (!hydrated) return <p className="p-6 text-sm text-muted-foreground">Loading…</p>;
  if (!sessionIdValid) {
    return <p className="p-6 text-sm text-destructive">Invalid session link.</p>;
  }
  if (!token) {
    router.replace("/login");
    return null;
  }
  if (results.isLoading) return <p className="p-6 text-sm text-muted-foreground">Loading…</p>;
  if (results.error) return <p className="p-6 text-sm text-destructive">{results.error.message}</p>;
  if (!results.data) return <p className="p-6 text-sm text-muted-foreground">No results data.</p>;

  const report = results.data.report;

  const downloadReport = () => {
    const previousTitle = document.title;
    const completed = results.data.session.completed_at
      ? new Date(results.data.session.completed_at).toISOString().slice(0, 10)
      : String(sessionId);
    document.title = `Subjective-Alignment-Report-${completed}`;
    window.print();
    document.title = previousTitle;
  };

  return (
    <AppShell
      title="Subjective Alignment Report"
      description={`Completed ${results.data.session.completed_at ? new Date(results.data.session.completed_at).toLocaleString() : "—"}`}
    >
      {!report ? (
        <p className="text-sm text-muted-foreground">Report is not available for this session yet.</p>
      ) : (
        <div className="grid gap-6">
          <div className="no-print flex flex-wrap items-center justify-end gap-3">
            <Button type="button" variant="outline" onClick={downloadReport}>
              <Download className="size-4" aria-hidden />
              Download report
            </Button>
            <p className="w-full text-right text-xs text-muted-foreground sm:w-auto">
              Opens print — choose &quot;Save as PDF&quot; to download.
            </p>
          </div>

          <Card className="report-card">
            <CardHeader>
              <CardTitle>1. Welcome</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed text-muted-foreground">{report.welcome}</p>
            </CardContent>
          </Card>

          <Card className="report-card">
            <CardHeader>
              <CardTitle>2. Your Overall Alignment Snapshot</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4">
              <div className="flex flex-wrap items-center gap-3">
                <span className="text-sm text-muted-foreground">Overall alignment level</span>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-medium ${alignmentBadgeClass(report.overall_snapshot.alignment_level)}`}
                >
                  {report.overall_snapshot.alignment_level}
                </span>
                <span className="text-xs text-muted-foreground">
                  System state: {report.overall_snapshot.system_state}
                </span>
              </div>
              <p className="text-sm leading-relaxed">{report.overall_snapshot.main_pattern}</p>
              {report.wheel ? <SubalWheel wheel={report.wheel} /> : null}
            </CardContent>
          </Card>

          <Card className="report-card">
            <CardHeader>
              <CardTitle>3. Your Top 3 Areas of Strain</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4">
              {report.top_strain_areas.map((area) => (
                <div key={area.domain} className="rounded-lg border p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-medium">
                      {area.rank}. {area.domain}
                    </span>
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${strainBadgeClass(area.level)}`}
                    >
                      {area.level}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground">
                    <span className="font-medium text-foreground">What this means: </span>
                    {area.what_this_means}
                  </p>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card className="report-card">
            <CardHeader>
              <CardTitle>4. Full Results Summary</CardTitle>
            </CardHeader>
            <CardContent className="overflow-x-auto">
              <table className="w-full min-w-[520px] text-left text-sm">
                <thead>
                  <tr className="border-b text-muted-foreground">
                    <th className="py-2 pr-4 font-medium">Area</th>
                    <th className="py-2 pr-4 font-medium">Level</th>
                    <th className="py-2 font-medium">What it reflects</th>
                  </tr>
                </thead>
                <tbody>
                  {report.full_results_summary.map((row) => (
                    <tr key={row.domain} className="border-b border-border/60">
                      <td className="py-3 pr-4 font-medium">{row.domain}</td>
                      <td className="py-3 pr-4">
                        <span
                          className={`rounded-full px-2 py-0.5 text-xs font-medium ${strainBadgeClass(row.level)}`}
                        >
                          {row.level}
                        </span>
                      </td>
                      <td className="py-3 text-muted-foreground">{row.what_it_reflects}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>

          <Card className="report-card">
            <CardHeader>
              <CardTitle>5. What Your Results Suggest</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4">
              {report.what_results_suggest.split("\n\n").map((paragraph) => (
                <p key={paragraph.slice(0, 24)} className="text-sm leading-relaxed text-muted-foreground">
                  {paragraph}
                </p>
              ))}
            </CardContent>
          </Card>

          <Card className="report-card">
            <CardHeader>
              <CardTitle>6. Recommended Focus Areas</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4">
              <p className="text-sm text-muted-foreground">
                Based on this pattern, these appear to be the most useful places to direct attention.
              </p>
              {report.recommended_focus_areas.map((area) => (
                <div key={`${area.rank}-${area.title}`} className="rounded-lg border p-4">
                  <div className="font-medium">{area.title}</div>
                  <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                    <span className="font-medium text-foreground">Why this matters: </span>
                    {area.why_this_matters}
                  </p>
                  <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                    <span className="font-medium text-foreground">Reflective question: </span>
                    {area.reflective_question}
                  </p>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card className="report-card">
            <CardHeader>
              <CardTitle>7. Suggested Next Steps</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc space-y-2 pl-5 text-sm text-muted-foreground">
                {report.suggested_next_steps.map((step) => (
                  <li key={step}>{step}</li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card className="report-card">
            <CardHeader>
              <CardTitle>8. Closing Reflection</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed text-muted-foreground">{report.closing_reflection}</p>
            </CardContent>
          </Card>

          {results.data.flags.length ? (
            <Card className="report-card">
              <CardHeader>
                <CardTitle>Triggered pattern insights</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-3">
                {results.data.flags.map((flag) => (
                  <div key={flag.flag} className="rounded-lg border p-3">
                    <div className="text-sm font-medium">{flag.flag}</div>
                    <div className="mt-1 text-sm text-muted-foreground">{flag.insight}</div>
                  </div>
                ))}
              </CardContent>
            </Card>
          ) : null}
        </div>
      )}
    </AppShell>
  );
}
