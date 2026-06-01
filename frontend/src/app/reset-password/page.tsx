"use client";

import { AuthLayout } from "@/components/layout/AuthLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiFetch } from "@/lib/api";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

type ResetConfirmResponse = { detail: string };

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const uid = searchParams.get("uid") ?? "";
  const token = searchParams.get("token") ?? "";

  const [password, setPassword] = useState("");
  const [repeatPassword, setRepeatPassword] = useState("");

  const reset = useMutation({
    mutationFn: async () =>
      apiFetch<ResetConfirmResponse>("/auth/password-reset/confirm/", {
        method: "POST",
        body: JSON.stringify({ uid, token, password }),
      }),
    onSuccess: () => router.replace("/login"),
  });

  const linkInvalid = !uid || !token;

  return (
    <AuthLayout title="Choose a new password" subtitle="Use a password you do not use elsewhere.">
      <div className="rounded-lg border border-border bg-card p-6 shadow-sm">
        {linkInvalid ? (
          <div className="grid gap-4">
            <p className="text-sm text-destructive">
              This reset link is invalid or incomplete. Request a new one.
            </p>
            <Link
              href="/forgot-password"
              className="text-sm font-medium text-brand underline-offset-4 hover:underline"
            >
              Request reset link
            </Link>
          </div>
        ) : (
          <form
            className="grid gap-5"
            onSubmit={(e) => {
              e.preventDefault();
              reset.mutate();
            }}
          >
            <div className="grid gap-2">
              <Label htmlFor="password">New password</Label>
              <Input
                id="password"
                type="password"
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                className="transition-ui"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="repeatPassword">Repeat password</Label>
              <Input
                id="repeatPassword"
                type="password"
                autoComplete="new-password"
                value={repeatPassword}
                onChange={(e) => setRepeatPassword(e.target.value)}
                required
                minLength={6}
                className="transition-ui"
              />
            </div>
            {repeatPassword && password !== repeatPassword ? (
              <p className="text-sm text-destructive">Passwords do not match</p>
            ) : reset.error ? (
              <p className="text-sm text-destructive">{reset.error.message}</p>
            ) : reset.isSuccess ? (
              <p className="text-sm text-muted-foreground">Password updated. Redirecting…</p>
            ) : null}
            <Button
              type="submit"
              disabled={
                reset.isPending || !password || password !== repeatPassword || password.length < 6
              }
              className="transition-ui"
            >
              {reset.isPending ? "Updating…" : "Update password"}
            </Button>
            <p className="text-center text-sm text-muted-foreground">
              <Link href="/login" className="font-medium text-brand underline-offset-4 hover:underline">
                Back to sign in
              </Link>
            </p>
          </form>
        )}
      </div>
    </AuthLayout>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div className="p-8 text-sm text-muted-foreground">Loading…</div>}>
      <ResetPasswordForm />
    </Suspense>
  );
}
