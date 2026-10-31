// The landing page claims only what the code does: answers come from a Gemini model
// chain with fallback (not one fixed model), chunking is recursive character splitting,
// and citations come from the retrieved chunks.
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import Landing from "./Landing";

vi.mock("../api/health", () => ({ wakeServer: vi.fn() }));

const page = () => render(<MemoryRouter><Landing /></MemoryRouter>).container.textContent;

describe("landing page copy", () => {
  it("does not name a single fixed model", () => {
    const text = page();
    expect(text).not.toMatch(/Gemini 2\.5|Gemini Flash|Gemini Vision/);
    expect(screen.getAllByText("Google Gemini · automatic fallback").length).toBe(2);
    expect(screen.getByText("Auto fallback")).toBeInTheDocument();
  });

  it("describes chunking and citations as they work", () => {
    const text = page();
    expect(text).not.toMatch(/semantic chunking|page-level citations/i);
    expect(screen.getByText("Recursive character chunking (1,000 chars, 150 overlap)")).toBeInTheDocument();
    expect(text).toContain("Citations are built from the retrieved chunks, deduplicated by file, page and section.");
  });

  it("does not promise a structured image analysis", () => {
    expect(page()).not.toMatch(/structured/i);
  });
});
