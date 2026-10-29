import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChatBubble from "./ChatBubble";

describe("ChatBubble", () => {
  it("shows the user's text as typed", () => {
    render(<ChatBubble role="user" content="**not markdown**" />);
    expect(screen.getByText("**not markdown**")).toBeInTheDocument();
  });

  it("renders assistant markdown", () => {
    render(<ChatBubble role="assistant" content="The harvest was **1,870 tonnes**." />);
    expect(screen.getByText("1,870 tonnes").tagName).toBe("STRONG");
  });

  it("lists a source card per citation with its page", () => {
    const citations = [
      { page: 2, chunk: "Total apple harvest in 2025…" },
      { page: 4, chunk: "Revenue was 3.4 million credits…" },
    ];
    render(<ChatBubble role="assistant" content="Answer" citations={citations} />);
    expect(screen.getByText("2 citations")).toBeInTheDocument();
    expect(screen.getByText("Page 2")).toBeInTheDocument();
    expect(screen.getByText("Page 4")).toBeInTheDocument();
  });

  // U4: fixed in feat/ui-polish-a11y
  it.fails("keeps inline code inline", () => {
    const { container } = render(<ChatBubble role="assistant" content="Run `npm test` now." />);
    expect(container.querySelector("pre")).toBeNull();
  });

  // U4: fixed in feat/ui-polish-a11y
  it.fails("keeps numbers on ordered lists", () => {
    const { container } = render(<ChatBubble role="assistant" content={"1. First\n2. Second"} />);
    expect(container.textContent).toContain("1.");
  });
});
