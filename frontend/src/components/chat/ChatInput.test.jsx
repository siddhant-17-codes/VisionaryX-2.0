import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ChatInput from "./ChatInput";

describe("ChatInput", () => {
  it("sends the trimmed message on Enter and clears the box", async () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} loading={false} />);
    const box = screen.getByPlaceholderText("Ask VisionaryX anything…");

    await userEvent.type(box, "  hello there  {Enter}");

    expect(onSend).toHaveBeenCalledWith("hello there");
    expect(box).toHaveValue("");
  });

  it("adds a new line on Shift+Enter instead of sending", async () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} loading={false} />);

    await userEvent.type(screen.getByRole("textbox"), "line one{Shift>}{Enter}{/Shift}line two");

    expect(onSend).not.toHaveBeenCalled();
    expect(screen.getByRole("textbox")).toHaveValue("line one\nline two");
  });

  it("is disabled while a reply is loading", () => {
    render(<ChatInput onSend={vi.fn()} loading={true} />);
    expect(screen.getByRole("textbox")).toBeDisabled();
  });
});
