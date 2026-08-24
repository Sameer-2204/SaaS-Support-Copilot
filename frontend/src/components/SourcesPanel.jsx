import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ChevronDown, ChevronUp, BookOpen } from 'lucide-react';
import { getSourceTypeColor, getSourceTypeLabel } from '../lib/utils';

/**
 * Collapsible panel showing cited source chunks with metadata.
 */
export default function SourcesPanel({ sources }) {
  const [expandedIndex, setExpandedIndex] = useState(null);

  if (!sources || sources.length === 0) return null;

  const toggleExpand = (index) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  return (
    <Card className="fade-in">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <BookOpen className="w-4 h-4 text-primary" />
          Sources ({sources.length})
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {sources.map((source, i) => (
          <div
            key={source.chunk_id}
            id={`source-${source.index}`}
            className="border border-border/40 rounded-lg overflow-hidden transition-all duration-200 hover:border-border/80"
          >
            {/* Source Header */}
            <button
              onClick={() => toggleExpand(i)}
              className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-secondary/30 transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className="flex items-center justify-center w-6 h-6 text-xs font-bold rounded bg-primary/20 text-primary-foreground">
                  {source.index}
                </span>
                <span
                  className={`text-xs px-2 py-0.5 rounded-full border ${getSourceTypeColor(
                    source.source_type
                  )}`}
                >
                  {getSourceTypeLabel(source.source_type)}
                </span>
                <span className="text-xs text-muted-foreground">
                  {source.product}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground">
                  Score: {(source.reranker_score * 100).toFixed(0)}%
                </span>
                {expandedIndex === i ? (
                  <ChevronUp className="w-4 h-4 text-muted-foreground" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-muted-foreground" />
                )}
              </div>
            </button>

            {/* Expanded Content */}
            {expandedIndex === i && (
              <div className="px-4 pb-4 border-t border-border/30">
                <p className="text-sm text-gray-300 mt-3 leading-relaxed whitespace-pre-wrap">
                  {source.text}
                </p>
              </div>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
