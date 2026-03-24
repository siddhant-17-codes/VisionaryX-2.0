import { useState, useRef, useEffect } from "react";
import { SendIcon } from "../icons/Icons";

export default function ChatInput({ onSend, loading, placeholder = "Ask VisionaryX anything…" }) {
  const [value, setValue] = useState("");
  const textareaRef = useRef(null);

  // Auto-expand textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 160) + "px";
  }, [value]);

  const handleSubmit = () => {
    if (!value.trim() || loading) return;
    onSend(value.trim());
    setValue("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="px-4 py-3 border-t border-border flex-shrink-0">
      <div className="flex items-end gap-2 bg-base border border-border
                      rounded-xl px-4 py-2 focus-within:border-primary transition-colors">
        <textarea
          ref={textareaRef}
          className="flex-1 bg-transparent border-none text-linen text-sm outline-none
                     placeholder-dim font-sans resize-none leading-relaxed
                     min-h-[28px] max-h-[160px] overflow-y-auto py-1"
          placeholder={placeholder}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
          rows={1}
          style={{ scrollbarWidth: "thin" }}
        />
        <button
          onClick={handleSubmit}
          disabled={loading || !value.trim()}
          className="bg-primary text-linen border-none rounded-lg p-2 mb-0.5
                     hover:bg-orange-500 active:scale-95 transition-all duration-150
                     disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer flex-shrink-0"
        >
          <SendIcon size={14} color="#FCF5EF" />
        </button>
      </div>
      <p className="text-[9px] text-dim mt-1 px-1">Enter to send · Shift+Enter for new line</p>
    </div>
  );
}
