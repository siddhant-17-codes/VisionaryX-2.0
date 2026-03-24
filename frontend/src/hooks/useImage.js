import { useState, useEffect } from "react";
import { queryImage, generateImage } from "../api/image";
import { createSession, getSession } from "../api/sessions";

const QUERY_KEY = "vx_image_query_session";
const GEN_KEY   = "vx_image_gen_session";

export function useImageQuery() {
  const [answer, setAnswer]   = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    const existing = localStorage.getItem(QUERY_KEY);
    if (existing) {
      getSession(existing)
        .then((s) => { setSessionId(s.id); setHistory(s.messages || []); })
        .catch(() => init());
    } else { init(); }
    async function init() {
      try { const s = await createSession("image"); setSessionId(s.id); localStorage.setItem(QUERY_KEY, s.id); } catch {}
    }
  }, []);

  const analyse = async (file, prompt) => {
    setLoading(true); setError(null);
    try {
      const result = await queryImage(file, prompt);
      // Stream result
      let streamed = "";
      const words = result.split(" ");
      for (let i = 0; i < words.length; i++) {
        streamed += (i === 0 ? "" : " ") + words[i];
        setAnswer(streamed);
        await new Promise((r) => setTimeout(r, 16));
      }
      setHistory((h) => [...h, { role: "user", content: prompt || "Analyse image" }, { role: "assistant", content: result }]);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  return { answer, history, loading, error, analyse, reset: () => { setAnswer(""); } };
}

export function useImageGenerate() {
  const [imageB64, setImageB64] = useState(null);
  const [history, setHistory]   = useState([]);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    const existing = localStorage.getItem(GEN_KEY);
    if (existing) {
      getSession(existing)
        .then((s) => { setSessionId(s.id); setHistory(s.messages || []); })
        .catch(() => init());
    } else { init(); }
    async function init() {
      try { const s = await createSession("generate"); setSessionId(s.id); localStorage.setItem(GEN_KEY, s.id); } catch {}
    }
  }, []);

  const generate = async (prompt) => {
    setLoading(true); setError(null);
    try {
      const b64 = await generateImage(prompt);
      setImageB64(b64);
      setHistory((h) => [...h, { prompt, hasImage: true }]);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  return { imageB64, history, loading, error, generate, reset: () => setImageB64(null) };
}
