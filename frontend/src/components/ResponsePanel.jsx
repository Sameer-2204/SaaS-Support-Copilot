import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { FileText } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

/**
 * Renders the LLM-generated draft response with proper markdown formatting
 * and inline citation highlighting. Citations like [1], [2] are styled as
 * clickable badges that link to the corresponding source.
 */
export default function ResponsePanel({ response }) {
  if (!response) return null;

  // Custom renderer to inject citation badges into text nodes
  const injectCitations = (text) => {
    if (typeof text !== 'string') return text;
    const parts = text.split(/(\[\d+\])/g);
    if (parts.length === 1) return text;

    return parts.map((part, i) => {
      const match = part.match(/^\[(\d+)\]$/);
      if (match) {
        return (
          <a
            key={i}
            href={`#source-${match[1]}`}
            className="inline-flex items-center justify-center w-5 h-5 text-[10px] font-bold rounded bg-primary/30 text-primary-foreground hover:bg-primary/50 transition-colors mx-0.5 align-super cursor-pointer"
            title={`View source ${match[1]}`}
          >
            {match[1]}
          </a>
        );
      }
      return <span key={i}>{part}</span>;
    });
  };

  // Custom markdown components for polished rendering
  const markdownComponents = {
    p: ({ children }) => (
      <p className="mb-3 last:mb-0 text-gray-200 leading-relaxed">
        {Array.isArray(children)
          ? children.map((child, i) =>
              typeof child === 'string' ? <span key={i}>{injectCitations(child)}</span> : child
            )
          : typeof children === 'string'
          ? injectCitations(children)
          : children}
      </p>
    ),
    strong: ({ children }) => (
      <strong className="font-semibold text-white">{children}</strong>
    ),
    em: ({ children }) => (
      <em className="italic text-gray-300">{children}</em>
    ),
    h1: ({ children }) => (
      <h3 className="text-lg font-bold text-white mt-4 mb-2 border-b border-white/10 pb-1">
        {children}
      </h3>
    ),
    h2: ({ children }) => (
      <h4 className="text-base font-bold text-white mt-4 mb-2">{children}</h4>
    ),
    h3: ({ children }) => (
      <h5 className="text-sm font-semibold text-gray-100 mt-3 mb-1">{children}</h5>
    ),
    ul: ({ children }) => (
      <ul className="my-2 ml-1 space-y-1.5">{children}</ul>
    ),
    ol: ({ children }) => (
      <ol className="my-2 ml-1 space-y-1.5 list-decimal list-inside">{children}</ol>
    ),
    li: ({ children, ordered }) => (
      <li className="flex items-start gap-2 text-gray-200">
        {!ordered && (
          <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0" />
        )}
        <span className="flex-1">{children}</span>
      </li>
    ),
    code: ({ children, inline }) =>
      inline ? (
        <code className="px-1.5 py-0.5 rounded bg-white/10 text-emerald-300 text-xs font-mono">
          {children}
        </code>
      ) : (
        <pre className="my-3 p-3 rounded-lg bg-black/40 border border-white/10 overflow-x-auto">
          <code className="text-xs font-mono text-emerald-300 whitespace-pre-wrap">
            {children}
          </code>
        </pre>
      ),
    blockquote: ({ children }) => (
      <blockquote className="my-3 pl-4 border-l-2 border-primary/50 text-gray-300 italic">
        {children}
      </blockquote>
    ),
    a: ({ href, children }) => (
      <a
        href={href}
        className="text-primary underline underline-offset-2 hover:text-primary/80 transition-colors"
        target="_blank"
        rel="noopener noreferrer"
      >
        {children}
      </a>
    ),
    hr: () => <hr className="my-4 border-white/10" />,
  };

  return (
    <Card className="fade-in glow-purple">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <FileText className="w-4 h-4 text-primary" />
          Draft Response
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="prose prose-invert prose-sm max-w-none">
          <ReactMarkdown components={markdownComponents}>
            {response}
          </ReactMarkdown>
        </div>
      </CardContent>
    </Card>
  );
}
