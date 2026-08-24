import { useState, useEffect } from 'react';
import { Star, ThumbsUp, MessageSquare } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { getFeedbackSummary } from '../lib/api';

/**
 * FeedbackInsights — Dashboard panel showing CSAT metrics,
 * rating distribution bar chart, and recent feedback comments.
 */
export default function FeedbackInsights() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getFeedbackSummary()
      .then(setSummary)
      .catch(() => setSummary(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Card>
        <CardContent className="p-5">
          <div className="skeleton h-48 rounded-lg" />
        </CardContent>
      </Card>
    );
  }

  if (!summary || summary.total_feedback === 0) {
    return (
      <Card>
        <CardContent className="p-5 space-y-3">
          <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
            <Star className="w-4 h-4 text-amber-400" />
            Customer Satisfaction
          </h3>
          <div className="text-center py-6">
            <p className="text-sm text-muted-foreground">
              No feedback received yet. Feedback will appear here as customers rate responses.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const maxRating = Math.max(...Object.values(summary.rating_distribution), 1);

  // Star colors for the distribution bars
  const ratingColors = {
    '5': '#22c55e',
    '4': '#4ade80',
    '3': '#facc15',
    '2': '#fb923c',
    '1': '#ef4444',
  };

  return (
    <Card>
      <CardContent className="p-5 space-y-4">
        <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
          <Star className="w-4 h-4 text-amber-400" />
          Customer Satisfaction (CSAT)
        </h3>

        {/* Top-level metrics */}
        <div className="grid grid-cols-3 gap-3">
          <div className="text-center p-3 rounded-lg bg-secondary/30">
            <p className="text-2xl font-bold text-amber-400">
              {summary.avg_rating.toFixed(1)}
            </p>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wider mt-1">
              Avg Rating
            </p>
          </div>
          <div className="text-center p-3 rounded-lg bg-secondary/30">
            <p className="text-2xl font-bold text-emerald-400">
              {summary.satisfaction_rate}%
            </p>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wider mt-1">
              Helpful
            </p>
          </div>
          <div className="text-center p-3 rounded-lg bg-secondary/30">
            <p className="text-2xl font-bold text-primary">
              {summary.total_feedback}
            </p>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wider mt-1">
              Responses
            </p>
          </div>
        </div>

        {/* Rating Distribution */}
        <div className="space-y-1.5">
          <p className="text-xs text-muted-foreground font-medium">Rating Distribution</p>
          {['5', '4', '3', '2', '1'].map((rating) => {
            const count = summary.rating_distribution[rating] || 0;
            const pct = summary.total_feedback > 0
              ? (count / summary.total_feedback) * 100
              : 0;

            return (
              <div key={rating} className="flex items-center gap-2 text-xs">
                <span className="w-4 text-right text-muted-foreground">{rating}</span>
                <Star className="w-3 h-3" style={{ color: ratingColors[rating] }} />
                <div className="flex-1 h-4 bg-secondary/30 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{
                      width: `${pct}%`,
                      backgroundColor: ratingColors[rating],
                      minWidth: count > 0 ? '4px' : '0',
                    }}
                  />
                </div>
                <span className="w-8 text-right text-muted-foreground">{count}</span>
              </div>
            );
          })}
        </div>

        {/* Recent Feedback Comments */}
        {summary.recent_feedback.filter((f) => f.comment).length > 0 && (
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground font-medium flex items-center gap-1">
              <MessageSquare className="w-3 h-3" />
              Recent Comments
            </p>
            <div className="space-y-1.5 max-h-32 overflow-y-auto">
              {summary.recent_feedback
                .filter((f) => f.comment)
                .slice(0, 5)
                .map((f) => (
                  <div
                    key={f.feedback_id}
                    className="px-3 py-2 rounded-lg bg-secondary/20 text-xs"
                  >
                    <div className="flex items-center gap-1 mb-0.5">
                      {Array.from({ length: f.rating }, (_, i) => (
                        <Star
                          key={i}
                          className="w-2.5 h-2.5 fill-amber-400 text-amber-400"
                        />
                      ))}
                      {f.was_helpful && (
                        <ThumbsUp className="w-2.5 h-2.5 text-emerald-400 ml-1" />
                      )}
                    </div>
                    <p className="text-muted-foreground leading-snug">
                      {f.comment}
                    </p>
                  </div>
                ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
