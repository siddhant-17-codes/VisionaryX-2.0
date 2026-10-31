import { useRef } from "react";
import { UploadIcon } from "../icons/Icons";

export default function PDFUploader({ onUpload, loading }) {
  const ref = useRef();
  const open = () => { if (!loading) ref.current.click(); };
  const handleChange = (e) => {
    const files = Array.from(e.target.files);
    e.target.value = "";  // so choosing the same file again still triggers a change
    if (files.length) onUpload(files);
  };
  const handleDrop = (e) => {
    e.preventDefault();
    if (loading) return;
    const files = Array.from(e.dataTransfer.files);
    if (files.length) onUpload(files);
  };

  return (
    <div
      role="button"
      tabIndex={loading ? -1 : 0}
      aria-label="Upload PDF or DOCX files"
      aria-busy={loading}
      aria-disabled={loading}
      onClick={open}
      onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); } }}
      onDragOver={(e) => e.preventDefault()}
      onDrop={handleDrop}
      className={`border-2 border-dashed rounded-xl p-10 text-center transition-colors duration-200
                  flex flex-col items-center gap-3
                  ${loading ? "border-primary cursor-wait" : "border-border cursor-pointer hover:border-primary focus-visible:border-primary"}`}
    >
      <input ref={ref} type="file" accept=".pdf,.docx" multiple onChange={handleChange} className="hidden" />
      {loading
        ? <span className="w-7 h-7 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        : <UploadIcon size={28} color="#947FB2" />}
      <div>
        <p className="text-sm font-medium text-muted">
          {loading ? "Reading and indexing your documents…" : "Click or drag to upload"}
        </p>
        <p className="text-xs text-hint mt-1">
          {loading ? "Large files can take up to a minute." : "PDF and DOCX supported · Multiple files allowed"}
        </p>
      </div>
    </div>
  );
}
