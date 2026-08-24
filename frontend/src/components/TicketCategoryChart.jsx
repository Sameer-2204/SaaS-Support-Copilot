import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { PieChart as PieIcon } from 'lucide-react';
import { getSourceTypeLabel } from '../lib/utils';

const COLORS = {
  product_docs: '#3b82f6',
  resolved_ticket: '#22c55e',
  changelog: '#f59e0b',
  api_error: '#ef4444',
};

/**
 * Pie chart showing ticket distribution across source type categories.
 */
export default function TicketCategoryChart({ data }) {
  if (!data || Object.keys(data).length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center text-muted-foreground text-sm">
          No category data available yet.
        </CardContent>
      </Card>
    );
  }

  const chartData = Object.entries(data).map(([key, value]) => ({
    name: getSourceTypeLabel(key),
    value,
    color: COLORS[key] || '#6b7280',
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass-card p-3 text-xs space-y-1">
          <p className="font-medium" style={{ color: payload[0].payload.color }}>
            {payload[0].name}
          </p>
          <p className="text-muted-foreground">{payload[0].value} tickets</p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base">
          <PieIcon className="w-4 h-4 text-primary" />
          Ticket Categories
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={65}
              outerRadius={100}
              paddingAngle={4}
              dataKey="value"
              strokeWidth={0}
            >
              {chartData.map((entry, i) => (
                <Cell key={i} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend
              formatter={(value) => (
                <span className="text-xs text-muted-foreground">{value}</span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
