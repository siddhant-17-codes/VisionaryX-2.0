import { useRef } from "react";
import { UploadIcon } from "../icons/Icons";

export default function PDFUploader({ onUpload, loading }) {
  const ref = useRef();
  const handleChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length) onUpload(files);
  };
  const handleDrop = (e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    if (files.length) onUpload(files);
  };

  return (
    <div
      onClick={() => ref.current.click()}
      onDragOver={(e) => e.preventDefault()}
      onDrop={handleDrop}
      className="border-2 border-dashed border-border rounded-xl p-10 text-center
                 cursor-pointer hover:border-primary transition-colors duration-200
                 flex flex-col items-center gap-3"
    >
      <input ref={ref} type="file" accept=".pdf,.docx,.doc" multiple onChange={handleChange} className="hidden" />
      <UploadIcon size={28} color="#3D3050" />
      <div>
        <p className="text-sm font-medium text-muted">
          {loading ? "Processing…" : "Click or drag to upload"}
        </p>
        <p className="text-xs text-hint mt-1">PDF and DOCX supported · Multiple files allowed</p>
      </div>
    </div>
  );
}
