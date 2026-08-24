import { useState, useEffect } from 'react';
import { Loader2, BarChart3 } from 'lucide-react';
import DashboardStats from '../components/DashboardStats';
import ConfidenceOverTimeChart from '../components/ConfidenceOverTimeChart';
import TicketCategoryChart from '../components/TicketCategoryChart';
import FeedbackInsights from '../components/FeedbackInsights';
import TicketHistoryTable from '../components/TicketHistoryTable';
import { getDashboardStats } from '../lib/api';

/**
 * Dashboard page: aggregate statistics, CSAT, confidence trend,
 * category distribution, feedback insights, and ticket history.
 */
export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchStats() {
      try {
        const data = await getDashboardStats();
        setStats(data);
      } catch (err) {
        setError(err.message || 'Failed to load dashboard stats');
      } finally {
        setIsLoading(false);
      }
    }
    fetchStats();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-24">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-950/30 border border-red-500/30 rounded-xl p-6 text-center text-red-300">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold gradient-text flex items-center gap-3">
          <BarChart3 className="w-8 h-8" />
          Dashboard
        </h1>
        <p className="text-muted-foreground">
          Performance metrics, customer satisfaction, and ticket analytics.
        </p>
      </div>

      {/* Stat Cards */}
      <DashboardStats stats={stats} />

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ConfidenceOverTimeChart data={stats?.confidence_over_time} />
        <TicketCategoryChart data={stats?.category_distribution} />
      </div>

      {/* Feedback + History Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <FeedbackInsights />
        <TicketHistoryTable />
      </div>
    </div>
  );
}

