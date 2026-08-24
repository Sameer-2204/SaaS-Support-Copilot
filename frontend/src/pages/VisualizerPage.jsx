import UmapVisualization from '../components/UmapVisualization';

/**
 * Visualizer page: UMAP embedding space explorer.
 */
export default function VisualizerPage() {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold gradient-text">Embedding Visualizer</h1>
        <p className="text-muted-foreground">
          UMAP projection of the document corpus. Each point is a chunk, colored by
          source type. Hover to see content previews.
        </p>
      </div>

      {/* UMAP Plot */}
      <UmapVisualization />
    </div>
  );
}
