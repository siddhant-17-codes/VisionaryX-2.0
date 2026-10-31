// F5: no empty sessions from just opening a page; the model that answered is shown.
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as chatApi from "../api/chat";
import * as imageApi from "../api/image";
import * as sessionsApi from "../api/sessions";
import Chat from "./Chat";
import ImageQuery from "./ImageQuery";
import TextToImage from "./TextToImage";

vi.mock("../api/chat", () => ({ sendMessage: vi.fn() }));
vi.mock("../api/image", () => ({ queryImage: vi.fn(), generateImage: vi.fn(),
  getImageStatus: vi.fn().mockResolvedValue({ available: true, resumes_at: null }) }));
vi.mock("../api/sessions", () => ({ createSession: vi.fn(), getSession: vi.fn() }));
vi.mock("../utils/reveal", () => ({ reveal: async (text, onUpdate) => onUpdate(text) }));

const renderAt = (ui) => render(<MemoryRouter>{ui}</MemoryRouter>);

describe("sessions are created only when there is something to save (F5)", () => {
  beforeEach(() => { vi.clearAllMocks(); localStorage.clear(); });

  it("opening Chat creates nothing; the first message creates one session", async () => {
    sessionsApi.createSession.mockResolvedValue({ id: "s1" });
    chatApi.sendMessage.mockResolvedValue({ reply: "Hello!", model: "gemini-3.1-flash-lite" });
    renderAt(<Chat />);
    expect(sessionsApi.createSession).not.toHaveBeenCalled();

    await userEvent.type(screen.getByRole("textbox"), "hi{Enter}");
    expect(await screen.findByText("Hello!")).toBeInTheDocument();
    expect(sessionsApi.createSession).toHaveBeenCalledTimes(1);
    expect(chatApi.sendMessage).toHaveBeenCalledWith("hi", [], "s1");

    await userEvent.type(screen.getByRole("textbox"), "again{Enter}");
    await screen.findAllByText("Hello!");
    expect(sessionsApi.createSession).toHaveBeenCalledTimes(1);  // reused
  });

  it("shows which model answered", async () => {
    sessionsApi.createSession.mockResolvedValue({ id: "s1" });
    chatApi.sendMessage.mockResolvedValue({ reply: "Hello!", model: "gemini-3.1-flash-lite" });
    renderAt(<Chat />);
    await userEvent.type(screen.getByRole("textbox"), "hi{Enter}");
    expect(await screen.findByText("Answered by gemini-3.1-flash-lite")).toBeInTheDocument();
  });

  it("Image Query and Text to Image never create sessions", async () => {
    imageApi.queryImage.mockResolvedValue({ answer: "Three bars.", model: "gemini-2.5-flash" });
    renderAt(<ImageQuery />);
    renderAt(<TextToImage />);
    await screen.findAllByRole("button");
    expect(sessionsApi.createSession).not.toHaveBeenCalled();
    expect(sessionsApi.getSession).not.toHaveBeenCalled();
  });
});
