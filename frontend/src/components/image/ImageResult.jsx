import ReactMarkdown from "react-markdown";

export default function ImageResult({ answer }) {
  if (!answer) return null;
  return (
    <div className="card mt-4">
      <p className="text-xs text-brand-400 font-medium mb-2 uppercase tracking-wide">VisionaryX Response</p>
      <div className="text-sm text-gray-200 leading-relaxed prose prose-invert max-w-none">
        <ReactMarkdown>{answer}</ReactMarkdown>
      </div>
    </div>
  );
}
