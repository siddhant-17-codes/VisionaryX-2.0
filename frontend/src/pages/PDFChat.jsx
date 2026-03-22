import { useState } from "react";
import PDFUploader from "../components/pdf/PDFUploader";
import SuggestedQuestions from "../components/pdf/SuggestedQuestions";
import CitationCard from "../components/pdf/CitationCard";
import ChatWindow from "../components/chat/ChatWindow";
import ChatInput from "../components/chat/ChatInput";
import { uploadPDFs, queryPDF } from "../api/pdf";
import toast from "react-hot-toast";

export default function PDFChat() {
  const [sessionId, setSessionId] = useState(null);
  const [suggested, setSuggested] = useState([]);
  const [messages, setMessages] = useState([]);
  const [citations, setCitations] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (files) => {
    setUploading(true);
    try {
      const data = await uploadPDFs(files);
      setSessionId(data.session_id);
      setSuggested(data.questions || []);
      setMessages([]);
      toast.success("PDFs processed!");
    } catch (e) {
      toast.error(e.message);
    } finally {
      setUploading(false);
    }
  };

  const handleQuery = async (question) => {
    if (!sessionId) return toast.error("Please upload PDFs first.");
    const updated = [...messages, { role: "user", content: question }];
    setMessages(updated);
    setSuggested([]);
    setLoading(true);
    try {
      const data = await queryPDF(sessionId, question, updated.slice(0, -1));
      setMessages([...updated, { role: "assistant", content: data.answer }]);
      setCitations(data.citations || []);
    } catch (e) {
      toast.error(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen">
      <div className="flex flex-col flex-1">
        <div className="px-6 py-4 border-b border-surface-600">
          <h1 className="font-medium">PDF Chat</h1>
          <p className="text-xs text-gray-400 mt-0.5">Upload documents and ask questions with cited answers</p>
        </div>
        {!sessionId
          ? <div className="p-6"><PDFUploader onUpload={handleUpload} loading={uploading} /></div>
          : <>
              <SuggestedQuestions questions={suggested} onSelect={handleQuery} />
              <ChatWindow messages={messages} loading={loading} />
              <ChatInput onSend={handleQuery} loading={loading} />
            </>
        }
      </div>
      {citations.length > 0 && (
        <aside className="w-72 border-l border-surface-600 overflow-y-auto p-4 space-y-3">
          <p className="text-xs text-gray-400 font-medium uppercase tracking-wide">Sources</p>
          {citations.map((c, i) => <CitationCard key={i} citation={c} index={i} />)}
        </aside>
      )}
    </div>
  );
}
