import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import SuggestedQuestions from "./SuggestedQuestions";

describe("SuggestedQuestions", () => {
  it("asks the clicked question", async () => {
    const onSelect = vi.fn();
    render(<SuggestedQuestions questions={["Who is the treasurer?", "How much water?"]} onSelect={onSelect} />);

    await userEvent.click(screen.getByRole("button", { name: "How much water?" }));

    expect(onSelect).toHaveBeenCalledWith("How much water?");
  });

  it("renders nothing without questions", () => {
    const { container } = render(<SuggestedQuestions questions={[]} onSelect={vi.fn()} />);
    expect(container).toBeEmptyDOMElement();
  });
});
