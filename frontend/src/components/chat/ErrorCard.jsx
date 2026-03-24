import { parseApiError } from "../../utils/errorHandler";

export default function ErrorCard({ error, onRetry }) {
  if (!error) return null;
  const parsed = parseApiError(error instanceof Error ? error : new Error(error));

  const icons = {
    quota:     { bg: "#1A0A04", border: "#3A1808", color: "#FEA735", symbol: "⚠" },
    ratelimit: { bg: "#1A0A04", border: "#3A1808", color: "#FEA735", symbol: "⏱" },
    network:   { bg: "#0A1020", border: "#1C2A40", color: "#00C3FF", symbol: "⚡" },
    server:    { bg: "#1A0A04", border: "#3A1808", color: "#FE7235", symbol: "✕" },
    unknown:   { bg: "#100D1A", border: "#2A2040", color: "#6B5E7A", symbol: "?" },
  };
  const style = icons[parsed.type] || icons.unknown;

  return (
    <div className="mx-4 mb-3 rounded-xl border p-4"
         style={{ background: style.bg, borderColor: style.border }}>
      <div className="flex items-start gap-3">
        <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 text-sm font-bold"
             style={{ background: style.border, color: style.color }}>
          {style.symbol}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold mb-0.5" style={{ color: style.color }}>
            {parsed.title}
          </p>
          <p className="text-xs text-muted leading-relaxed mb-1">{parsed.message}</p>
          <p className="text-[10px] text-hint leading-relaxed">{parsed.guidance}</p>
        </div>
      </div>
      {parsed.retryable && onRetry && (
        <button
          onClick={onRetry}
          className="mt-3 text-xs font-semibold px-4 py-1.5 rounded-lg border transition-colors cursor-pointer bg-transparent"
          style={{ color: style.color, borderColor: style.border }}
        >
          Try again
        </button>
      )}
    </div>
  );
}
