import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CitationCard from "./CitationCard";

describe("CitationCard", () => {
  it("names the file and the page", () => {
    render(<CitationCard index={0} citation={{ source: "lumen_ridge_report.pdf", page: 2, chunk: "Harvest…" }} />);
    expect(screen.getByText("lumen_ridge_report.pdf")).toHaveAttribute("title", "lumen_ridge_report.pdf");
    expect(screen.getByText("· p. 2")).toBeInTheDocument();
  });

  it("still shows the page for answers from older indexes without a file name", () => {
    render(<CitationCard index={0} citation={{ source: null, page: 3, chunk: "Text" }} />);
    expect(screen.getByText("Page 3")).toBeInTheDocument();
  });
});
