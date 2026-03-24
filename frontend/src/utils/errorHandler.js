export function parseApiError(error) {
  const msg = error?.message || "";

  if (msg.includes("429") || msg.includes("quota") || msg.includes("RESOURCE_EXHAUSTED") || msg.includes("LLM error")) {
    return {
      type: "quota",
      title: "Daily quota reached",
      message: "The Gemini API free tier limit has been hit for today.",
      guidance: "Quota resets every 24 hours. Check your usage at ai.dev/rate-limit.",
      retryable: false,
    };
  }
  if (msg.includes("rate") || msg.includes("retry") || msg.includes("429")) {
    return {
      type: "ratelimit",
      title: "Too many requests",
      message: "The AI service is temporarily rate-limited.",
      guidance: "Wait 30–60 seconds, then try again.",
      retryable: true,
    };
  }
  if (msg.includes("network") || msg.includes("timeout") || msg.includes("ECONNREFUSED") || msg.includes("ERR_")) {
    return {
      type: "network",
      title: "Connection issue",
      message: "Could not reach the VisionaryX backend.",
      guidance: "Ensure the backend is running: cd backend && make dev",
      retryable: true,
    };
  }
  if (msg.includes("500") || msg.includes("Internal")) {
    return {
      type: "server",
      title: "Server error",
      message: "Something went wrong on the backend.",
      guidance: "Restart the backend and try again.",
      retryable: true,
    };
  }
  return {
    type: "unknown",
    title: "AI service unavailable",
    message: msg || "An unexpected error occurred.",
    guidance: "Check your API keys in the .env file and try again.",
    retryable: true,
  };
}
