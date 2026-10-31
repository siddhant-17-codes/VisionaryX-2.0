import { useState } from "react";
import { queryImage, generateImage } from "../api/image";
import { reveal } from "../utils/reveal";

// Image Query and Text to Image keep nothing on the server, so they create no
// session: visiting them used to leave an empty "New chat" in the history (F5).

export function useImageQuery() {
  const [answer, setAnswer]   = useState("");
  const [model, setModel]     = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const analyse = async (file, prompt) => {
    setLoading(true); setError(null); setModel(null);
    try {
      const result = await queryImage(file, prompt);
      await reveal(result.answer, setAnswer);
      setModel(result.model || null);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  return { answer, model, loading, error, analyse, reset: () => { setAnswer(""); setModel(null); } };
}

export function useImageGenerate() {
  const [imageB64, setImageB64] = useState(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);

  const generate = async (prompt) => {
    setLoading(true); setError(null);
    try {
      setImageB64(await generateImage(prompt));
    } catch (e) { setError(e); }
    finally { setLoading(false); }
  };

  return { imageB64, loading, error, generate, reset: () => setImageB64(null) };
}
