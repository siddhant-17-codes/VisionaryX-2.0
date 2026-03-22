import { useState } from "react";

export default function ChatInput({ onSend, loading }) {
  const [value, setValue] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!value.trim() || loading) return;
    onSend(value.trim());
    setValue("");
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-3 p-4 border-t border-surface-600 bg-surface-800">
      <input
        className="input-field flex-1"
        placeholder="Ask anything…"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        disabled={loading}
      />
      <button type="submit" className="btn-primary px-5" disabled={loading || !value.trim()}>
        Send
      </button>
    </form>
  );
}
