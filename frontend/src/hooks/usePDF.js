import { useState, useRef, useEffect, useCallback } from "react";
import { uploadPDFs, queryPDF } from "../api/pdf";
import { createSession, getSession } from "../api/sessions";

const STORAGE_KEY = "vx_active_pdf_session";

export function usePDF(restoreSessionId = null) {
  const [messages, setMessages]         = useState([]);
  const [suggested, setSuggested]       = useState([]);
  const [loading, setLoading]           = useState(false);
  const [uploading, setUploading]       = useState(false);
  const [indexed, setIndexed]           = useState(false);
  const [error, setError]               = useState(null);
  const [uploadedFiles, setUploadedFiles]           = useState([]);
  const [uploadedFileObjects, setUploadedFileObjects] = useState([]);
  const faissSessionRef = useRef(null);
  const chatSessionRef  = useRef(null);
  const lastQuestionRef = useRef("");

  useEffect(() => {
    const init = async () => {
      const existingId = restoreSessionId || localStorage.getItem(STORAGE_KEY);
      if (!existingId) return;
      try {
        const session = await getSession(existingId);
        chatSessionRef.current  = session.id;
        faissSessionRef.current = session.session_id;
        setMessages(session.messages || []);
        setUploadedFiles(session.documents || []);
        if (session.session_id) { setIndexed(true); localStorage.setItem(STORAGE_KEY, session.id); }
      } catch {}
    };
    init();
  }, [restoreSessionId]);

  const upload = async (files) => {
    setUploading(true); setError(null);
    try {
      let chatId = chatSessionRef.current;
      if (!chatId) {
        const s = await createSession("pdf");
        chatId = s.id;
        chatSessionRef.current = chatId;
      }
      const data = await uploadPDFs(files, chatId);
      faissSessionRef.current = data.session_id;
      setSuggested(data.questions || []);
      setIndexed(true);
      setMessages([]);
      setUploadedFiles(files.map((f) => f.name));
      setUploadedFileObjects(files);
      localStorage.setItem(STORAGE_KEY, chatId);
    } catch (e) { setError(e); }
    finally { setUploading(false); }
  };

  const doQuery = useCallback(async (question, currentMessages) => {
    if (!faissSessionRef.current) return;
    const userMsg = { role: "user", content: question };
    const updated = [...currentMessages, userMsg];
    setMessages(updated);
    setLoading(true); setError(null);
    try {
      const history = updated.slice(0, -1);
      const data = await queryPDF(faissSessionRef.current, question, history, chatSessionRef.current);
      let streamed = "";
      const words = data.answer.split(" ");
      for (let i = 0; i < words.length; i++) {
        streamed += (i === 0 ? "" : " ") + words[i];
        setMessages([...updated, { role: "assistant", content: streamed, citations: data.citations || [] }]);
        await new Promise((r) => setTimeout(r, 18));
      }
    } catch (e) { setError(e); }
    finally { setLoading(false); }
  }, []);

  const query = useCallback(async (question) => {
    if (loading) return;
    lastQuestionRef.current = question;
    await doQuery(question, messages);
  }, [loading, messages, doQuery]);

  const retry = useCallback(async () => {
    if (!lastQuestionRef.current) return;
    const withoutLast = messages.filter((_, i) => i !== messages.length - 1);
    await doQuery(lastQuestionRef.current, withoutLast);
  }, [messages, doQuery]);

  const reset = async () => {
    setMessages([]); setSuggested([]); setIndexed(false);
    setUploadedFiles([]); setUploadedFileObjects([]); setError(null);
    faissSessionRef.current = null; chatSessionRef.current = null;
    localStorage.removeItem(STORAGE_KEY);
  };

  return { messages, suggested, loading, uploading, indexed, error, upload, query, reset, retry, uploadedFiles, uploadedFileObjects };
}
