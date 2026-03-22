import { useEffect, useRef } from "react";
import ChatBubble from "./ChatBubble";
import TypingIndicator from "./TypingIndicator";

export default function ChatWindow({ messages, loading }) {
  const bottomRef = useRef(null);
  useEffect(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), [messages, loading]);

  return (
    <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
      {messages.length === 0 && (
        <p className="text-center text-gray-500 mt-20 text-sm">Start a conversation…</p>
      )}
      {messages.map((m, i) => <ChatBubble key={i} {...m} />)}
      {loading && <TypingIndicator />}
      <div ref={bottomRef} />
    </div>
  );
}
