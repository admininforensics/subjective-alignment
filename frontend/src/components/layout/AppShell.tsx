"use client";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Separator } from "@/components/ui/separator";
import { clearAuth, getUser } from "@/lib/auth";
import type { AuthUser } from "@/lib/types";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useMemo, useSyncExternalStore } from "react";

const NAV = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/admin", label: "Admin", roles: ["ORG_ADMIN", "SUPER_ADMIN", "MANAGER"] as const },
] as const;

function initials(email: string) {
  const part = email.split("@")[0] ?? "?";
  return part.slice(0, 2).toUpperCase();
}

type AppShellProps = {
  children: ReactNode;
  title?: string;
  description?: string;
};

export function AppShell({ children, title, description }: AppShellProps) {
  const router = useRouter();
  const pathname = usePathname();
  const hydrated = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false
  );
  const user = useMemo(() => (hydrated ? getUser() : null), [hydrated]) as AuthUser | null;

  const visibleNav = NAV.filter((item) => {
    if (!("roles" in item)) return true;
    if (!user) return false;
    return item.roles.includes(user.role as (typeof item.roles)[number]);
  });

  const signOut = () => {
    clearAuth();
    router.replace("/login");
  };

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-50 border-b border-border bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/80">
        <div className="mx-auto flex h-14 max-w-6xl items-center gap-6 px-4 sm:px-6">
          <Link
            href="/dashboard"
            className="font-heading text-base font-semibold text-foreground transition-ui hover:text-brand"
          >
            Subjective Alignment
          </Link>

          <nav className="hidden items-center gap-1 sm:flex">
            {visibleNav.map((item) => {
              const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "rounded-md px-3 py-1.5 text-sm font-medium transition-ui",
                    active
                      ? "bg-accent text-accent-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="ml-auto flex items-center gap-2">
            {user ? (
              <DropdownMenu>
                <DropdownMenuTrigger className="inline-flex h-9 items-center gap-2 rounded-md px-2 text-sm transition-ui hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback className="bg-accent text-xs font-medium text-accent-foreground">
                        {initials(user.email)}
                      </AvatarFallback>
                    </Avatar>
                    <span className="hidden max-w-[140px] truncate sm:inline">{user.email}</span>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuLabel className="font-normal">
                    <p className="text-sm font-medium">{user.email}</p>
                    <p className="text-xs text-muted-foreground">{user.role.replace("_", " ")}</p>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="sm:hidden" onClick={() => router.push("/dashboard")}>
                    Dashboard
                  </DropdownMenuItem>
                  {visibleNav
                    .filter((n) => n.href !== "/dashboard")
                    .map((item) => (
                      <DropdownMenuItem
                        key={item.href}
                        className="sm:hidden"
                        onClick={() => router.push(item.href)}
                      >
                        {item.label}
                      </DropdownMenuItem>
                    ))}
                  <DropdownMenuSeparator className="sm:hidden" />
                  <DropdownMenuItem onClick={signOut} className="text-destructive focus:text-destructive">
                    Sign out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : null}
          </div>
        </div>
      </header>

      <main className="flex-1">
        <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
          {title ? (
            <div className="mb-8 space-y-1">
              <h1 className="font-heading text-2xl font-semibold tracking-tight">{title}</h1>
              {description ? <p className="text-sm text-muted-foreground">{description}</p> : null}
              <Separator className="mt-4" />
            </div>
          ) : null}
          {children}
        </div>
      </main>
    </div>
  );
}
