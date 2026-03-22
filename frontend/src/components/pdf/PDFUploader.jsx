import { useRef } from "react";

export default function PDFUploader({ onUpload, loading }) {
  const ref = useRef();
  const handleChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length) onUpload(files);
  };
  return (
    <div
      onClick={() => ref.current.click()}
      className="border-2 border-dashed border-surface-600 hover:border-brand-400 rounded-xl p-8 text-center cursor-pointer transition-colors"
    >
      <input ref={ref} type="file" accept=".pdf" multiple onChange={handleChange} className="hidden" />
      <p className="text-gray-400 text-sm">{loading ? "Processing…" : "Click to upload PDF(s)"}</p>
      <p className="text-gray-500 text-xs mt-1">Multiple files supported</p>
    </div>
  );
}
