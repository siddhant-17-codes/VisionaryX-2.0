export default function SuggestedQuestions({ questions, onSelect }) {
  if (!questions?.length) return null;
  return (
    <div className="p-4 space-y-2">
      <p className="text-xs text-gray-400 font-medium uppercase tracking-wide">Suggested questions</p>
      {questions.map((q, i) => (
        <button
          key={i}
          onClick={() => onSelect(q)}
          className="w-full text-left text-sm bg-surface-700 hover:bg-surface-600 border border-surface-600 rounded-lg px-4 py-2.5 text-gray-200 transition-colors"
        >
          {q}
        </button>
      ))}
    </div>
  );
}
