import { useState } from "react";
import Sidebar from "./Sidebar";

export default function Layout({ children, showSidebar = true }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  if (!showSidebar) return <>{children}</>;

  return (
    <div className="flex min-h-screen bg-base">

      {/* Mobile overlay backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-60 z-20 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed md:sticky top-0 z-30 h-screen transition-transform duration-300 ease-in-out
        ${sidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}
      `}>
        <Sidebar onClose={() => setSidebarOpen(false)} />
      </div>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto min-w-0 w-full">
        {/* Mobile topbar */}
        <div className="md:hidden flex items-center gap-3 px-4 py-3 border-b border-border bg-base sticky top-0 z-10">
          <button
            onClick={() => setSidebarOpen(true)}
            className="text-muted hover:text-linen transition-colors bg-transparent border-none cursor-pointer p-1"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <line x1="3" y1="6" x2="21" y2="6"/>
              <line x1="3" y1="12" x2="21" y2="12"/>
              <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>
          <div className="text-sm font-extrabold tracking-tight">
            Visionary<span className="text-primary">X</span>
          </div>
        </div>
        {children}
      </main>

    </div>
  );
}