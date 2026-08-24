import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { TrendingUp } from 'lucide-react';

/**
 * Line chart showing average confidence score over time.
 * Includes a reference line at the escalation threshold (0.45).
 */
export default function ConfidenceOverTimeChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center text-muted-foreground text-sm">
          No confidence data available yet.
        </CardContent>
      </Card>
    );
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass-card p-3 text-xs space-y-1">
          <p className="text-muted-foreground">{label}</p>
          <p className="text-violet-400 font-medium">
            Confidence: {(payload[0].value * 100).toFixed(1)}%
          </p>
          {payload[0].payload.count && (
            <p className="text-muted-foreground">
              {payload[0].payload.count} tickets
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base">
          <TrendingUp className="w-4 h-4 text-primary" />
          Confidence Over Time
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(240 3.7% 15.9%)" />
            <XAxis
              dataKey="date"
              tick={{ fill: '#94a3b8', fontSize: 11 }}
              axisLine={{ stroke: 'hsl(240 3.7% 15.9%)' }}
            />
            <YAxis
              domain={[0, 1]}
              tick={{ fill: '#94a3b8', fontSize: 11 }}
              axisLine={{ stroke: 'hsl(240 3.7% 15.9%)' }}
              tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine
              y={0.45}
              stroke="#f59e0b"
              strokeDasharray="6 4"
              label={{
                value: 'Escalation threshold',
                fill: '#f59e0b',
                fontSize: 10,
                position: 'right',
              }}
            />
            <Line
              type="monotone"
              dataKey="avg_confidence"
              stroke="#8b5cf6"
              strokeWidth={2}
              dot={{ fill: '#8b5cf6', r: 3 }}
              activeDot={{ r: 5, fill: '#a78bfa' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
