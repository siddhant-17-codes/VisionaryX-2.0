import { useSyncExternalStore } from "react";
import client from "./client";

// Render's free tier puts the backend to sleep when idle; the first request after
// that waits while it starts. This pings /health once per page load so visitors see
// why the first answer is slow, and so the server starts waking before they type.
//   "unknown" → "waking" (no answer within WAKE_NOTICE_MS) → "ready" or "offline"
export const WAKE_NOTICE_MS = 3000;
const WAKE_TIMEOUT_MS = 90000;

let status = "unknown";
let pending = null;
const listeners = new Set();

function setStatus(next) {
  status = next;
  listeners.forEach((listener) => listener());
}

export function wakeServer() {
  if (status === "ready") return Promise.resolve();
  if (pending) return pending;
  const notice = setTimeout(() => setStatus("waking"), WAKE_NOTICE_MS);
  pending = client.get("/health", { timeout: WAKE_TIMEOUT_MS })
    .then(() => setStatus("ready"))
    .catch(() => setStatus("offline"))
    .finally(() => { clearTimeout(notice); pending = null; });
  return pending;
}

function subscribe(listener) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function useServerStatus() {
  return useSyncExternalStore(subscribe, () => status);
}

// Tests only: forget the result of the last check.
export function resetServerStatus() {
  status = "unknown";
  pending = null;
}
