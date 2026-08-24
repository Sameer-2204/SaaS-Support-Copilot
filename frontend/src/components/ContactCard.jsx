import { Mail, Phone, Clock, Building2, ChevronDown } from 'lucide-react';
import { useState, useEffect } from 'react';
import { getContactInfo } from '../lib/api';

/**
 * ContactCard — Displays department contact information relevant to the ticket.
 * Auto-detects the product from the response and shows the matching department.
 */
export default function ContactCard({ routedSources, citedSources }) {
  const [contact, setContact] = useState(null);
  const [detectedProduct, setDetectedProduct] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [loading, setLoading] = useState(false);

  // Detect the primary product from cited sources
  useEffect(() => {
    const products = (citedSources || [])
      .map((s) => s.product)
      .filter((p) => p && p !== 'unknown');

    if (products.length === 0) return;

    // Count occurrences and pick the most frequent
    const counts = {};
    products.forEach((p) => {
      counts[p] = (counts[p] || 0) + 1;
    });
    const topProduct = Object.entries(counts).sort((a, b) => b[1] - a[1])[0][0];
    setDetectedProduct(topProduct);
  }, [citedSources]);

  // Fetch contact info when product is detected
  useEffect(() => {
    if (!detectedProduct) return;

    setLoading(true);
    getContactInfo(detectedProduct)
      .then(setContact)
      .catch(() => setContact(null))
      .finally(() => setLoading(false));
  }, [detectedProduct]);

  if (!detectedProduct || loading || !contact) return null;

  const platformColors = {
    shopify: 'from-green-500/20 to-emerald-500/10 border-green-500/20',
    stripe: 'from-violet-500/20 to-purple-500/10 border-violet-500/20',
    twilio: 'from-red-500/20 to-rose-500/10 border-red-500/20',
    vercel: 'from-zinc-400/20 to-neutral-500/10 border-zinc-400/20',
  };

  const colorClass = platformColors[detectedProduct] || platformColors.vercel;

  return (
    <div className={`rounded-xl border bg-gradient-to-br ${colorClass} overflow-hidden fade-in`}>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-2">
          <Building2 className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-medium text-foreground">
            {contact.department}
          </span>
          <span className="text-xs text-muted-foreground">
            — Need more help? Contact our team
          </span>
        </div>
        <ChevronDown
          className={`w-4 h-4 text-muted-foreground transition-transform ${
            isExpanded ? 'rotate-180' : ''
          }`}
        />
      </button>

      {isExpanded && (
        <div className="px-4 pb-4 space-y-3 fade-in">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* Email */}
            <a
              href={`mailto:${contact.email}`}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-background/40 hover:bg-background/60 transition-colors group"
            >
              <Mail className="w-4 h-4 text-primary/70 group-hover:text-primary" />
              <div className="min-w-0">
                <p className="text-xs text-muted-foreground">Email</p>
                <p className="text-sm text-foreground truncate">{contact.email}</p>
              </div>
            </a>

            {/* Phone */}
            <a
              href={`tel:${contact.phone.replace(/\s/g, '')}`}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-background/40 hover:bg-background/60 transition-colors group"
            >
              <Phone className="w-4 h-4 text-primary/70 group-hover:text-primary" />
              <div className="min-w-0">
                <p className="text-xs text-muted-foreground">Phone</p>
                <p className="text-sm text-foreground">{contact.phone}</p>
              </div>
            </a>

            {/* Hours */}
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-background/40">
              <Clock className="w-4 h-4 text-primary/70 flex-shrink-0" />
              <div className="min-w-0">
                <p className="text-xs text-muted-foreground">Hours</p>
                <p className="text-sm text-foreground">{contact.hours}</p>
              </div>
            </div>
          </div>

          {/* Specialties */}
          <div className="flex flex-wrap gap-1.5">
            {contact.specialties.map((s) => (
              <span
                key={s}
                className="px-2 py-0.5 text-xs rounded-full bg-primary/10 text-primary/80"
              >
                {s}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
