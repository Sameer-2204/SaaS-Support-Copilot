import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merge Tailwind classes with clsx for conditional class composition.
 * Used by shadcn/ui components.
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

/**
 * Format a confidence score as a colored label.
 */
export function getConfidenceColor(score) {
  if (score >= 0.7) return '#22c55e';   // green
  if (score >= 0.45) return '#eab308';  // yellow
  return '#ef4444';                      // red
}

/**
 * Format a confidence score as a human-readable label.
 */
export function getConfidenceLabel(score) {
  if (score >= 0.7) return 'High';
  if (score >= 0.45) return 'Medium';
  return 'Low';
}

/**
 * Get the badge color for a source type.
 */
export function getSourceTypeColor(sourceType) {
  const colors = {
    product_docs: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    resolved_ticket: 'bg-green-500/20 text-green-400 border-green-500/30',
    changelog: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    api_error: 'bg-red-500/20 text-red-400 border-red-500/30',
  };
  return colors[sourceType] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
}

/**
 * Get a human-readable label for a source type.
 */
export function getSourceTypeLabel(sourceType) {
  const labels = {
    product_docs: 'Documentation',
    resolved_ticket: 'Past Ticket',
    changelog: 'Changelog',
    api_error: 'API Error Ref',
  };
  return labels[sourceType] || sourceType;
}
