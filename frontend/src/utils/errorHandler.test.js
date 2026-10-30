import { describe, expect, it } from "vitest";
import { parseApiError } from "./errorHandler";

describe("parseApiError", () => {
  it("recognises a Gemini quota error", () => {
    const parsed = parseApiError(new Error("LLM error: 429 You exceeded your current quota"));
    expect(parsed.type).toBe("quota");
  });

  it("recognises a timeout as a connection problem", () => {
    expect(parseApiError(new Error("timeout of 120000ms exceeded")).type).toBe("network");
  });

  it("falls back to the raw message for unknown errors", () => {
    expect(parseApiError(new Error("Something odd")).message).toBe("Something odd");
  });

  // R2: fixed in feat/ui-cold-start-errors
  it.fails("does not report an unrelated model error as a quota problem", () => {
    expect(parseApiError(new Error("LLM error: contents must not be empty")).type).not.toBe("quota");
  });

  // R2: fixed in feat/ui-cold-start-errors
  it.fails("never shows developer setup advice to visitors", () => {
    expect(parseApiError(new Error("Something odd")).guidance).not.toMatch(/\.env|make dev/);
  });
});
