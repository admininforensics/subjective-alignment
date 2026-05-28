"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
    <div className="flex flex-1 items-center justify-center px-6 py-12">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Create account</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            className="grid gap-4"
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
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="org">Organisation name</Label>
              <Input
                id="org"
                value={organisationName}
                onChange={(e) => setOrganisationName(e.target.value)}
                placeholder="Optional"
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
            >
              {signup.isPending ? "Creating…" : "Sign up"}
            </Button>

            <p className="text-sm text-muted-foreground">
              Already have an account?{" "}
              <Link href="/login" className="underline underline-offset-4">
                Sign in
              </Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

