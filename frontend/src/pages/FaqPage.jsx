import { useState, useMemo } from 'react';
import { Search, ChevronDown, HelpCircle, MessageSquare } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import faqData from '../data/faq-data';

/**
 * FaqPage — Self-service FAQ with search, category filters, and accordion answers.
 * Customers can find answers without submitting a ticket.
 */
export default function FaqPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedItems, setExpandedItems] = useState(new Set());
  const [activeCategory, setActiveCategory] = useState(null);
  const navigate = useNavigate();

  // Filter FAQs based on search and category
  const filteredData = useMemo(() => {
    const query = searchQuery.toLowerCase().trim();

    return faqData
      .map((section) => {
        // Filter by category
        if (activeCategory && section.category !== activeCategory) {
          return { ...section, items: [] };
        }

        // Filter by search query
        const filteredItems = section.items.filter((item) => {
          if (!query) return true;
          return (
            item.q.toLowerCase().includes(query) ||
            item.a.toLowerCase().includes(query) ||
            item.tags.some((t) => t.includes(query))
          );
        });

        return { ...section, items: filteredItems };
      })
      .filter((section) => section.items.length > 0);
  }, [searchQuery, activeCategory]);

  const totalResults = filteredData.reduce((sum, s) => sum + s.items.length, 0);

  const toggleItem = (key) => {
    setExpandedItems((prev) => {
      const next = new Set(prev);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  // Simple markdown-like formatting for answers
  const formatAnswer = (text) => {
    return text
      .split('\n')
      .map((line, i) => {
        // Bold
        line = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        // Code
        line = line.replace(/`(.+?)`/g, '<code class="px-1 py-0.5 rounded bg-secondary text-xs">$1</code>');
        // Numbered list
        if (/^\d+\.\s/.test(line)) {
          return `<div key="${i}" class="ml-4 mb-1">${line}</div>`;
        }
        // Bullet
        if (line.startsWith('- ')) {
          return `<div key="${i}" class="ml-4 mb-1">• ${line.slice(2)}</div>`;
        }
        // Empty line
        if (line.trim() === '') {
          return `<div key="${i}" class="h-2"></div>`;
        }
        return `<div key="${i}" class="mb-1">${line}</div>`;
      })
      .join('');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold gradient-text flex items-center gap-3">
          <HelpCircle className="w-8 h-8" />
          Frequently Asked Questions
        </h1>
        <p className="text-muted-foreground">
          Find quick answers to common questions. Can't find what you need?{' '}
          <button
            onClick={() => navigate('/')}
            className="text-primary hover:underline"
          >
            Submit a support ticket
          </button>
          .
        </p>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search FAQs... (e.g., 'refund', 'shipping', 'SMS')"
          className="w-full pl-10 pr-4 py-3 rounded-xl bg-secondary/40 border border-border/40 text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
          id="faq-search"
        />
        {searchQuery && (
          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">
            {totalResults} result{totalResults !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {/* Category Filters */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setActiveCategory(null)}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            activeCategory === null
              ? 'bg-primary/20 text-primary ring-1 ring-primary/30'
              : 'bg-secondary/50 text-muted-foreground hover:bg-secondary'
          }`}
        >
          All
        </button>
        {faqData.map((section) => (
          <button
            key={section.category}
            onClick={() =>
              setActiveCategory(
                activeCategory === section.category ? null : section.category
              )
            }
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeCategory === section.category
                ? 'bg-primary/20 text-primary ring-1 ring-primary/30'
                : 'bg-secondary/50 text-muted-foreground hover:bg-secondary'
            }`}
          >
            {section.icon} {section.category}
          </button>
        ))}
      </div>

      {/* FAQ Sections */}
      {filteredData.length === 0 ? (
        <div className="glass-card p-8 text-center space-y-3">
          <Search className="w-8 h-8 text-muted-foreground/40 mx-auto" />
          <p className="text-muted-foreground">
            No FAQs match your search. Try different keywords or{' '}
            <button
              onClick={() => navigate('/')}
              className="text-primary hover:underline"
            >
              ask our AI copilot
            </button>
            .
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {filteredData.map((section) => (
            <div key={section.category} className="space-y-2">
              {/* Section Header */}
              <h2 className="text-sm font-semibold text-muted-foreground flex items-center gap-2 px-1">
                <span>{section.icon}</span>
                {section.category}
                <span className="text-xs font-normal">
                  ({section.items.length})
                </span>
              </h2>

              {/* FAQ Items */}
              <div className="space-y-1.5">
                {section.items.map((item, idx) => {
                  const key = `${section.category}-${idx}`;
                  const isExpanded = expandedItems.has(key);

                  return (
                    <div
                      key={key}
                      className={`rounded-xl border transition-all ${
                        isExpanded
                          ? 'border-primary/20 bg-primary/5'
                          : 'border-border/40 bg-secondary/20 hover:bg-secondary/30'
                      }`}
                    >
                      <button
                        onClick={() => toggleItem(key)}
                        className="w-full px-4 py-3 flex items-start justify-between text-left gap-3"
                        id={`faq-${section.category.replace(/\s+/g, '-')}-${idx}`}
                      >
                        <span className="text-sm font-medium text-foreground leading-snug">
                          {item.q}
                        </span>
                        <ChevronDown
                          className={`w-4 h-4 text-muted-foreground flex-shrink-0 mt-0.5 transition-transform ${
                            isExpanded ? 'rotate-180' : ''
                          }`}
                        />
                      </button>

                      {isExpanded && (
                        <div className="px-4 pb-4 fade-in">
                          <div
                            className="text-sm text-muted-foreground leading-relaxed"
                            dangerouslySetInnerHTML={{
                              __html: formatAnswer(item.a),
                            }}
                          />
                          {/* Tags */}
                          <div className="flex flex-wrap gap-1 mt-3">
                            {item.tags.map((tag) => (
                              <span
                                key={tag}
                                className="px-1.5 py-0.5 text-[10px] rounded bg-secondary/60 text-muted-foreground/70"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* CTA Banner */}
      <div className="glass-card p-6 text-center space-y-3 glow-purple">
        <MessageSquare className="w-6 h-6 text-primary mx-auto" />
        <p className="text-sm text-foreground font-medium">
          Still need help?
        </p>
        <p className="text-xs text-muted-foreground">
          Our AI support copilot can provide personalized solutions with cited sources.
        </p>
        <Button
          onClick={() => navigate('/')}
          size="sm"
          className="bg-primary/90 hover:bg-primary text-primary-foreground"
        >
          <MessageSquare className="w-3.5 h-3.5 mr-1.5" />
          Submit a Support Ticket
        </Button>
      </div>
    </div>
  );
}
