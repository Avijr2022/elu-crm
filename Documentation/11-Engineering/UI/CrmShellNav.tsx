"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState, useTransition } from "react";

export type Tenant = { id: string; code: string; name: string };

export type ShellNavItem = {
  href: string;
  label: string;
  icon: React.ReactNode;
};

export type CrmShellNavProps = {
  children: React.ReactNode;
  tenants: Tenant[];
  initialTenantId: string;
  onTenantSwitch?: (tenantId: string) => Promise<void> | void;
  navItems?: ShellNavItem[];
};

const defaultNav: ShellNavItem[] = [
  {
    href: "/crm/dashboard",
    label: "Dashboard",
    icon: (
      <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M4 10.5L12 4l8 6.5V20a1 1 0 01-1 1h-5v-6H10v6H5a1 1 0 01-1-1v-9.5z" />
      </svg>
    ),
  },
  {
    href: "/crm/leads",
    label: "Leads",
    icon: (
      <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2" />
        <circle cx="9" cy="7" r="4" />
      </svg>
    ),
  },
  {
    href: "/crm/opportunities",
    label: "Opportunities",
    icon: (
      <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M3 3v18h18" />
        <path d="M18 17V9" />
        <path d="M13 17V5" />
        <path d="M8 17v-3" />
      </svg>
    ),
  },
];

const isActive = (pathname: string, href: string) =>
  pathname === href || pathname.startsWith(`${href}/`);

function TenantSwitcher({
  tenants,
  value,
  onChange,
  loading,
}: {
  tenants: Tenant[];
  value: string;
  onChange: (id: string) => void;
  loading?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const active = tenants.find((t) => t.id === value);

  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (!ref.current?.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  return (
    <div ref={ref} className="relative w-full max-w-xs">
      <button
        type="button"
        disabled={loading || !tenants.length}
        onClick={() => setOpen((v) => !v)}
        className="flex h-10 w-full items-center justify-between rounded-lg border border-slate-200 bg-white px-3 text-sm font-medium text-slate-900 hover:bg-slate-50 disabled:opacity-60"
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        <span className="truncate">{loading ? "Switching…" : active?.name ?? "Workspace"}</span>
        <span className="ml-2 shrink-0 text-xs text-slate-500">{active?.code}</span>
      </button>
      {open && (
        <ul role="listbox" className="absolute z-50 mt-1 max-h-56 w-full overflow-auto rounded-lg border bg-white py-1 shadow-lg">
          {tenants.map((t) => (
            <li key={t.id}>
              <button
                type="button"
                role="option"
                aria-selected={t.id === value}
                onClick={() => {
                  onChange(t.id);
                  setOpen(false);
                }}
                className={`flex w-full items-center justify-between px-3 py-2 text-left text-sm hover:bg-slate-50 ${
                  t.id === value ? "bg-slate-100 font-semibold" : ""
                }`}
              >
                <span className="truncate">{t.name}</span>
                <span className="text-xs text-slate-500">{t.code}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function ShellSidebar({
  items,
  onNavigate,
}: {
  items: ShellNavItem[];
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  return (
    <nav className="flex flex-1 flex-col gap-1 p-3" aria-label="Main">
      {items.map((item) => {
        const active = isActive(pathname, item.href);
        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            className={`flex min-h-11 items-center gap-3 rounded-lg px-3 text-sm font-medium ${
              active ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
            }`}
            aria-current={active ? "page" : undefined}
          >
            <span className="shrink-0">{item.icon}</span>
            <span className="truncate">{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}

export function CrmShellNav({
  children,
  tenants,
  initialTenantId,
  onTenantSwitch,
  navItems = defaultNav,
}: CrmShellNavProps) {
  const router = useRouter();
  const [tenantId, setTenantId] = useState(initialTenantId);
  const [tenantLoading, setTenantLoading] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isPending, startTransition] = useTransition();
  const closeMobile = useCallback(() => setMobileOpen(false), []);

  const handleTenantChange = useCallback(
    async (next: string) => {
      if (next === tenantId) return;
      setTenantLoading(true);
      try {
        await onTenantSwitch?.(next);
        setTenantId(next);
        startTransition(() => router.refresh());
      } finally {
        setTenantLoading(false);
      }
    },
    [tenantId, onTenantSwitch, router]
  );

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900">
      <aside className="hidden w-64 shrink-0 flex-col border-r border-slate-200 bg-white lg:flex">
        <div className="border-b border-slate-200 p-4 text-sm font-semibold">E-LinkUp CRM</div>
        <ShellSidebar items={navItems} />
      </aside>

      {mobileOpen && (
        <button
          type="button"
          aria-label="Close menu overlay"
          className="fixed inset-0 z-40 bg-black/40 lg:hidden"
          onClick={closeMobile}
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-slate-200 bg-white transition-transform lg:hidden ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-14 items-center border-b border-slate-200 px-4 text-sm font-semibold">
          E-LinkUp CRM
        </div>
        <ShellSidebar items={navItems} onNavigate={closeMobile} />
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 items-center gap-3 border-b border-slate-200 bg-white px-4">
          <button
            type="button"
            className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-slate-200 lg:hidden"
            aria-label="Toggle menu"
            aria-expanded={mobileOpen}
            onClick={() => setMobileOpen((v) => !v)}
          >
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 7h16M4 12h16M4 17h16" />
            </svg>
          </button>
          <div className="flex-1">
            <TenantSwitcher
              tenants={tenants}
              value={tenantId}
              onChange={handleTenantChange}
              loading={tenantLoading}
            />
          </div>
        </header>
        <main className="relative flex-1 p-4 md:p-6">
          {(isPending || tenantLoading) && (
            <div className="pointer-events-none absolute inset-x-0 top-0 z-10 h-0.5 bg-slate-900" />
          )}
          {children}
        </main>
      </div>
    </div>
  );
}
