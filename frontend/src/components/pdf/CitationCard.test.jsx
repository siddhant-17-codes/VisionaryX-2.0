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

describe("CitationCard for Word documents", () => {
  it("shows the section heading instead of a page", () => {
    render(<CitationCard index={0} citation={{ source: "h.docx", page: 0, section: "Shifts", chunk: "x" }} />);
    expect(screen.getByText("· Shifts")).toBeInTheDocument();
    expect(screen.queryByText(/p\. 0/)).toBeNull();
  });

  it("shows just the file name when the document has no headings", () => {
    const { container } = render(<CitationCard index={0} citation={{ source: "h.docx", page: 0, chunk: "x" }} />);
    expect(screen.getByText("h.docx")).toBeInTheDocument();
    expect(container.textContent).not.toMatch(/p\. 0|Page 0/);
  });
});
