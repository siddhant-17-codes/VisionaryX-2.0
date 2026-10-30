import { useEffect, useRef } from "react";
import ChatBubble from "./ChatBubble";
import TypingIndicator from "./TypingIndicator";
import ErrorCard from "./ErrorCard";

export default function ChatWindow({ messages, loading, error, onRetry, emptyText = "Start a conversation…" }) {
  const listRef = useRef(null);
  // Scroll only this list. scrollIntoView also scrolled every ancestor, which on
  // mobile pushed the menu bar off screen.
  useEffect(() => {
    const list = listRef.current;
    list?.scrollTo?.({ top: list.scrollHeight, behavior: "smooth" });
  }, [messages, loading, error]);

  return (
    <div ref={listRef} className="flex-1 min-h-0 overflow-y-auto px-5 py-5 flex flex-col gap-4">
      {messages.length === 0 && !error && (
        <p className="text-center text-hint text-sm mt-20">{emptyText}</p>
      )}
      {messages.map((m, i) => (
        <ChatBubble key={i} role={m.role} content={m.content} citations={m.citations} />
      ))}
      {loading && <TypingIndicator />}
      {error && !loading && <ErrorCard error={error} onRetry={onRetry} />}
    </div>
  );
}
