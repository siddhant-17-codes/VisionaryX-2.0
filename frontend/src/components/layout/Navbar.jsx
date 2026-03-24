import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { GithubIcon } from "../icons/Icons";

export default function Navbar({ onFeaturesClick }) {
  const navigate = useNavigate();
  const [showDemo, setShowDemo] = useState(false);

  return (
    <>
      <nav className="flex items-center justify-between px-8 py-4 border-b border-border bg-base sticky top-0 z-10">
        <div
          onClick={() => navigate("/")}
          className="text-[17px] font-extrabold tracking-tight cursor-pointer"
        >
          Visionary<span className="text-primary">X</span>
          <span className="ml-2 bg-primary text-linen text-[9px] font-bold
                           px-2 py-0.5 rounded-full align-middle">2.0</span>
        </div>
        <div className="flex items-center gap-6">
          <button
            onClick={onFeaturesClick}
            className="text-xs text-hint font-medium cursor-pointer hover:text-linen transition-colors bg-transparent border-none"
          >Features</button>
          <button
            onClick={() => setShowDemo(true)}
            className="text-xs text-hint font-medium cursor-pointer hover:text-linen transition-colors bg-transparent border-none"
          >Demo</button>
          <a href="https://github.com/siddhant-17-codes/VisionaryX-2.0"
             target="_blank" rel="noreferrer"
             className="flex items-center gap-1.5 text-xs text-hint hover:text-linen transition-colors">
            <GithubIcon size={14} />GitHub
          </a>
        </div>
        <button onClick={() => navigate("/workspace/chat")} className="btn-primary py-2 px-5 text-xs">
          Launch workspace
        </button>
      </nav>

      {/* Demo Modal */}
      {showDemo && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-6"
          style={{ background: "rgba(8,6,14,0.85)", backdropFilter: "blur(4px)" }}
          onClick={() => setShowDemo(false)}
        >
          <div
            className="bg-surface border border-border rounded-2xl p-8 max-w-xl w-full max-h-[80vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-base font-bold text-linen">How to use VisionaryX</h2>
                <p className="text-[10px] text-hint mt-0.5">Quick guide to all four features</p>
              </div>
              <button onClick={() => setShowDemo(false)}
                      className="text-hint hover:text-linen text-lg bg-transparent border-none cursor-pointer">✕</button>
            </div>
            {[
              { color:"#FE7235", title:"PDF Chat + RAG", steps:["Click PDF Chat in the sidebar","Upload one or more PDF or DOCX files","Wait for indexing — suggested questions appear automatically","Ask anything about your documents","Every answer shows page-level source citations"] },
              { color:"#FE7235", title:"General Chat", steps:["Click Chat in the sidebar","Type any question and press Send","Conversation memory is maintained across turns","All sessions are saved — click Recent to revisit"] },
              { color:"#0077FF", title:"Image Query", steps:["Click Image Query in the sidebar","Upload any JPG or PNG image","Optionally type a specific question","Click Analyse Image — Gemini Vision responds in detail"] },
              { color:"#FEA735", title:"Text to Image", steps:["Click Text to Image in the sidebar","Describe what you want to see","Click Generate Image (takes 15–30s)","Download the result when ready"] },
            ].map(({ color, title, steps }) => (
              <div key={title} className="mb-6 last:mb-0">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-2 h-2 rounded-full" style={{ background: color }} />
                  <h3 className="text-sm font-semibold text-linen">{title}</h3>
                </div>
                <ol className="space-y-1.5">
                  {steps.map((s, i) => (
                    <li key={i} className="flex gap-2 text-[11px] text-muted">
                      <span className="text-hint flex-shrink-0">{i+1}.</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ol>
              </div>
            ))}
            <button onClick={() => { setShowDemo(false); navigate("/workspace/chat"); }}
                    className="btn-primary w-full mt-4">
              Launch workspace →
            </button>
          </div>
        </div>
      )}
    </>
  );
}
