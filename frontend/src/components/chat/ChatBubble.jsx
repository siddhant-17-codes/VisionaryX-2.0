import ReactMarkdown from "react-markdown";
import CitationCard from "../pdf/CitationCard";

export default function ChatBubble({ role, content, citations = [] }) {
  const isUser = role === "user";
  return (
    <div className={`flex flex-col gap-2 ${isUser ? "items-end" : "items-start"}`}>
      {isUser ? (
        <div className="msg-user">{content}</div>
      ) : (
        <div className="bg-[#0D0B16] border border-[#1C1628] text-[#D4C8E8]
                        rounded-2xl rounded-tl-sm px-5 py-4 text-sm leading-7
                        max-w-[88%] font-sans">
          <ReactMarkdown
            components={{
              p: ({ children }) => <p className="mb-3 last:mb-0 text-[#D4C8E8] leading-7">{children}</p>,
              strong: ({ children }) => <strong className="text-[#FEA735] font-semibold">{children}</strong>,
              em: ({ children }) => <em className="text-[#FCF5EF] not-italic font-medium">{children}</em>,
              h1: ({ children }) => <h1 className="text-base font-bold text-linen mb-2 mt-3">{children}</h1>,
              h2: ({ children }) => <h2 className="text-sm font-bold text-linen mb-2 mt-3">{children}</h2>,
              h3: ({ children }) => <h3 className="text-sm font-semibold text-[#FCF5EF] mb-1.5 mt-2">{children}</h3>,
              ul: ({ children }) => <ul className="list-none space-y-1.5 mb-3 pl-1">{children}</ul>,
              ol: ({ children }) => <ol className="list-none space-y-1.5 mb-3 pl-1 counter-reset-item">{children}</ol>,
              li: ({ children }) => (
                <li className="flex gap-2 text-[#C4B8D8] text-sm leading-relaxed">
                  <span className="text-primary mt-0.5 flex-shrink-0">·</span>
                  <span>{children}</span>
                </li>
              ),
              code: ({ inline, children }) =>
                inline ? (
                  <code className="bg-[#1C1628] text-[#FEA735] px-1.5 py-0.5 rounded text-xs font-mono">{children}</code>
                ) : (
                  <pre className="bg-[#08060E] border border-border rounded-lg p-3 my-2 overflow-x-auto">
                    <code className="text-xs font-mono text-[#C4B8D8] leading-relaxed">{children}</code>
                  </pre>
                ),
              blockquote: ({ children }) => (
                <blockquote className="border-l-2 border-primary pl-4 my-2 text-muted italic">{children}</blockquote>
              ),
              a: ({ href, children }) => (
                <a href={href} className="text-cyan underline underline-offset-2 hover:text-[#00D4FF]"
                   target="_blank" rel="noreferrer">{children}</a>
              ),
              hr: () => <hr className="border-border my-3" />,
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
      )}
      {citations.length > 0 && (
        <div className="w-full max-w-[88%]">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-[9px] font-bold text-hint uppercase tracking-widest">Sources</span>
            <div className="flex-1 h-px bg-border" />
            <span className="badge-blue">{citations.length} citation{citations.length > 1 ? "s" : ""}</span>
          </div>
          <div className="flex gap-2 flex-wrap">
            {citations.map((c, i) => <CitationCard key={i} citation={c} index={i} />)}
          </div>
        </div>
      )}
    </div>
  );
}
