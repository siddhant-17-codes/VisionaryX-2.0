import { act, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import client from "../../api/client";
import { resetServerStatus, WAKE_NOTICE_MS, wakeServer } from "../../api/health";
import ServerStatusBanner from "./ServerStatusBanner";

function pendingHealth() {
  let answer;
  vi.spyOn(client, "get").mockReturnValue(new Promise((resolve, reject) => { answer = { resolve, reject }; }));
  return answer;
}

describe("ServerStatusBanner", () => {
  beforeEach(() => { vi.useFakeTimers(); resetServerStatus(); });
  afterEach(() => { vi.useRealTimers(); vi.restoreAllMocks(); });

  it("stays hidden when the server answers quickly", async () => {
    const health = pendingHealth();
    render(<ServerStatusBanner />);
    wakeServer();
    await act(async () => { health.resolve({}); });
    await act(async () => { vi.advanceTimersByTime(WAKE_NOTICE_MS); });
    expect(screen.queryByRole("status")).toBeNull();
  });

  it("explains a slow start, then disappears once the server is up", async () => {
    const health = pendingHealth();
    render(<ServerStatusBanner />);
    wakeServer();
    await act(async () => { vi.advanceTimersByTime(WAKE_NOTICE_MS); });
    expect(screen.getByRole("status")).toHaveTextContent("Waking up the server");

    await act(async () => { health.resolve({}); });
    expect(screen.queryByRole("status")).toBeNull();
  });

  it("offers a retry when the server can't be reached", async () => {
    const health = pendingHealth();
    render(<ServerStatusBanner />);
    wakeServer();
    await act(async () => { health.reject(new Error("down")); });
    expect(screen.getByRole("status")).toHaveTextContent("Can't reach the server");
    expect(screen.getByRole("button", { name: "Try again" })).toBeInTheDocument();
  });

  it("pings /health only once while a check is in flight", () => {
    pendingHealth();
    wakeServer();
    wakeServer();
    expect(client.get).toHaveBeenCalledTimes(1);
    expect(client.get).toHaveBeenCalledWith("/health", expect.anything());
  });
});
