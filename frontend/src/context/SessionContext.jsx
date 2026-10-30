import { createContext, useContext, useState, useEffect, useCallback, useRef } from "react";
import { listSessions, createSession, deleteSession } from "../api/sessions";
import { isNotFound, notifyError } from "../utils/notify";

const SessionContext = createContext(null);

export function SessionProvider({ children }) {
  const [sessions, setSessions]           = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [loading, setLoading]             = useState(false);

  // Refresh runs every 30s; only the first failure in a row is shown.
  const refreshFailed = useRef(false);
  const refresh = useCallback(async () => {
    try {
      setSessions(await listSessions());
      refreshFailed.current = false;
    } catch (e) {
      if (!refreshFailed.current) notifyError(e, "Couldn't load your conversations.", "sessions-load");
      refreshFailed.current = true;
    }
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
    } catch (e) {
      notifyError(e, "Couldn't start a new conversation.", "session-create");
      return null;
    } finally {
      setLoading(false);
    }
  }, [refresh]);

  const removeSession = useCallback(async (id) => {
    try {
      await deleteSession(id);
    } catch (e) {
      if (!isNotFound(e)) {
        notifyError(e, "Couldn't delete that conversation.", "session-delete");
        return;
      }
    }
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
