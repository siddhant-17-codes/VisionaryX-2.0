import { useRef } from "react";
import { ImageIcon } from "../icons/Icons";

export default function ImageUploader({ onSelect, preview }) {
  const ref = useRef();
  const open = () => ref.current.click();
  return (
    <div
      role="button"
      tabIndex={0}
      aria-label={preview ? "Choose a different image" : "Upload an image"}
      onClick={open}
      onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); } }}
      className="border-2 border-dashed border-border rounded-xl cursor-pointer
                 hover:border-primary focus-visible:border-primary transition-colors duration-200 overflow-hidden"
    >
      <input
        ref={ref}
        type="file"
        accept="image/*"
        onChange={(e) => {
          const file = e.target.files[0];
          e.target.value = "";  // so choosing the same file again still triggers a change
          if (file) onSelect(file);
        }}
        className="hidden"
      />
      {preview ? (
        <img src={preview} alt="The image you chose" className="w-full max-h-64 object-contain p-2" />
      ) : (
        <div className="p-8 flex flex-col items-center gap-3">
          <ImageIcon size={28} color="#947FB2" />
          <p className="text-sm text-muted">Click to upload an image</p>
          <p className="text-xs text-hint">JPG, PNG, WebP or GIF</p>
        </div>
      )}
    </div>
  );
}
