import { useNavigate } from "react-router-dom";

const features = [
  { to: "/chat",     icon: "💬", title: "General Chat",    desc: "Conversational AI with full memory across turns." },
  { to: "/pdf",      icon: "📄", title: "PDF Chat + RAG",  desc: "Upload docs, get cited answers with page numbers." },
  { to: "/image",    icon: "🖼️", title: "Image Query",     desc: "Analyse any image with Gemini Vision." },
  { to: "/generate", icon: "✨", title: "Text to Image",   desc: "Turn descriptions into AI-generated visuals." },
];

export default function Home() {
  const nav = useNavigate();
  return (
    <div className="max-w-4xl mx-auto px-6 py-16">
      <div className="mb-12">
        <h1 className="text-4xl font-semibold mb-3">
          <span className="text-brand-400">Visionary</span>X <span className="text-gray-400 text-2xl font-normal">2.0</span>
        </h1>
        <p className="text-gray-400 text-lg max-w-xl">
          An intelligent AI workspace — query documents, analyse images, and generate visuals, all powered by Gemini and FAISS.
        </p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {features.map(({ to, icon, title, desc }) => (
          <button
            key={to}
            onClick={() => nav(to)}
            className="card text-left hover:border-brand-400 transition-colors group"
          >
            <span style={{ fontSize: 24 }}>{icon}</span>
            <h2 className="mt-3 font-medium text-white group-hover:text-brand-400 transition-colors">{title}</h2>
            <p className="text-sm text-gray-400 mt-1">{desc}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
