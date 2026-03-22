import { NavLink } from "react-router-dom";

const links = [
  { to: "/",        icon: "⬡", label: "Home"          },
  { to: "/chat",    icon: "💬", label: "Chat"          },
  { to: "/pdf",     icon: "📄", label: "PDF Chat"      },
  { to: "/image",   icon: "🖼️", label: "Image Query"   },
  { to: "/generate",icon: "✨", label: "Text to Image" },
];

export default function Sidebar() {
  return (
    <aside className="w-60 bg-surface-800 border-r border-surface-600 flex flex-col h-screen sticky top-0">
      <div className="px-6 py-5 border-b border-surface-600">
        <span className="text-xl font-semibold tracking-tight">
          <span className="text-brand-400">Visionary</span>X
        </span>
        <span className="ml-2 text-xs bg-brand-600 text-brand-50 px-2 py-0.5 rounded-full">2.0</span>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {links.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors duration-150 ${
                isActive
                  ? "bg-brand-600 text-white"
                  : "text-gray-400 hover:text-white hover:bg-surface-700"
              }`
            }
          >
            <span style={{ fontSize: 16 }}>{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="px-6 py-4 border-t border-surface-600 text-xs text-gray-500">
        Powered by Gemini 1.5 Flash
      </div>
    </aside>
  );
}
