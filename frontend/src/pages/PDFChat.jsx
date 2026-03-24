import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { usePDF } from "../hooks/usePDF";
import PDFUploader from "../components/pdf/PDFUploader";
import SuggestedQuestions from "../components/pdf/SuggestedQuestions";
import ChatWindow from "../components/chat/ChatWindow";
import ChatInput from "../components/chat/ChatInput";
import toast from "react-hot-toast";

export default function PDFChat() {
  const location = useLocation();
  const restoreId = location.state?.sessionId || null;
  const {
    messages, suggested, loading, uploading, indexed,
    error, upload, query, reset, uploadedFiles, uploadedFileObjects, retry,
  } = usePDF(restoreId);

  useEffect(() => {
    if (error?.type === "network") toast.error("Backend connection lost");
  }, [error]);

  return (
    <div className="flex flex-col h-screen">
      <div className="px-5 py-4 border-b border-border flex items-center justify-between flex-shrink-0">
        <div>
          <h1 className="text-sm font-bold text-linen">PDF Chat</h1>
          <p className="text-[10px] text-hint mt-0.5">
            {indexed ? `${uploadedFiles.length} file(s) indexed · Ask anything` : "Upload PDF or DOCX to begin"}
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {indexed && uploadedFileObjects.map((f, i) => (
            <button key={i}
              onClick={() => window.open(URL.createObjectURL(f), "_blank")}
              className="text-[9px] text-cyan border border-[#0A2A30] bg-[#061418]
                         rounded px-2 py-0.5 cursor-pointer hover:bg-[#0a1e28] transition-colors">
              {f.name}
            </button>
          ))}
          {indexed && <span className="badge-blue">RAG active</span>}
          <span className="badge-orange">FAISS</span>
          {indexed && (
            <button onClick={reset}
                    className="text-[9px] text-hint hover:text-linen border border-border
                               rounded px-2 py-0.5 transition-colors cursor-pointer bg-transparent">
              New doc
            </button>
          )}
        </div>
      </div>

      {!indexed ? (
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="w-full max-w-lg">
            <PDFUploader onUpload={upload} loading={uploading} />
          </div>
        </div>
      ) : (
        <>
          {suggested.length > 0 && (
            <SuggestedQuestions questions={suggested} onSelect={query} />
          )}
          <ChatWindow messages={messages} loading={loading} error={error} onRetry={retry}
                      emptyText="Ask anything about your document…" />
          <ChatInput onSend={query} loading={loading} placeholder="Ask about your document…" />
        </>
      )}
    </div>
  );
}
