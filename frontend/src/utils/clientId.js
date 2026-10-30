const STORAGE_KEY = "vx_client_id";
const VALID = /^[A-Za-z0-9_-]{16,64}$/;

let memoryId = null;

// Anonymous owner key sent as X-Client-Id. The backend only shows a browser the
// sessions created with its id. Kept in memory too, so private windows that block
// localStorage still work for the life of the tab.
export function getClientId() {
  if (memoryId) return memoryId;
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored && VALID.test(stored)) return (memoryId = stored);
  } catch { /* storage blocked: fall through to a tab-scoped id */ }
  memoryId = crypto.randomUUID().replaceAll("-", "");
  try { localStorage.setItem(STORAGE_KEY, memoryId); } catch { /* tab-scoped only */ }
  return memoryId;
}

export function resetClientIdForTests() {
  memoryId = null;
}
