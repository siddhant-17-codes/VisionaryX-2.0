// U5: keyboard and screen-reader access to the sidebar, navbar dialog and uploaders.
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import PDFUploader from "../pdf/PDFUploader";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

const removeSession = vi.fn();
vi.mock("../../context/SessionContext", () => ({
  useSessionContext: () => ({
    sessions: [{ id: "s1", title: "Orchard report", mode: "pdf" }],
    newSession: vi.fn(),
    removeSession,
  }),
}));

const inRouter = (ui) => render(<MemoryRouter>{ui}</MemoryRouter>);

describe("Sidebar", () => {
  beforeEach(() => removeSession.mockClear());
  afterEach(() => vi.restoreAllMocks());

  it("lets the keyboard reach each conversation", async () => {
    inRouter(<Sidebar />);
    expect(screen.getByRole("button", { name: "Orchard report" })).toBeInTheDocument();
  });

  it("says that history is kept per browser", () => {
    inRouter(<Sidebar />);
    expect(screen.getByText("Your history is saved in this browser only.")).toBeInTheDocument();
  });

  it("labels delete and asks before deleting", async () => {
    inRouter(<Sidebar />);
    const del = screen.getByRole("button", { name: "Delete conversation: Orchard report" });

    vi.spyOn(window, "confirm").mockReturnValueOnce(false);
    await userEvent.click(del);
    expect(removeSession).not.toHaveBeenCalled();

    vi.spyOn(window, "confirm").mockReturnValueOnce(true);
    await userEvent.click(del);
    expect(removeSession).toHaveBeenCalledWith("s1");
  });

  it("keeps delete visible on touch screens (hidden only from md up until hover or focus)", () => {
    inRouter(<Sidebar />);
    const del = screen.getByRole("button", { name: /Delete conversation/ });
    expect(del).toHaveClass("md:opacity-0", "md:group-hover:opacity-100", "focus:opacity-100");
    expect(del).not.toHaveClass("opacity-0");
  });
});

describe("Navbar demo guide", () => {
  it("is a labelled dialog that closes on Escape", async () => {
    inRouter(<Navbar />);
    await userEvent.click(screen.getAllByRole("button", { name: "Demo" })[0]);
    expect(screen.getByRole("dialog", { name: "How to use VisionaryX" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Close guide" })).toHaveFocus();

    await userEvent.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("labels the icon-only menu button", () => {
    inRouter(<Navbar />);
    expect(screen.getByRole("button", { name: "Open menu" })).toHaveAttribute("aria-expanded", "false");
  });
});

describe("PDFUploader", () => {
  it("opens the file picker from the keyboard", async () => {
    render(<PDFUploader onUpload={vi.fn()} loading={false} />);
    const zone = screen.getByRole("button", { name: "Upload PDF or DOCX files" });
    const picker = zone.querySelector("input[type=file]");
    const click = vi.spyOn(picker, "click");
    zone.focus();
    await userEvent.keyboard("{Enter}");
    expect(click).toHaveBeenCalled();
  });

  it("shows progress and ignores clicks while a file is processing", async () => {
    render(<PDFUploader onUpload={vi.fn()} loading={true} />);
    const zone = screen.getByRole("button", { name: "Upload PDF or DOCX files" });
    expect(zone).toHaveAttribute("aria-busy", "true");
    expect(screen.getByText("Reading and indexing your documents…")).toBeInTheDocument();
    const click = vi.spyOn(zone.querySelector("input[type=file]"), "click");
    await userEvent.click(zone);
    expect(click).not.toHaveBeenCalled();
  });
});
