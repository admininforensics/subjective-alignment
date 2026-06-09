"use client";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { clearAuth, useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";
import { Menu } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useState } from "react";

const NAV = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/admin", label: "Admin", roles: ["ORG_ADMIN", "SUPER_ADMIN", "MANAGER"] as const },
] as const;

function initials(email: string) {
  const part = email.split("@")[0] ?? "?";
  return part.slice(0, 2).toUpperCase();
}

function formatRole(role: string | undefined) {
  return role ? role.replaceAll("_", " ") : "User";
}

type AppShellProps = {
  children: ReactNode;
  title?: string;
  description?: string;
};

export function AppShell({ children, title, description }: AppShellProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const { accessToken, user } = useAuth();

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
      <header className="app-shell-header sticky top-0 z-50 border-b border-border bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/80">
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
            {visibleNav.length > 1 ? (
              <div className="relative sm:hidden">
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  aria-label="Open navigation menu"
                  aria-expanded={mobileNavOpen}
                  onClick={() => setMobileNavOpen((open) => !open)}
                >
                  <Menu className="h-5 w-5" />
                </Button>
                {mobileNavOpen ? (
                  <>
                    <button
                      type="button"
                      className="fixed inset-0 z-40 cursor-default bg-transparent"
                      aria-label="Close navigation menu"
                      onClick={() => setMobileNavOpen(false)}
                    />
                    <div className="absolute right-0 z-50 mt-1 w-44 rounded-lg border border-border bg-popover p-1 shadow-md">
                      {visibleNav.map((item) => (
                        <Link
                          key={item.href}
                          href={item.href}
                          className="block rounded-md px-2 py-1.5 text-sm font-medium text-foreground transition-ui hover:bg-muted"
                          onClick={() => setMobileNavOpen(false)}
                        >
                          {item.label}
                        </Link>
                      ))}
                    </div>
                  </>
                ) : null}
              </div>
            ) : null}

            {user && accessToken ? (
              <>
                <div
                  className="flex h-9 max-w-[200px] items-center gap-2 rounded-md px-2"
                  title={`${user.email} · ${formatRole(user.role)}`}
                >
                  <Avatar className="h-8 w-8 shrink-0">
                    <AvatarFallback className="bg-accent text-xs font-medium text-accent-foreground">
                      {initials(user.email)}
                    </AvatarFallback>
                  </Avatar>
                  <span className="hidden min-w-0 truncate text-sm text-muted-foreground md:inline">
                    {user.email}
                  </span>
                </div>
                <Button type="button" variant="secondary" size="sm" onClick={signOut}>
                  Sign out
                </Button>
              </>
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
