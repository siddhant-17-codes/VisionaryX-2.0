import { useState } from "react";
import ImageUploader from "../components/image/ImageUploader";
import ImageResult from "../components/image/ImageResult";
import { queryImage } from "../api/image";
import toast from "react-hot-toast";

export default function ImageQuery() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSelect = (f) => {
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setAnswer("");
  };

  const handleSubmit = async () => {
    if (!file) return toast.error("Please upload an image first.");
    setLoading(true);
    try {
      const result = await queryImage(file, prompt);
      setAnswer(result);
    } catch (e) {
      toast.error(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-10">
      <h1 className="font-medium mb-1">Image Query</h1>
      <p className="text-xs text-gray-400 mb-6">Upload an image and ask Gemini Vision anything about it</p>
      <ImageUploader onSelect={handleSelect} preview={preview} />
      <input
        className="input-field mt-4"
        placeholder="Optional: ask a specific question about the image"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />
      <button onClick={handleSubmit} disabled={loading || !file} className="btn-primary mt-3 w-full">
        {loading ? "Analysing…" : "Analyse Image"}
      </button>
      <ImageResult answer={answer} />
    </div>
  );
}
