import { useRef } from 'react';
import { useTicketSubmit } from '../hooks/useTicketSubmit';
import TicketForm from '../components/TicketForm';
import ResponsePanel from '../components/ResponsePanel';
import SourcesPanel from '../components/SourcesPanel';
import ConfidenceBar from '../components/ConfidenceBar';
import EscalationBanner from '../components/EscalationBanner';
import FeedbackPanel from '../components/FeedbackPanel';
import ContactCard from '../components/ContactCard';
import LandingHero from '../components/LandingHero';
import { RotateCcw } from 'lucide-react';
import { Button } from '../components/ui/button';

/**
 * Home page: Landing hero → Ticket submission → Response display.
 */
export default function HomePage() {
  const { submit, isLoading, result, error, sessionId, reset, resetSession } =
    useTicketSubmit();
  const ticketRef = useRef(null);

  const scrollToTicket = () => {
    ticketRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Hero Section */}
      <LandingHero onScrollToTicket={scrollToTicket} />

      {/* Ticket Input */}
      <div ref={ticketRef}>
        <TicketForm
          onSubmit={submit}
          isLoading={isLoading}
          hasSession={!!sessionId}
        />
      </div>

      {/* Error State */}
      {error && (
        <div className="fade-in bg-red-950/30 border border-red-500/30 rounded-xl p-4 text-sm text-red-300">
          <p className="font-medium text-red-400 mb-1">Error</p>
          <p>{error}</p>
          <Button
            variant="ghost"
            size="sm"
            onClick={reset}
            className="mt-2 text-red-400 hover:text-red-300"
          >
            Try again
          </Button>
        </div>
      )}

      {/* Loading Skeleton */}
      {isLoading && (
        <div className="space-y-4">
          <div className="skeleton h-8 w-48 rounded-lg" />
          <div className="skeleton h-40 rounded-xl" />
          <div className="skeleton h-12 rounded-xl" />
        </div>
      )}

      {/* Result Display */}
      {result && !isLoading && (
        <div className="space-y-4 fade-in">
          {/* Session Controls */}
          {sessionId && (
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">
                Session: {sessionId.slice(0, 8)}...
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={resetSession}
                className="text-xs text-muted-foreground"
              >
                <RotateCcw className="w-3 h-3 mr-1" />
                New Session
              </Button>
            </div>
          )}

          {/* Escalation Banner */}
          {result.escalated && (
            <EscalationBanner reason={result.escalation_reason} />
          )}

          {/* Confidence Bar */}
          <ConfidenceBar
            score={result.confidence_score}
            processingTime={result.processing_time_ms}
          />

          {/* Draft Response */}
          <ResponsePanel response={result.draft_response} />

          {/* Department Contact Info */}
          <ContactCard
            routedSources={result.routed_sources}
            citedSources={result.cited_sources}
          />

          {/* Feedback / Rating */}
          <FeedbackPanel ticketId={result.ticket_id} />

          {/* Cited Sources */}
          <SourcesPanel sources={result.cited_sources} />

          {/* Routed Sources Info */}
          <div className="text-xs text-muted-foreground flex items-center gap-2 flex-wrap">
            <span>Searched:</span>
            {result.routed_sources.map((s) => (
              <span
                key={s}
                className="px-2 py-0.5 rounded-full bg-secondary text-muted-foreground"
              >
                {s.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

