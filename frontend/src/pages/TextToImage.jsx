import { useState } from "react";
import { generateImage } from "../api/image";
import toast from "react-hot-toast";

export default function TextToImage() {
  const [prompt, setPrompt] = useState("");
  const [imageB64, setImageB64] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (!prompt.trim()) return toast.error("Please enter a prompt.");
    setLoading(true);
    try {
      const b64 = await generateImage(prompt);
      setImageB64(b64);
    } catch (e) {
      toast.error(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-10">
      <h1 className="font-medium mb-1">Text to Image</h1>
      <p className="text-xs text-gray-400 mb-6">Describe what you want and let AI paint it</p>
      <textarea
        className="input-field resize-none"
        rows={3}
        placeholder="e.g. A futuristic city at sunset with neon lights reflecting on rain-soaked streets"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />
      <button onClick={handleGenerate} disabled={loading || !prompt.trim()} className="btn-primary mt-3 w-full">
        {loading ? "Generating…" : "Generate Image"}
      </button>
      {imageB64 && (
        <div className="mt-6">
          <img src={`data:image/png;base64,${imageB64}`} alt="generated" className="rounded-xl w-full" />
          <a
            href={`data:image/png;base64,${imageB64}`}
            download="visionaryx_generated.png"
            className="btn-ghost block text-center mt-3 text-sm"
          >
            Download Image
          </a>
        </div>
      )}
    </div>
  );
}
