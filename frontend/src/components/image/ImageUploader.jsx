import { useRef } from "react";
import { ImageIcon } from "../icons/Icons";

export default function ImageUploader({ onSelect, preview }) {
  const ref = useRef();
  return (
    <div
      onClick={() => ref.current.click()}
      className="border-2 border-dashed border-border rounded-xl cursor-pointer
                 hover:border-primary transition-colors duration-200 overflow-hidden"
    >
      <input
        ref={ref}
        type="file"
        accept="image/*"
        onChange={(e) => e.target.files[0] && onSelect(e.target.files[0])}
        className="hidden"
      />
      {preview ? (
        <img src={preview} alt="preview" className="w-full max-h-64 object-contain p-2" />
      ) : (
        <div className="p-8 flex flex-col items-center gap-3">
          <ImageIcon size={28} color="#3D3050" />
          <p className="text-sm text-muted">Click to upload an image</p>
          <p className="text-xs text-hint">JPG, PNG supported</p>
        </div>
      )}
    </div>
  );
}
