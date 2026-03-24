import { useLocation } from "react-router-dom";
import { useChat } from "../hooks/useChat";
import ChatWindow from "../components/chat/ChatWindow";
import ChatInput from "../components/chat/ChatInput";

export default function Chat() {
  const location = useLocation();
  const restoreId = location.state?.sessionId || null;
  const { messages, loading, error, send, clear, sessionTitle, lastInput, retry } = useChat(restoreId);

  return (
    <div className="flex flex-col h-screen">
      <div className="px-5 py-4 border-b border-border flex items-center justify-between flex-shrink-0">
        <div>
          <h1 className="text-sm font-bold text-linen">{sessionTitle}</h1>
          <p className="text-[10px] text-hint mt-0.5">Memory enabled · session auto-saved</p>
        </div>
        <div className="flex gap-2">
          <span className="badge-blue">Live</span>
          <span className="badge-orange">Gemini 2.5</span>
        </div>
      </div>
      <ChatWindow messages={messages} loading={loading} error={error} onRetry={retry} />
      <ChatInput onSend={send} loading={loading} />
    </div>
  );
}
