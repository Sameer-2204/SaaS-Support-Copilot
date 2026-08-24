import { Card, CardContent } from './ui/card';
import { TrendingUp, AlertCircle, CheckCircle2, Gauge } from 'lucide-react';
import { getConfidenceColor } from '../lib/utils';

/**
 * Four stat cards for the dashboard: total tickets, auto-resolved, escalated, avg confidence.
 */
export default function DashboardStats({ stats }) {
  if (!stats) return null;

  const cards = [
    {
      title: 'Total Processed',
      value: stats.total_tickets,
      icon: TrendingUp,
      color: '#a78bfa',
      subtitle: 'tickets',
    },
    {
      title: 'Auto-Resolved',
      value: `${stats.auto_resolved_pct.toFixed(1)}%`,
      icon: CheckCircle2,
      color: '#22c55e',
      subtitle: `${stats.auto_resolved} tickets`,
    },
    {
      title: 'Escalated',
      value: `${stats.escalated_pct.toFixed(1)}%`,
      icon: AlertCircle,
      color: '#f59e0b',
      subtitle: `${stats.escalated} tickets`,
    },
    {
      title: 'Avg Confidence',
      value: `${(stats.avg_confidence * 100).toFixed(0)}%`,
      icon: Gauge,
      color: getConfidenceColor(stats.avg_confidence),
      subtitle: `${stats.avg_processing_time_ms.toFixed(0)}ms avg`,
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <Card key={card.title} className="hover:border-border/80 transition-colors">
          <CardContent className="p-5">
            <div className="flex items-start justify-between">
              <div className="space-y-2">
                <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider">
                  {card.title}
                </p>
                <p className="text-3xl font-bold" style={{ color: card.color }}>
                  {card.value}
                </p>
                <p className="text-xs text-muted-foreground">{card.subtitle}</p>
              </div>
              <div
                className="p-2 rounded-lg"
                style={{ backgroundColor: `${card.color}15` }}
              >
                <card.icon className="w-5 h-5" style={{ color: card.color }} />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
