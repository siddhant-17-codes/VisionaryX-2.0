import { useNavigate } from "react-router-dom";
import { useRef } from "react";
import Navbar from "../components/layout/Navbar";
import { ChatIcon, PDFIcon, ImageIcon, SparkleIcon, GithubIcon } from "../components/icons/Icons";

const features = [
  {
    Icon: PDFIcon, iconBg: "#1E1008", iconBorder: "#3A2010", iconColor: "#FE7235",
    badge: "Hero feature", badgeClass: "badge-amber",
    title: "PDF Chat + RAG", route: "/workspace/pdf",
    desc: "Upload PDF or DOCX. Adaptive relevance threshold. Every answer includes inline page-level citations. Multi-document sessions persisted to disk.",
    tech: "FAISS · LangChain · Gemini",
  },
  {
    Icon: ChatIcon, iconBg: "#1E1008", iconBorder: "#3A2010", iconColor: "#FE7235",
    title: "General Chat", route: "/workspace/chat",
    desc: "Full conversation memory per turn. Chat sessions saved to disk. Sidebar shows all previous sessions. Start fresh anytime.",
    tech: "Gemini 2.5 Flash",
  },
  {
    Icon: ImageIcon, iconBg: "#060F1E", iconBorder: "#0D2040", iconColor: "#0077FF",
    title: "Image Query", route: "/workspace/image",
    desc: "Upload any image and ask anything about it. Gemini Vision returns detailed structured analysis.",
    tech: "Gemini Vision",
  },
  {
    Icon: SparkleIcon, iconBg: "#120A04", iconBorder: "#2A1800", iconColor: "#FEA735",
    title: "Text to Image", route: "/workspace/generate",
    desc: "Describe what you want. FLUX.1-schnell generates a downloadable high-quality image.",
    tech: "FLUX · HuggingFace",
  },
];

const strip = [
  "Semantic chunking","Page-level citations","Persistent sessions",
  "Multi-document RAG","Gemini Vision","Conversation memory",
  "FLUX image gen","FastAPI + React",
];

export default function Landing() {
  const navigate = useNavigate();
  const capabilitiesRef = useRef(null);
  const scrollToCapabilities = () => capabilitiesRef.current?.scrollIntoView({ behavior: "smooth" });

  return (
    <div className="bg-base min-h-screen">
      <Navbar onFeaturesClick={scrollToCapabilities} />

      {/* Hero — tight top padding so it's visible without scrolling */}
      <section className="relative overflow-hidden text-center px-8 pt-12 pb-16 border-b border-border">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[500px] h-[280px] glow-orange pointer-events-none" />
        <div className="absolute top-8 left-1/2 -translate-x-1/2 w-[300px] h-[200px] glow-blue pointer-events-none" />
        <div className="relative">
          <div className="inline-flex items-center gap-2 bg-[#100D1A] border border-[#2A2040]
                          text-secondary px-4 py-1.5 rounded-full text-[11px] font-semibold mb-6">
            <span className="w-1.5 h-1.5 rounded-full bg-primary" />
            Gemini 2.5 Flash · FAISS · FLUX · FastAPI + React
          </div>
          <h1 className="text-5xl font-extrabold tracking-tight leading-tight mb-4">
            <span className="block text-linen">Intelligence, not</span>
            <span className="block text-gradient">just answers.</span>
            <span className="block text-dim text-4xl mt-1">Your documents. Your context.</span>
          </h1>
          <p className="text-sm text-muted leading-relaxed max-w-md mx-auto mb-8">
            The AI workspace that{" "}
            <strong className="text-secondary font-medium">cites its sources</strong>.
            Query documents, analyse images, generate visuals — with persistent chat history.
          </p>
          <div className="flex gap-3 justify-center mb-10">
            <button onClick={() => navigate("/workspace/chat")} className="btn-primary">
              Launch workspace →
            </button>
            <a href="https://github.com/siddhant-17-codes/VisionaryX-2.0"
               target="_blank" rel="noreferrer"
               className="btn-ghost flex items-center gap-2">
              <GithubIcon size={14} color="#00C3FF" />
              View on GitHub
            </a>
          </div>
          <div className="flex justify-center">
            <div className="flex border border-border rounded-xl bg-surface overflow-hidden">
              {[["RAG","Core engine"],["FAISS","Vector search"],["2.5","Gemini Flash"],["FLUX","Image gen"]].map(([num,lbl]) => (
                <div key={lbl} className="flex-1 px-6 py-3 text-center border-r border-border last:border-r-0">
                  <div className="text-base font-extrabold text-primary">{num}</div>
                  <div className="text-[9px] font-semibold text-hint uppercase tracking-widest mt-0.5">{lbl}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Strip */}
      <div className="bg-surface border-b border-border px-8 py-3 flex gap-8 overflow-hidden">
        {strip.map((item, i) => (
          <div key={item} className="flex items-center gap-2 text-[10px] text-hint font-semibold uppercase tracking-wider flex-shrink-0">
            <span className="w-1.5 h-1.5 rounded-full"
                  style={{ background: i%3===0?"#FE7235":i%3===1?"#00C3FF":"#FEA735" }} />
            {item}
          </div>
        ))}
      </div>

      {/* Features */}
      <section ref={capabilitiesRef} className="px-8 py-16">
        <div className="text-center mb-8">
          <div className="section-eyebrow mb-1">Capabilities</div>
          <h2 className="text-2xl font-extrabold text-linen tracking-tight">
            Four features. <span className="text-primary">One workspace.</span>
          </h2>
          <p className="text-xs text-hint mt-1">Production-grade architecture. Every feature is a full pipeline.</p>
        </div>
        <div className="grid grid-cols-2 gap-3 max-w-3xl mx-auto">
          {features.map(({ Icon, iconBg, iconBorder, iconColor, badge, badgeClass, title, desc, tech, route }) => (
            <div key={title}
                 onClick={() => navigate(route)}
                 className="bg-surface border border-border rounded-xl p-5 relative overflow-hidden
                            hover:border-primary transition-colors cursor-pointer group">
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center"
                     style={{ background: iconBg, border: `1px solid ${iconBorder}` }}>
                  <Icon size={20} color={iconColor} />
                </div>
                {badge && <span className={`${badgeClass} text-[9px]`}>{badge}</span>}
              </div>
              <h3 className="text-sm font-bold text-linen mb-1.5">{title}</h3>
              <p className="text-[11px] text-hint leading-relaxed mb-3">{desc}</p>
              <div className="flex justify-between items-center pt-3 border-t border-border">
                <span className="text-[10px] text-dim">{tech}</span>
                <span className="text-[11px] text-primary font-bold group-hover:translate-x-1 transition-transform">→</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border px-8 py-6 flex items-center justify-between bg-base">
        <div className="text-sm font-extrabold">Visionary<span className="text-primary">X</span></div>
        <div className="text-[10px] text-dim">
          Crafted with purpose by{" "}
          <span className="text-secondary font-semibold">Siddhant Thakur</span>
          {" "}· FastAPI · React · Gemini 2.5 · FAISS · FLUX
        </div>
        <a href="https://github.com/siddhant-17-codes/VisionaryX-2.0"
           target="_blank" rel="noreferrer"
           className="text-[10px] text-dim hover:text-linen transition-colors">GitHub</a>
      </footer>
    </div>
  );
}
