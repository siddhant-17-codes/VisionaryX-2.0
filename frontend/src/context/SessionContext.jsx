import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { listSessions, createSession, deleteSession } from "../api/sessions";

const SessionContext = createContext(null);

export function SessionProvider({ children }) {
  const [sessions, setSessions]           = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [loading, setLoading]             = useState(false);

  const refresh = useCallback(async () => {
    try { const data = await listSessions(); setSessions(data); } catch {}
  }, []);

  // Refresh on mount and every 30s
  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 30000);
    return () => clearInterval(interval);
  }, [refresh]);

  const newSession = useCallback(async (mode = "chat") => {
    setLoading(true);
    try {
      const session = await createSession(mode);
      setActiveSessionId(session.id);
      await refresh();
      return session;
    } finally {
      setLoading(false);
    }
  }, [refresh]);

  const removeSession = useCallback(async (id) => {
    await deleteSession(id);
    if (activeSessionId === id) setActiveSessionId(null);
    await refresh();
  }, [activeSessionId, refresh]);

  return (
    <SessionContext.Provider value={{
      sessions, activeSessionId, setActiveSessionId,
      newSession, removeSession, refresh, loading,
    }}>
      {children}
    </SessionContext.Provider>
  );
}

export const useSessionContext = () => {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error("useSessionContext must be inside SessionProvider");
  return ctx;
};
