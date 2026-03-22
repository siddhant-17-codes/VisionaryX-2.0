import ReactMarkdown from "react-markdown";

export default function ChatBubble({ role, content }) {
  const isUser = role === "user";
  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm flex-shrink-0 ${
        isUser ? "bg-brand-600" : "bg-surface-600"
      }`}>
        {isUser ? "U" : "V"}
      </div>
      <div className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
        isUser
          ? "bg-brand-600 text-white rounded-tr-sm"
          : "bg-surface-700 text-gray-100 rounded-tl-sm"
      }`}>
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
    </div>
  );
}
