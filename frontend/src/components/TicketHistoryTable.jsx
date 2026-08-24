import { useState, useEffect } from 'react';
import { Clock, AlertTriangle, CheckCircle2, ChevronLeft, ChevronRight } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { getTicketHistory } from '../lib/api';

/**
 * TicketHistoryTable — Paginated table of past ticket submissions
 * with status, confidence, and timing info.
 */
export default function TicketHistoryTable() {
  const [data, setData] = useState(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const limit = 10;

  const fetchPage = async (p) => {
    setLoading(true);
    try {
      const result = await getTicketHistory(p, limit);
      setData(result);
      setPage(p);
    } catch {
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPage(1);
  }, []);

  if (loading && !data) {
    return (
      <Card>
        <CardContent className="p-5">
          <div className="skeleton h-48 rounded-lg" />
        </CardContent>
      </Card>
    );
  }

  if (!data || data.items.length === 0) {
    return (
      <Card>
        <CardContent className="p-5 space-y-3">
          <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
            <Clock className="w-4 h-4 text-primary" />
            Ticket History
          </h3>
          <div className="text-center py-6">
            <p className="text-sm text-muted-foreground">
              No tickets processed yet. Submit a ticket to see it here.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const totalPages = Math.ceil(data.total / limit);

  const getConfidenceClass = (score) => {
    if (score >= 0.7) return 'text-emerald-400 bg-emerald-400/10';
    if (score >= 0.45) return 'text-amber-400 bg-amber-400/10';
    return 'text-red-400 bg-red-400/10';
  };

  return (
    <Card>
      <CardContent className="p-5 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
            <Clock className="w-4 h-4 text-primary" />
            Ticket History
          </h3>
          <span className="text-xs text-muted-foreground">
            {data.total} total
          </span>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-border/40">
                <th className="text-left py-2 px-2 text-muted-foreground font-medium">Ticket</th>
                <th className="text-center py-2 px-2 text-muted-foreground font-medium">Status</th>
                <th className="text-center py-2 px-2 text-muted-foreground font-medium">Confidence</th>
                <th className="text-right py-2 px-2 text-muted-foreground font-medium">Time</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((ticket) => (
                <tr
                  key={ticket.ticket_id}
                  className="border-b border-border/20 hover:bg-secondary/20 transition-colors"
                >
                  <td className="py-2.5 px-2 max-w-xs">
                    <p className="text-foreground truncate leading-snug">
                      {ticket.ticket_text}
                    </p>
                    <p className="text-[10px] text-muted-foreground/60 mt-0.5">
                      {new Date(ticket.created_at).toLocaleString()}
                    </p>
                  </td>
                  <td className="py-2.5 px-2 text-center">
                    {ticket.escalated ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-400/10 text-amber-400">
                        <AlertTriangle className="w-3 h-3" />
                        Escalated
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-400/10 text-emerald-400">
                        <CheckCircle2 className="w-3 h-3" />
                        Resolved
                      </span>
                    )}
                  </td>
                  <td className="py-2.5 px-2 text-center">
                    <span
                      className={`inline-block px-2 py-0.5 rounded-full font-medium ${getConfidenceClass(
                        ticket.confidence_score
                      )}`}
                    >
                      {(ticket.confidence_score * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td className="py-2.5 px-2 text-right text-muted-foreground">
                    {ticket.processing_time_ms.toFixed(0)}ms
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between pt-2">
            <span className="text-[10px] text-muted-foreground">
              Page {page} of {totalPages}
            </span>
            <div className="flex gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => fetchPage(page - 1)}
                disabled={page <= 1 || loading}
                className="h-7 w-7 p-0"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => fetchPage(page + 1)}
                disabled={page >= totalPages || loading}
                className="h-7 w-7 p-0"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
