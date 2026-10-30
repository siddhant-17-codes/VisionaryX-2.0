import { describe, expect, it } from "vitest";
import { ApiError, toApiError } from "../api/client";
import { parseApiError } from "./errorHandler";

const backend = (status, type, message = "Server says no.", retryAfter = null) =>
  new ApiError(message, { status, type, retryAfter });

describe("parseApiError", () => {
  it("recognises the backend's quota error and offers no retry", () => {
    const parsed = parseApiError(backend(429, "LLMQuotaError", "The AI model's free daily quota is used up."));
    expect(parsed.type).toBe("quota");
    expect(parsed.message).toBe("The AI model's free daily quota is used up.");
    expect(parsed.retryable).toBe(false);
  });

  it("tells a rate-limited user how long to wait", () => {
    const parsed = parseApiError(backend(429, "RateLimitError", "Too many requests.", 12));
    expect(parsed.type).toBe("ratelimit");
    expect(parsed.guidance).toContain("12 seconds");
    expect(parsed.retryable).toBe(true);
  });

  it("does not report an unrelated model error as a quota problem", () => {
    const parsed = parseApiError(backend(502, "LLMError", "The AI model could not answer this request."));
    expect(parsed.type).toBe("unavailable");
    expect(parsed.retryable).toBe(true);
  });

  it("explains a missing response as a sleeping server or a connection problem", () => {
    const parsed = parseApiError(new ApiError("Could not reach the server."));
    expect(parsed.type).toBe("network");
    expect(parsed.message).toMatch(/wake up/);
    expect(parsed.retryable).toBe(true);
  });

  it("treats a client timeout as retryable", () => {
    expect(parseApiError(new ApiError("slow", { type: "Timeout" })).type).toBe("timeout");
  });

  it("shows the backend's own reason for a rejected upload, without a retry button", () => {
    const parsed = parseApiError(backend(422, "DocumentProcessingError", "No readable text found."));
    expect(parsed.type).toBe("request");
    expect(parsed.message).toBe("No readable text found.");
    expect(parsed.retryable).toBe(false);
  });

  it("hides internal details of a 500", () => {
    const parsed = parseApiError(backend(500, "InternalServerError", "An unexpected error occurred."));
    expect(parsed.type).toBe("server");
    expect(parsed.message).toMatch(/nothing to change on your end/);
  });

  it("falls back to the raw message for unknown errors", () => {
    expect(parseApiError(new Error("Something odd")).message).toBe("Something odd");
  });

  it("never shows developer setup advice to visitors", () => {
    const cases = [
      new Error("Something odd"), new ApiError("x"), new ApiError("x", { type: "Timeout" }),
      ...[400, 404, 413, 415, 422, 429, 500, 502, 503, 504].map((s) => backend(s, "HttpError")),
    ];
    for (const err of cases) {
      const { title, message, guidance } = parseApiError(err);
      expect(`${title} ${message} ${guidance}`).not.toMatch(/\.env|make dev|API key|backend/i);
    }
  });
});

describe("toApiError", () => {
  it("keeps status, type and Retry-After from a backend response", () => {
    const err = toApiError({ response: { status: 429, data: { error: "Slow down.", type: "RateLimitError" },
                                         headers: { "retry-after": "7" } } });
    expect(err).toMatchObject({ message: "Slow down.", status: 429, type: "RateLimitError", retryAfter: 7 });
  });

  it("marks an axios timeout and a missing response differently", () => {
    expect(toApiError({ code: "ECONNABORTED" }).type).toBe("Timeout");
    expect(toApiError({ code: "ERR_NETWORK" })).toMatchObject({ status: 0, type: "NetworkError" });
  });

  it("does not show FastAPI's validation list as a message", () => {
    const err = toApiError({ response: { status: 422, data: { detail: [{ msg: "x" }] }, headers: {} } });
    expect(err.message).toBe("Something went wrong. Please try again.");
  });
});
