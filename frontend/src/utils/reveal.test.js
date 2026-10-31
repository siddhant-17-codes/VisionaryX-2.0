import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { REVEAL_MS, reveal } from "./reveal";

describe("reveal", () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  async function timeToReveal(text) {
    const shown = [];
    const start = Date.now();
    const done = reveal(text, (t) => shown.push(t));
    await vi.runAllTimersAsync();
    await done;
    return { ms: Date.now() - start, shown };
  }

  it("shows a 400-word answer in about a second, not seven", async () => {
    const text = Array.from({ length: 400 }, (_, i) => `word${i}`).join(" ");
    const { ms, shown } = await timeToReveal(text);
    expect(ms).toBeLessThanOrEqual(REVEAL_MS);
    expect(shown.at(-1)).toBe(text);
    expect(shown.length).toBeGreaterThan(10);  // still animated
  });

  it("finishes short answers quickly", async () => {
    const { ms, shown } = await timeToReveal("Ping");
    expect(ms).toBeLessThanOrEqual(25);
    expect(shown.at(-1)).toBe("Ping");
  });

  it("never loses or reorders words", async () => {
    const text = "one two three four five six seven eight nine ten eleven";
    const { shown } = await timeToReveal(text);
    for (const partial of shown) expect(text.startsWith(partial)).toBe(true);
    expect(shown.at(-1)).toBe(text);
  });
});
