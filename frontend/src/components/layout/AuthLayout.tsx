"use client";

import { PRODUCT_TAGLINE } from "@/lib/branding";
import Image from "next/image";
import Link from "next/link";
import { ReactNode, useState } from "react";

type AuthLayoutProps = {
  children: ReactNode;
  title: string;
  subtitle?: string;
};

export function AuthLayout({ children, title, subtitle }: AuthLayoutProps) {
  const [bgError, setBgError] = useState(false);

  return (
    <div className="flex min-h-screen flex-col lg:flex-row">
      {/* Left: brand panel */}
      <div className="relative hidden min-h-[280px] flex-1 overflow-hidden lg:flex lg:min-h-screen">
        {!bgError ? (
          <Image
            src="/images/login-background.jpg"
            alt=""
            fill
            priority
            className="object-cover"
            onError={() => setBgError(true)}
          />
        ) : null}
        <div
          className="absolute inset-0 bg-gradient-to-br from-[#3d6b84]/90 via-[#2d5569]/85 to-[#1e3a4d]/90"
          aria-hidden
        />
        <div className="relative z-10 flex flex-col justify-between p-10 text-white">
          <div>
            <Link href="/" className="font-heading text-xl font-semibold tracking-tight">
              Subjective Alignment
            </Link>
          </div>
          <div className="max-w-md space-y-4">
            <p className="font-heading text-3xl font-semibold leading-snug tracking-tight">
              Understand alignment between who you are and how you work.
            </p>
            <p className="text-base leading-relaxed text-white/85">{PRODUCT_TAGLINE}</p>
          </div>
          <p className="text-sm text-white/60">Confidential · Evidence-based · For workplace growth</p>
        </div>
      </div>

      {/* Mobile brand strip */}
      <div className="border-b border-border bg-accent px-6 py-4 lg:hidden">
        <p className="font-heading text-lg font-semibold text-foreground">Subjective Alignment</p>
        <p className="mt-1 text-sm text-muted-foreground">{PRODUCT_TAGLINE}</p>
      </div>

      {/* Right: form */}
      <div className="flex flex-1 flex-col justify-center px-6 py-10 sm:px-10 lg:max-w-lg lg:px-14 xl:max-w-xl">
        <div className="mx-auto w-full max-w-md space-y-6">
          <div className="space-y-1">
            <h1 className="font-heading text-2xl font-semibold">{title}</h1>
            {subtitle ? <p className="text-sm text-muted-foreground">{subtitle}</p> : null}
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}
