import { useState, useEffect, useRef, useCallback } from "react";
import { sendMessage } from "../api/chat";
import { createSession, getSession } from "../api/sessions";

const STORAGE_KEY = "vx_active_chat_session";

export function useChat(restoreSessionId = null) {
  const [messages, setMessages]     = useState([]);
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState(null);
  const [sessionTitle, setTitle]    = useState("General Chat");
  const sessionIdRef = useRef(null);
  const lastInputRef = useRef("");

  useEffect(() => {
    const init = async () => {
      const existingId = restoreSessionId || localStorage.getItem(STORAGE_KEY);
      if (existingId) {
        try {
          const session = await getSession(existingId);
          sessionIdRef.current = session.id;
          setMessages(session.messages || []);
          setTitle(session.title !== "New chat" ? session.title : "General Chat");
          localStorage.setItem(STORAGE_KEY, session.id);
          return;
        } catch {}
      }
      try {
        const s = await createSession("chat");
        sessionIdRef.current = s.id;
        localStorage.setItem(STORAGE_KEY, s.id);
      } catch {}
    };
    init();
  }, [restoreSessionId]);

  const doSend = useCallback(async (text, currentMessages) => {
    const userMsg = { role: "user", content: text };
    const updated = [...currentMessages, userMsg];
    setMessages(updated);
    setLoading(true);
    setError(null);
    try {
      const history = updated.slice(0, -1);
      const reply = await sendMessage(text, history, sessionIdRef.current);
      let streamed = "";
      const words = reply.split(" ");
      for (let i = 0; i < words.length; i++) {
        streamed += (i === 0 ? "" : " ") + words[i];
        setMessages([...updated, { role: "assistant", content: streamed }]);
        await new Promise((r) => setTimeout(r, 18));
      }
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  }, []);

  const send = useCallback(async (text) => {
    if (!text.trim() || loading) return;
    lastInputRef.current = text;
    await doSend(text, messages);
  }, [loading, messages, doSend]);

  const retry = useCallback(async () => {
    if (!lastInputRef.current) return;
    const withoutLast = messages.filter((_, i) => i !== messages.length - 1);
    await doSend(lastInputRef.current, withoutLast);
  }, [messages, doSend]);

  const clear = async () => {
    setMessages([]); setError(null);
    localStorage.removeItem(STORAGE_KEY);
    try {
      const s = await createSession("chat");
      sessionIdRef.current = s.id;
      localStorage.setItem(STORAGE_KEY, s.id);
    } catch {}
  };

  return { messages, loading, error, send, clear, retry, sessionTitle };
}
