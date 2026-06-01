"use client";

import dynamic from "next/dynamic";

const AdminView = dynamic(() => import("./AdminView"), { ssr: false });

export default function AdminPage() {
  return <AdminView />;
}
