const barColors = ["#0077FF", "#00C3FF", "#FEA735", "#FE7235"];
const numColors = ["#0077FF", "#00C3FF", "#FEA735", "#FE7235"];

export default function CitationCard({ citation, index }) {
  const color = barColors[index % barColors.length];
  const numBg = numColors[index % numColors.length];
  return (
    <div className="bg-base border border-border rounded-lg p-2.5 flex-1 min-w-[160px] max-w-[260px]">
      <div
        className="h-0.5 rounded mb-2"
        style={{ background: `linear-gradient(90deg,${color},transparent)` }}
      />
      <div className="flex items-center gap-1.5 mb-1.5">
        <div
          className="w-4 h-4 rounded text-[8px] font-bold text-linen
                     flex items-center justify-center flex-shrink-0"
          style={{ background: numBg }}
        >
          {index + 1}
        </div>
        {/* Answers from indexes built before sources were stored have no file name. */}
        {citation.source && (
          <span className="text-[9px] font-semibold text-muted truncate min-w-0" title={citation.source}>
            {citation.source}
          </span>
        )}
        <span className="text-[9px] font-semibold flex-shrink-0" style={{ color }}>
          {citation.source ? `· p. ${citation.page}` : `Page ${citation.page}`}
        </span>
      </div>
      <p className="text-[10px] text-hint leading-relaxed line-clamp-3">{citation.chunk}</p>
    </div>
  );
}
