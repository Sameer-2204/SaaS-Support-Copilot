import { useState } from 'react';
import { Star, ThumbsUp, ThumbsDown, Send, CheckCircle2 } from 'lucide-react';
import { Button } from './ui/button';
import { submitFeedback } from '../lib/api';

/**
 * FeedbackPanel — Allows customers to rate the copilot response and leave feedback.
 * Shows after a response is displayed, with star rating, helpful toggle, and optional comment.
 */
export default function FeedbackPanel({ ticketId }) {
  const [rating, setRating] = useState(0);
  const [hoveredStar, setHoveredStar] = useState(0);
  const [wasHelpful, setWasHelpful] = useState(null);
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);

  const ratingLabels = {
    1: 'Very Unsatisfied',
    2: 'Unsatisfied',
    3: 'Neutral',
    4: 'Satisfied',
    5: 'Very Satisfied',
  };

  const handleSubmit = async () => {
    if (rating === 0 || wasHelpful === null) return;

    setIsSubmitting(true);
    setError(null);

    try {
      await submitFeedback(ticketId, rating, wasHelpful, comment || null);
      setSubmitted(true);
    } catch (err) {
      if (err.response?.status === 409) {
        setError('Feedback already submitted for this ticket.');
      } else {
        setError('Failed to submit feedback. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // Success state
  if (submitted) {
    return (
      <div className="glass-card p-5 fade-in">
        <div className="flex items-center gap-3 text-emerald-400">
          <CheckCircle2 className="w-5 h-5" />
          <div>
            <p className="font-medium">Thank you for your feedback!</p>
            <p className="text-sm text-muted-foreground mt-0.5">
              Your response helps us improve our support quality.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card p-5 space-y-4 fade-in">
      <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
        <Star className="w-4 h-4 text-amber-400" />
        Rate this response
      </h3>

      {/* Star Rating */}
      <div className="space-y-1.5">
        <div className="flex items-center gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              onMouseEnter={() => setHoveredStar(star)}
              onMouseLeave={() => setHoveredStar(0)}
              onClick={() => setRating(star)}
              className="p-0.5 transition-transform hover:scale-110 focus:outline-none"
              aria-label={`Rate ${star} stars`}
            >
              <Star
                className={`w-6 h-6 transition-colors ${
                  star <= (hoveredStar || rating)
                    ? 'fill-amber-400 text-amber-400'
                    : 'text-muted-foreground/40'
                }`}
              />
            </button>
          ))}
          {(hoveredStar || rating) > 0 && (
            <span className="text-xs text-muted-foreground ml-2">
              {ratingLabels[hoveredStar || rating]}
            </span>
          )}
        </div>
      </div>

      {/* Was it helpful? */}
      <div className="space-y-1.5">
        <p className="text-xs text-muted-foreground">Did this resolve your issue?</p>
        <div className="flex gap-2">
          <button
            onClick={() => setWasHelpful(true)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-all ${
              wasHelpful === true
                ? 'bg-emerald-500/20 text-emerald-400 ring-1 ring-emerald-500/30'
                : 'bg-secondary/50 text-muted-foreground hover:bg-secondary'
            }`}
          >
            <ThumbsUp className="w-3.5 h-3.5" />
            Yes, it helped
          </button>
          <button
            onClick={() => setWasHelpful(false)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-all ${
              wasHelpful === false
                ? 'bg-red-500/20 text-red-400 ring-1 ring-red-500/30'
                : 'bg-secondary/50 text-muted-foreground hover:bg-secondary'
            }`}
          >
            <ThumbsDown className="w-3.5 h-3.5" />
            No, I need more help
          </button>
        </div>
      </div>

      {/* Optional Comment */}
      <div className="space-y-1.5">
        <label htmlFor="feedback-comment" className="text-xs text-muted-foreground">
          Additional feedback (optional)
        </label>
        <textarea
          id="feedback-comment"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Tell us how we can improve..."
          rows={2}
          maxLength={2000}
          className="w-full rounded-lg bg-secondary/40 border border-border/40 px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-1 focus:ring-primary/50 resize-none"
        />
      </div>

      {/* Error */}
      {error && (
        <p className="text-xs text-red-400">{error}</p>
      )}

      {/* Submit */}
      <div className="flex justify-end">
        <Button
          onClick={handleSubmit}
          disabled={rating === 0 || wasHelpful === null || isSubmitting}
          size="sm"
          className="gap-1.5"
        >
          <Send className="w-3.5 h-3.5" />
          {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
        </Button>
      </div>
    </div>
  );
}
