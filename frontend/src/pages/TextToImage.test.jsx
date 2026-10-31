import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "../api/client";
import * as imageApi from "../api/image";
import TextToImage from "./TextToImage";

vi.mock("../api/image", () => ({ getImageStatus: vi.fn(), generateImage: vi.fn(), queryImage: vi.fn() }));
vi.mock("../api/sessions", () => ({
  createSession: vi.fn().mockResolvedValue({ id: "s1" }),
  getSession: vi.fn().mockRejectedValue(new Error("none")),
}));

describe("TextToImage", () => {
  beforeEach(() => { vi.clearAllMocks(); localStorage.clear(); });

  it("shows the paused state before anyone types", async () => {
    imageApi.getImageStatus.mockResolvedValue({ available: false, resumes_at: "2099-01-01T00:00:00+00:00" });
    render(<TextToImage />);
    expect(await screen.findByText("Image generation is paused")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Paused" })).toBeDisabled();
  });

  it("switches to the paused state when a generation hits the quota", async () => {
    imageApi.getImageStatus.mockResolvedValue({ available: true, resumes_at: null });
    imageApi.generateImage.mockRejectedValue(
      new ApiError("paused", { status: 503, type: "ImageQuotaExceededError", retryAfter: 3600 }));
    render(<TextToImage />);
    await userEvent.type(screen.getByRole("textbox"), "a red apple");
    await userEvent.click(screen.getByRole("button", { name: "Generate Image" }));
    expect(await screen.findByText("Image generation is paused")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Paused" })).toBeDisabled();
  });

  it("works normally when available", async () => {
    imageApi.getImageStatus.mockResolvedValue({ available: true, resumes_at: null });
    imageApi.generateImage.mockResolvedValue("iVBORw0KGgo=");
    render(<TextToImage />);
    await userEvent.type(screen.getByRole("textbox"), "a red apple");
    await userEvent.click(screen.getByRole("button", { name: "Generate Image" }));
    expect(await screen.findByAltText("generated")).toBeInTheDocument();
    expect(screen.queryByText("Image generation is paused")).toBeNull();
  });
});
