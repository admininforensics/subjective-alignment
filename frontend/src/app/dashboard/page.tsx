"use client";

import dynamic from "next/dynamic";

const DashboardView = dynamic(() => import("./DashboardView"), { ssr: false });

export default function DashboardPage() {
  return <DashboardView />;
}
