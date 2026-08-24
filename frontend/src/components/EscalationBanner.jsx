import { AlertTriangle } from 'lucide-react';

/**
 * Warning banner displayed when a ticket is escalated for human review.
 */
export default function EscalationBanner({ reason }) {
  return (
    <div className="fade-in bg-amber-950/40 border border-amber-500/30 rounded-xl p-4 flex items-start gap-3">
      <div className="mt-0.5 p-1.5 rounded-lg bg-amber-500/20">
        <AlertTriangle className="w-4 h-4 text-amber-400" />
      </div>
      <div className="space-y-1">
        <p className="font-semibold text-amber-300 text-sm">
          Escalated for Human Review
        </p>
        <p className="text-xs text-amber-400/70 leading-relaxed">
          {reason ||
            'This ticket has low retrieval confidence and has been flagged for manual review. A draft response is provided below for reference.'}
        </p>
      </div>
    </div>
  );
}
