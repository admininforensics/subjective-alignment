"use client";

import { AuthLayout } from "@/components/layout/AuthLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiFetch } from "@/lib/api";
import { setAuth } from "@/lib/auth";
import type { LoginResponse } from "@/lib/types";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

type SignupResponse = LoginResponse;

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [repeatPassword, setRepeatPassword] = useState("");
  const [organisationName, setOrganisationName] = useState("");

  const signup = useMutation({
    mutationFn: async () =>
      apiFetch<SignupResponse>("/auth/signup/", {
        method: "POST",
        body: JSON.stringify({ email, password, organisation_name: organisationName }),
      }),
    onSuccess: (data) => {
      setAuth(data);
      router.replace("/dashboard");
    },
  });

  return (
    <AuthLayout title="Create account" subtitle="For individuals and organisations getting started.">
      <form
        className="grid gap-5 rounded-lg border border-border bg-card p-6 shadow-sm"
        onSubmit={(e) => {
          e.preventDefault();
          signup.mutate();
        }}
      >
        <div className="grid gap-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="transition-ui"
          />
        </div>
        <div className="grid gap-2">
          <Label htmlFor="org">Organisation name</Label>
          <Input
            id="org"
            value={organisationName}
            onChange={(e) => setOrganisationName(e.target.value)}
            placeholder="Optional"
            className="transition-ui"
          />
        </div>
        <div className="grid gap-2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
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
            className="transition-ui"
          />
        </div>

        {repeatPassword && password !== repeatPassword ? (
          <p className="text-sm text-destructive">Passwords do not match</p>
        ) : signup.error ? (
          <p className="text-sm text-destructive">{signup.error.message}</p>
        ) : null}

        <Button
          type="submit"
          disabled={signup.isPending || !email.trim() || !password || password !== repeatPassword}
          className="transition-ui"
        >
          {signup.isPending ? "Creating…" : "Sign up"}
        </Button>

        <p className="text-center text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-brand underline-offset-4 hover:underline">
            Sign in
          </Link>
        </p>
      </form>
    </AuthLayout>
  );
}
