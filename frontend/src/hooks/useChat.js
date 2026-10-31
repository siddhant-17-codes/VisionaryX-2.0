import { useState, useEffect, useRef, useCallback } from "react";
import { sendMessage } from "../api/chat";
import { createSession, getSession } from "../api/sessions";
import { reveal } from "../utils/reveal";
import { isNotFound, notifyError } from "../utils/notify";

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
      if (!existingId) return;  // a new session is created with the first message
      try {
        const session = await getSession(existingId);
        sessionIdRef.current = session.id;
        setMessages(session.messages || []);
        setTitle(session.title !== "New chat" ? session.title : "General Chat");
        localStorage.setItem(STORAGE_KEY, session.id);
      } catch (e) {
        localStorage.removeItem(STORAGE_KEY);
        if (!isNotFound(e)) notifyError(e, "Couldn't load your last conversation.", "session-restore");
      }
    };
    init();
  }, [restoreSessionId]);

  // Created with the first message, not on page load, so opening the page never
  // leaves an empty "New chat" in the history (F5).
  const ensureSession = useCallback(async () => {
    if (sessionIdRef.current) return sessionIdRef.current;
    try {
      const s = await createSession("chat");
      sessionIdRef.current = s.id;
      localStorage.setItem(STORAGE_KEY, s.id);
    } catch (e) { notifyError(e, "Couldn't start a new conversation, so this one won't be saved.", "session-create"); }
    return sessionIdRef.current;
  }, []);

  const doSend = useCallback(async (text, currentMessages) => {
    const userMsg = { role: "user", content: text };
    const updated = [...currentMessages, userMsg];
    setMessages(updated);
    setLoading(true);
    setError(null);
    try {
      const history = updated.slice(0, -1);
      const { reply, model } = await sendMessage(text, history, await ensureSession());
      await reveal(reply, (shown) => setMessages([...updated, { role: "assistant", content: shown, model }]));
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  }, [ensureSession]);

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
    sessionIdRef.current = null;  // the next message starts a new session
  };

  return { messages, loading, error, send, clear, retry, sessionTitle };
}
