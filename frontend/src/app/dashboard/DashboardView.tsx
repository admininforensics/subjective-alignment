"use client";

import { AppShell } from "@/components/layout/AppShell";
import DashboardClient from "./DashboardClient";

export default function DashboardView() {
  return (
    <AppShell title="Dashboard" description="Your assessment progress and latest results.">
      <DashboardClient />
    </AppShell>
  );
}
