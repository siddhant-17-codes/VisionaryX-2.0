// Classifies on the HTTP status and the backend's error `type` (see ApiError in
// api/client.js), never on message text. Every string here is written for visitors.

const WAKE_NOTE = "The free server sleeps when idle and can take up to a minute to wake up.";

export function parseApiError(error) {
  const status = error?.status;
  const type = error?.type;
  const msg = error?.message || "";

  if (type === "NetworkError") {
    return {
      type: "network",
      title: "Can't reach the server",
      message: `${WAKE_NOTE} It may also be a problem with your connection.`,
      guidance: "Wait a moment, then try again.",
      retryable: true,
    };
  }
  if (type === "Timeout" || status === 504) {
    return {
      type: "timeout",
      title: "That took too long",
      message: status === 504 ? msg : `No answer in time. ${WAKE_NOTE}`,
      guidance: "Try again; the next attempt is usually much faster.",
      retryable: true,
    };
  }
  if (status === 429 && type === "LLMQuotaError") {
    return {
      type: "quota",
      title: "Daily AI limit reached",
      message: msg,
      guidance: "Your conversation is saved. Come back after the reset.",
      retryable: false,
    };
  }
  if (status === 429) {
    const wait = error.retryAfter ? `${error.retryAfter} seconds` : "a few seconds";
    return {
      type: "ratelimit",
      title: "Too many requests",
      message: msg,
      guidance: `Wait ${wait}, then try again.`,
      retryable: true,
    };
  }
  if (status === 502 || status === 503) {
    return {
      type: "unavailable",
      title: "AI service unavailable",
      message: msg,
      guidance: "This is usually temporary. Try again in a minute.",
      retryable: true,
    };
  }
  if (status >= 500) {
    return {
      type: "server",
      title: "Something went wrong on our side",
      message: "It wasn't anything you did, and there's nothing to change on your end.",
      guidance: "Try again. If it keeps happening, start a new chat.",
      retryable: true,
    };
  }
  if (status >= 400) {
    return {
      type: "request",
      title: status === 413 ? "File too large" : status === 404 ? "Not found" : "Couldn't process that",
      message: msg,
      guidance: status === 404 ? "Start a new chat or upload the document again." : "Change the file or message and try again.",
      retryable: false,
    };
  }
  return {
    type: "unknown",
    title: "Something went wrong",
    message: msg || "An unexpected error occurred.",
    guidance: "Please try again.",
    retryable: true,
  };
}
