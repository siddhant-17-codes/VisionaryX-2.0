import { useEffect, useState } from "react";
import { wakeServer } from "../../api/health";
import ServerStatusBanner from "./ServerStatusBanner";
import Sidebar from "./Sidebar";

export default function Layout({ children, showSidebar = true }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => { wakeServer(); }, []);

  if (!showSidebar) return <>{children}</>;

  return (
    // Exactly the visible height (dvh excludes mobile browser bars; h-screen is the
    // fallback). Only the content area below scrolls, so the menu bar stays put.
    <div className="flex h-screen h-dvh overflow-hidden bg-base">

      {/* Mobile overlay backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-60 z-20 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed md:static top-0 z-30 h-screen h-dvh transition-transform duration-300 ease-in-out
        ${sidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}
      `}>
        <Sidebar onClose={() => setSidebarOpen(false)} />
      </div>

      {/* Main content */}
      <main className="flex-1 min-w-0 w-full flex flex-col">
        {/* Mobile topbar */}
        <div className="md:hidden flex items-center gap-3 px-4 py-3 border-b border-border bg-base flex-shrink-0">
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
        <ServerStatusBanner />
        <div className="flex-1 min-h-0 overflow-y-auto">
          {children}
        </div>
      </main>

    </div>
  );
}