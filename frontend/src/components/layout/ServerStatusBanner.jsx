import { useServerStatus, wakeServer } from "../../api/health";

export default function ServerStatusBanner() {
  const status = useServerStatus();
  if (status !== "waking" && status !== "offline") return null;

  const waking = status === "waking";
  return (
    // Floats over the page header (pages are h-screen, so an inline banner would push
    // the chat input off screen). Centred on the main column; the sidebar is 210px.
    <div role="status" aria-live="polite"
         className="fixed top-14 md:top-3 left-1/2 md:left-[calc(50%+105px)] -translate-x-1/2 z-40
                    w-[min(92vw,520px)] rounded-xl border px-4 py-3 flex items-center gap-3 shadow-lg"
         style={{ background: "#0A1020", borderColor: "#1C2A40" }}>
      {waking && (
        <span className="w-3 h-3 rounded-full border-2 border-[#00C3FF] border-t-transparent animate-spin flex-shrink-0" />
      )}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold" style={{ color: "#00C3FF" }}>
          {waking ? "Waking up the server…" : "Can't reach the server"}
        </p>
        <p className="text-xs text-muted leading-relaxed">
          {waking
            ? "The free server sleeps when idle and can take up to a minute to start. Your first answer may be slow."
            : "It may still be starting, or your connection dropped."}
        </p>
      </div>
      {!waking && (
        <button onClick={() => wakeServer()}
                className="text-xs font-semibold px-3 py-1.5 rounded-lg border cursor-pointer bg-transparent"
                style={{ color: "#00C3FF", borderColor: "#1C2A40" }}>
          Try again
        </button>
      )}
    </div>
  );
}
