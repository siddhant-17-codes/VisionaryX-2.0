import { afterEach, describe, expect, it, vi } from "vitest";
import { getClientId, resetClientIdForTests } from "./clientId";

afterEach(() => {
  localStorage.clear();
  resetClientIdForTests();
  vi.restoreAllMocks();
});

describe("getClientId", () => {
  it("creates a 32-character id and keeps it across calls", () => {
    const id = getClientId();
    expect(id).toMatch(/^[0-9a-f]{32}$/);
    expect(getClientId()).toBe(id);
    expect(localStorage.getItem("vx_client_id")).toBe(id);
  });

  it("reuses the id stored by an earlier visit", () => {
    localStorage.setItem("vx_client_id", "f".repeat(32));
    expect(getClientId()).toBe("f".repeat(32));
  });

  it("replaces a tampered stored value", () => {
    localStorage.setItem("vx_client_id", "not valid!");
    expect(getClientId()).toMatch(/^[0-9a-f]{32}$/);
  });

  it("still works when storage is blocked", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => { throw new Error("blocked"); });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => { throw new Error("blocked"); });
    const id = getClientId();
    expect(id).toMatch(/^[0-9a-f]{32}$/);
    expect(getClientId()).toBe(id);
  });
});
