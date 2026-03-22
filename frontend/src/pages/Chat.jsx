import { useState } from "react";
import ChatWindow from "../components/chat/ChatWindow";
import ChatInput from "../components/chat/ChatInput";
import { sendMessage } from "../api/chat";
import toast from "react-hot-toast";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async (text) => {
    const updated = [...messages, { role: "user", content: text }];
    setMessages(updated);
    setLoading(true);
    try {
      const reply = await sendMessage(text, updated.slice(0, -1));
      setMessages([...updated, { role: "assistant", content: reply }]);
    } catch (e) {
      toast.error(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <div className="px-6 py-4 border-b border-surface-600">
        <h1 className="font-medium">General Chat</h1>
        <p className="text-xs text-gray-400 mt-0.5">Conversation history is preserved across turns</p>
      </div>
      <ChatWindow messages={messages} loading={loading} />
      <ChatInput onSend={handleSend} loading={loading} />
    </div>
  );
}
