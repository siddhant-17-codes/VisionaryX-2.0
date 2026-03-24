import ReactMarkdown from "react-markdown";

export default function ImageResult({ answer }) {
  if (!answer) return null;
  return (
    <div className="bg-base border border-border rounded-xl p-4 mt-4">
      <div className="badge-blue mb-3 inline-block">VisionaryX Response</div>
      <div className="text-sm text-muted leading-relaxed">
        <ReactMarkdown>{answer}</ReactMarkdown>
      </div>
    </div>
  );
}
