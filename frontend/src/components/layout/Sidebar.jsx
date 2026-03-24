import { NavLink, useNavigate } from "react-router-dom";
import { useSessionContext } from "../../context/SessionContext";
import { ChatIcon, PDFIcon, ImageIcon, SparkleIcon, PlusIcon, TrashIcon } from "../icons/Icons";

const navItems = [
  { to: "/workspace/chat",     label: "Chat",          Icon: ChatIcon    },
  { to: "/workspace/pdf",      label: "PDF Chat",      Icon: PDFIcon     },
  { to: "/workspace/image",    label: "Image Query",   Icon: ImageIcon   },
  { to: "/workspace/generate", label: "Text to Image", Icon: SparkleIcon },
];

const modeRouteMap = { chat: "/workspace/chat", pdf: "/workspace/pdf", image: "/workspace/image", generate: "/workspace/generate" };

export default function Sidebar() {
  const { sessions, newSession, removeSession } = useSessionContext();
  const navigate = useNavigate();

  const handleNewChat = async () => {
    const session = await newSession("chat");
    navigate("/workspace/chat", { state: { sessionId: session.id } });
  };

  const handleSessionClick = (session) => {
    const route = modeRouteMap[session.mode] || "/workspace/chat";
    navigate(route, { state: { sessionId: session.id, restore: true } });
  };

  return (
    <aside className="w-[210px] bg-base border-r border-border flex flex-col h-screen sticky top-0 flex-shrink-0">
      {/* Brand — click goes to landing */}
      <div className="px-4 py-4 border-b border-border">
        <div
          className="text-[13px] font-extrabold text-linen tracking-tight cursor-pointer hover:text-primary transition-colors"
          onClick={() => navigate("/")}
        >
          Visionary<span className="text-primary">X</span>
        </div>
        <div className="text-[9px] text-hint mt-0.5">AI workspace 2.0</div>
        <button
          onClick={handleNewChat}
          className="mt-3 w-full flex items-center justify-center gap-1.5 bg-primary
                     text-linen text-[11px] font-bold py-2 rounded-lg hover:bg-orange-500
                     active:scale-95 transition-all duration-150 border-none cursor-pointer"
        >
          <PlusIcon size={12} color="#FCF5EF" />
          New chat
        </button>
      </div>

      {/* Navigation */}
      <nav className="px-2 py-3">
        <div className="text-[9px] font-bold text-dim uppercase tracking-widest mb-1.5 px-2">Navigate</div>
        {navItems.map(({ to, label, Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `sidebar-item ${isActive ? "sidebar-item-active" : ""}`
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={14} color={isActive ? "#FE7235" : "#4A3D5A"} />
                <span className="flex-1">{label}</span>
                <span className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                      style={{ background: isActive ? "#FE7235" : "#2A2040" }} />
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Session History */}
      {sessions.length > 0 && (
        <div className="px-2 flex-1 overflow-y-auto">
          <div className="text-[9px] font-bold text-dim uppercase tracking-widest mb-1.5 px-2 mt-2">Recent</div>
          {sessions.slice(0, 12).map((s) => (
            <div
              key={s.id}
              onClick={() => handleSessionClick(s)}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg
                         cursor-pointer hover:bg-surface group transition-colors"
            >
              <span className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                    style={{ background: s.mode === "pdf" ? "#00C3FF" : s.mode === "image" ? "#0077FF" : s.mode === "generate" ? "#FEA735" : "#FEA735" }} />
              <span className="text-[11px] text-muted truncate flex-1">{s.title}</span>
              <button
                onClick={(e) => { e.stopPropagation(); removeSession(s.id); }}
                className="opacity-0 group-hover:opacity-100 transition-opacity p-0.5 rounded hover:text-red-400 btn-icon"
              >
                <TrashIcon size={11} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Footer */}
      <div className="px-4 py-3 border-t border-border mt-auto">
        <div className="text-[9px] text-dim text-center">
          Model: <span className="text-cyan font-bold">Gemini 2.5 Flash</span>
        </div>
      </div>
    </aside>
  );
}
