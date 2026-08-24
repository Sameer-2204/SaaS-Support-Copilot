import { useState } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Send, Loader2 } from 'lucide-react';

/**
 * Ticket submission form with validation and loading state.
 */
export default function TicketForm({ onSubmit, isLoading, hasSession }) {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim().length >= 10 && !isLoading) {
      onSubmit(text.trim());
      // Don't clear — keep the query visible alongside the response
    }
  };

  const charCount = text.trim().length;
  const isValid = charCount >= 10;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="relative">
        <Textarea
          id="ticket-input"
          placeholder={
            hasSession
              ? 'Ask a follow-up question...'
              : 'Describe your support issue in detail...'
          }
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={5}
          className="w-full pr-4 text-base"
          disabled={isLoading}
        />
        <span
          className={`absolute bottom-3 right-3 text-xs ${
            isValid ? 'text-muted-foreground' : 'text-red-400'
          }`}
        >
          {charCount} / 10 min
        </span>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">
          {hasSession && '🔗 Follow-up mode active — using conversation context'}
        </p>
        <Button
          type="submit"
          disabled={isLoading || !isValid}
          size="lg"
          className="min-w-[160px]"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Send className="w-4 h-4 mr-2" />
              Submit Ticket
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
