export default function CitationCard({ citation, index }) {
  return (
    <div className="card text-xs">
      <span className="text-brand-400 font-medium">Page {citation.page}</span>
      <p className="text-gray-400 mt-1 leading-relaxed">{citation.chunk}</p>
    </div>
  );
}
