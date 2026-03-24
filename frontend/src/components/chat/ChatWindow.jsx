import { useEffect, useRef } from "react";
import ChatBubble from "./ChatBubble";
import TypingIndicator from "./TypingIndicator";
import ErrorCard from "./ErrorCard";

export default function ChatWindow({ messages, loading, error, onRetry, emptyText = "Start a conversation…" }) {
  const bottomRef = useRef(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, error]);

  return (
    <div className="flex-1 overflow-y-auto px-5 py-5 flex flex-col gap-4">
      {messages.length === 0 && !error && (
        <p className="text-center text-hint text-sm mt-20">{emptyText}</p>
      )}
      {messages.map((m, i) => (
        <ChatBubble key={i} role={m.role} content={m.content} citations={m.citations} />
      ))}
      {loading && <TypingIndicator />}
      {error && !loading && <ErrorCard error={error} onRetry={onRetry} />}
      <div ref={bottomRef} />
    </div>
  );
}
