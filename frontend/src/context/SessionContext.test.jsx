import { act, render } from "@testing-library/react";
import toast from "react-hot-toast";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "../api/client";
import * as sessionsApi from "../api/sessions";
import { SessionProvider } from "./SessionContext";

describe("SessionProvider", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.spyOn(toast, "error").mockImplementation(() => "");
  });
  afterEach(() => { vi.useRealTimers(); vi.restoreAllMocks(); });

  it("tells the user once when the conversation list can't load, not every 30 s", async () => {
    vi.spyOn(sessionsApi, "listSessions").mockRejectedValue(new ApiError("Could not reach the server."));
    render(<SessionProvider><div /></SessionProvider>);

    await act(async () => { await vi.advanceTimersByTimeAsync(95000); });

    expect(sessionsApi.listSessions.mock.calls.length).toBeGreaterThanOrEqual(4);
    expect(toast.error).toHaveBeenCalledTimes(1);
    expect(toast.error.mock.calls[0][0]).toMatch(/^Couldn't load your conversations\. Can't reach the server\./);
  });
});
