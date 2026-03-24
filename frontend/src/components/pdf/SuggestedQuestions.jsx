export default function SuggestedQuestions({ questions, onSelect }) {
  if (!questions?.length) return null;
  return (
    <div className="flex items-center gap-2 px-4 py-2.5 border-b border-border overflow-x-auto flex-shrink-0"
         style={{ scrollbarWidth: "none" }}>
      <span className="text-[9px] font-bold text-hint uppercase tracking-widest flex-shrink-0">
        Suggested
      </span>
      {questions.map((q, i) => (
        <button
          key={i}
          onClick={() => onSelect(q)}
          className="bg-base border border-border rounded-full px-3 py-1 text-[11px]
                     text-muted whitespace-nowrap flex-shrink-0 cursor-pointer
                     hover:border-primary hover:text-secondary transition-colors duration-150"
        >
          {q}
        </button>
      ))}
    </div>
  );
}
