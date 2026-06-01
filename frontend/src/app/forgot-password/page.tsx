"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiFetch } from "@/lib/api";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";

type ResetRequestResponse = { detail: string };

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const requestReset = useMutation({
    mutationFn: async () =>
      apiFetch<ResetRequestResponse>("/auth/password-reset/", {
        method: "POST",
        body: JSON.stringify({ email: email.trim().toLowerCase() }),
      }),
    onSuccess: () => setSubmitted(true),
  });

  return (
    <div className="flex flex-1 items-center justify-center px-6 py-12">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Reset password</CardTitle>
        </CardHeader>
        <CardContent>
          {submitted ? (
            <div className="grid gap-4">
              <p className="text-sm text-muted-foreground">
                If an account exists for that email, you will receive a reset link shortly. Check
                your inbox and spam folder.
              </p>
              <Link href="/login" className="text-sm underline underline-offset-4">
                Back to sign in
              </Link>
            </div>
          ) : (
            <form
              className="grid gap-4"
              onSubmit={(e) => {
                e.preventDefault();
                requestReset.mutate();
              }}
            >
              <p className="text-sm text-muted-foreground">
                Enter your email and we will send you a link to choose a new password.
              </p>
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              {requestReset.error ? (
                <p className="text-sm text-destructive">{requestReset.error.message}</p>
              ) : null}
              <Button type="submit" disabled={requestReset.isPending || !email.trim()}>
                {requestReset.isPending ? "Sending…" : "Send reset link"}
              </Button>
              <p className="text-sm text-muted-foreground">
                <Link href="/login" className="underline underline-offset-4">
                  Back to sign in
                </Link>
              </p>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
