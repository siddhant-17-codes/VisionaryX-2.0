import { useState, useEffect } from "react";
import { useImageQuery } from "../hooks/useImage";
import ImageUploader from "../components/image/ImageUploader";
import ImageResult from "../components/image/ImageResult";
import toast from "react-hot-toast";

export default function ImageQuery() {
  const [file, setFile]     = useState(null);
  const [preview, setPreview] = useState(null);
  const [prompt, setPrompt] = useState("");
  const { answer, loading, error, analyse } = useImageQuery();

  useEffect(() => { if (error) toast.error(error); }, [error]);

  const handleSelect = (f) => {
    setFile(f);
    setPreview(URL.createObjectURL(f));
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-10">
      <div className="mb-6">
        <h1 className="text-sm font-bold text-linen">Image Query</h1>
        <p className="text-[10px] text-hint mt-0.5">Upload an image · Ask anything · Gemini Vision responds</p>
      </div>
      <ImageUploader onSelect={handleSelect} preview={preview} />
      <input
        className="input-field mt-4"
        placeholder="Ask a specific question about the image (optional)"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />
      <button
        onClick={() => file && analyse(file, prompt)}
        disabled={loading || !file}
        className="btn-primary w-full mt-3"
      >
        {loading ? "Analysing…" : "Analyse Image"}
      </button>
      <ImageResult answer={answer} />
    </div>
  );
}
