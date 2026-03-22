import { useRef } from "react";

export default function ImageUploader({ onSelect, preview }) {
  const ref = useRef();
  return (
    <div>
      <div
        onClick={() => ref.current.click()}
        className="border-2 border-dashed border-surface-600 hover:border-brand-400 rounded-xl p-8 text-center cursor-pointer transition-colors"
      >
        <input ref={ref} type="file" accept="image/*" onChange={(e) => onSelect(e.target.files[0])} className="hidden" />
        {preview
          ? <img src={preview} alt="preview" className="max-h-48 mx-auto rounded-lg object-contain" />
          : <p className="text-gray-400 text-sm">Click to upload an image</p>
        }
      </div>
    </div>
  );
}
