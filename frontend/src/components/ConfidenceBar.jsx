import { getConfidenceColor, getConfidenceLabel } from '../lib/utils';
import { Shield } from 'lucide-react';

/**
 * Animated confidence score bar with color interpolation.
 * Green ≥ 0.7 | Yellow 0.45–0.7 | Red < 0.45
 */
export default function ConfidenceBar({ score, processingTime }) {
  const pct = Math.round(score * 100);
  const color = getConfidenceColor(score);
  const label = getConfidenceLabel(score);

  return (
    <div className="glass-card p-4 rounded-xl space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4" style={{ color }} />
          <span className="text-sm font-medium">Confidence</span>
        </div>
        <div className="flex items-center gap-3">
          {processingTime && (
            <span className="text-xs text-muted-foreground">
              {processingTime.toFixed(0)}ms
            </span>
          )}
          <span
            className="text-sm font-semibold px-2 py-0.5 rounded-md"
            style={{ color, backgroundColor: `${color}15` }}
          >
            {label} — {pct}%
          </span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="h-2.5 bg-secondary rounded-full overflow-hidden">
        <div
          className="h-full rounded-full confidence-fill"
          style={{
            width: `${pct}%`,
            backgroundColor: color,
            boxShadow: `0 0 12px ${color}40`,
          }}
        />
      </div>
    </div>
  );
}
