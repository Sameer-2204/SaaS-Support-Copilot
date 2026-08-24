import { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Orbit, Loader2 } from 'lucide-react';
import { getUmapData } from '../lib/api';

const SOURCE_COLORS = {
  product_docs: '#3b82f6',
  resolved_ticket: '#22c55e',
  changelog: '#f59e0b',
  api_error: '#ef4444',
};

const SOURCE_LABELS = {
  product_docs: 'Documentation',
  resolved_ticket: 'Past Tickets',
  changelog: 'Changelogs',
  api_error: 'API Errors',
};

/**
 * Interactive UMAP scatter plot of document embeddings, colored by source type.
 * Uses Plotly.js for WebGL-accelerated rendering with hover labels.
 */
export default function UmapVisualization() {
  const [points, setPoints] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await getUmapData();
        setPoints(data.points);
      } catch (err) {
        setError(err.message || 'Failed to load UMAP data');
      } finally {
        setIsLoading(false);
      }
    }
    fetchData();
  }, []);

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-16 flex flex-col items-center justify-center gap-3">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
          <p className="text-sm text-muted-foreground">
            Computing UMAP projection...
          </p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-8 text-center text-red-400 text-sm">
          {error}
        </CardContent>
      </Card>
    );
  }

  if (!points || points.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center text-muted-foreground text-sm">
          No embedding data available. Ingest documents first.
        </CardContent>
      </Card>
    );
  }

  // Group points by source_type to create separate traces
  const sourceTypes = [...new Set(points.map((p) => p.source_type))];

  const traces = sourceTypes.map((st) => {
    const filtered = points.filter((p) => p.source_type === st);
    return {
      x: filtered.map((p) => p.x),
      y: filtered.map((p) => p.y),
      text: filtered.map(
        (p) => `${SOURCE_LABELS[st] || st}<br>${p.product}<br>${p.text_preview}`
      ),
      mode: 'markers',
      type: 'scattergl',
      name: SOURCE_LABELS[st] || st,
      marker: {
        color: SOURCE_COLORS[st] || '#6b7280',
        size: 5,
        opacity: 0.75,
        line: { width: 0 },
      },
      hoverinfo: 'text',
    };
  });

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base">
          <Orbit className="w-4 h-4 text-primary" />
          Embedding Space (UMAP Projection)
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0 overflow-hidden rounded-b-xl">
        <Plot
          data={traces}
          layout={{
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'hsl(240, 10%, 6%)',
            font: { color: '#94a3b8', size: 11 },
            margin: { l: 40, r: 20, t: 20, b: 40 },
            xaxis: {
              showgrid: false,
              zeroline: false,
              showticklabels: false,
              title: '',
            },
            yaxis: {
              showgrid: false,
              zeroline: false,
              showticklabels: false,
              title: '',
            },
            legend: {
              orientation: 'h',
              y: -0.1,
              x: 0.5,
              xanchor: 'center',
              font: { size: 11 },
            },
            hovermode: 'closest',
          }}
          config={{
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            displaylogo: false,
          }}
          style={{ width: '100%', height: '550px' }}
        />
      </CardContent>
    </Card>
  );
}
