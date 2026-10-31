import { useState, useEffect } from "react";
import { getImageStatus } from "../api/image";
import { useImageGenerate } from "../hooks/useImage";
import { SparkleIcon, DownloadIcon } from "../components/icons/Icons";
import toast from "react-hot-toast";

export default function TextToImage() {
  const [prompt, setPrompt] = useState("");
  const { imageB64, loading, error, generate } = useImageGenerate();
  const [pausedUntil, setPausedUntil] = useState(null);

  // Say "paused" before anyone types. If this check fails, the generate call
  // itself reports the problem, so it stays quiet here.
  useEffect(() => {
    getImageStatus()
      .then((s) => { if (!s.available && s.resumes_at) setPausedUntil(new Date(s.resumes_at)); })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!error) return;
    if (error.type === "ImageQuotaExceededError") {
      setPausedUntil(new Date(Date.now() + (error.retryAfter || 3600) * 1000));
    } else {
      toast.error(error.message);
    }
  }, [error]);

  const paused = pausedUntil && pausedUntil > new Date();

  return (
    <div className="max-w-2xl mx-auto px-6 py-10">
      <div className="mb-6">
        <h1 className="text-sm font-bold text-linen">Text to Image</h1>
        <p className="text-[10px] text-hint mt-0.5">Describe your visual · FLUX generates · Download ready</p>
      </div>
      <div className="bg-base border border-border rounded-xl overflow-hidden mb-4 min-h-[220px] flex items-center justify-center">
        {imageB64 ? (
          <img src={`data:image/png;base64,${imageB64}`} alt="generated" className="w-full object-contain" />
        ) : (
          <div className="text-center py-12">
            <div className="flex justify-center mb-3 opacity-20">
              <SparkleIcon size={32} color="#FEA735" />
            </div>
            <p className="text-xs text-hint">Generated image appears here</p>
          </div>
        )}
      </div>
      {paused && (
        <div role="status" className="mb-3 rounded-xl border px-4 py-3"
             style={{ background: "#1A0A04", borderColor: "#3A1808" }}>
          <p className="text-sm font-semibold" style={{ color: "#FEA735" }}>Image generation is paused</p>
          <p className="text-xs text-muted leading-relaxed">
            The free image quota is used up for now. It should be back around{" "}
            {pausedUntil.toLocaleString([], { weekday: "short", hour: "2-digit", minute: "2-digit" })}.
          </p>
        </div>
      )}
      <textarea
        className="textarea-field mb-3"
        rows={3}
        placeholder="A futuristic city at night with neon lights reflecting on rain-soaked streets…"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />
      <button
        onClick={() => prompt.trim() && generate(prompt)}
        disabled={loading || paused || !prompt.trim()}
        className="btn-primary w-full mb-3"
      >
        {loading ? "Generating… (usually a few seconds)" : paused ? "Paused" : "Generate Image"}
      </button>
      {imageB64 && (
        <a
          href={`data:image/png;base64,${imageB64}`}
          download="visionaryx_generated.png"
          className="flex items-center justify-center gap-2 w-full py-2.5 text-sm
                     text-cyan border border-[#0A2A30] rounded-lg hover:bg-[#061418] transition-colors"
        >
          <DownloadIcon size={14} color="#00C3FF" />
          Download Image
        </a>
      )}
    </div>
  );
}
