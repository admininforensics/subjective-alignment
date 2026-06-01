"use client";

import { AppShell } from "@/components/layout/AppShell";
import AdminClient from "./AdminClient";

export default function AdminView() {
  return (
    <AppShell title="Admin" description="Organisation users and assessment visibility.">
      <AdminClient />
    </AppShell>
  );
}
