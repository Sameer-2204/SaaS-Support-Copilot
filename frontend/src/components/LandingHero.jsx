import { useNavigate } from 'react-router-dom';
import { MessageSquare, Zap, Shield, BookOpen, ArrowRight } from 'lucide-react';
import { Button } from './ui/button';

/**
 * LandingHero — Premium hero section for the homepage.
 * Animated gradient background, key features, and CTA buttons.
 */
export default function LandingHero({ onScrollToTicket }) {
  const navigate = useNavigate();

  const features = [
    {
      icon: Zap,
      title: 'AI-Powered Responses',
      desc: 'Instant, context-aware answers with cited sources from our knowledge base.',
      color: '#a78bfa',
    },
    {
      icon: Shield,
      title: 'Smart Escalation',
      desc: 'Low-confidence queries are automatically flagged for human review.',
      color: '#22c55e',
    },
    {
      icon: BookOpen,
      title: 'Self-Service FAQ',
      desc: 'Browse 20+ curated FAQs across all platforms before submitting a ticket.',
      color: '#38bdf8',
    },
  ];

  return (
    <div className="relative overflow-hidden">
      {/* Background Gradient Orbs */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-32 -left-32 w-96 h-96 rounded-full bg-violet-600/10 blur-[120px] animate-pulse" />
        <div className="absolute -bottom-32 -right-32 w-96 h-96 rounded-full bg-indigo-600/10 blur-[120px] animate-pulse" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 rounded-full bg-purple-600/5 blur-[100px]" />
      </div>

      <div className="max-w-4xl mx-auto text-center space-y-8 pt-8 pb-12">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-xs text-primary">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          Powered by RAG + LangGraph
        </div>

        {/* Heading */}
        <div className="space-y-4">
          <h1 className="text-5xl sm:text-6xl font-bold leading-tight">
            <span className="gradient-text">E-Commerce</span>
            <br />
            <span className="text-foreground">Support Copilot</span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            AI-powered support for{' '}
            <span className="text-foreground font-medium">Shopify</span>,{' '}
            <span className="text-foreground font-medium">Stripe</span>,{' '}
            <span className="text-foreground font-medium">Twilio</span> &{' '}
            <span className="text-foreground font-medium">Vercel</span>.
            Get instant, cited responses from 800+ knowledge base articles.
          </p>
        </div>

        {/* CTA Buttons */}
        <div className="flex items-center justify-center gap-3">
          <Button
            onClick={onScrollToTicket}
            size="lg"
            className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white shadow-lg shadow-violet-500/25 px-6 gap-2"
          >
            <MessageSquare className="w-4 h-4" />
            Submit a Ticket
          </Button>
          <Button
            onClick={() => navigate('/faq')}
            variant="outline"
            size="lg"
            className="gap-2 border-border/60"
          >
            Browse FAQ
            <ArrowRight className="w-4 h-4" />
          </Button>
        </div>

        {/* Platform Logos */}
        <div className="flex items-center justify-center gap-6 pt-2">
          {['Shopify', 'Stripe', 'Twilio', 'Vercel'].map((name) => (
            <div
              key={name}
              className="px-3 py-1.5 rounded-lg bg-secondary/30 border border-border/20 text-xs text-muted-foreground font-medium hover:bg-secondary/50 transition-colors"
            >
              {name}
            </div>
          ))}
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4">
          {features.map((f) => (
            <div
              key={f.title}
              className="glass-card p-5 text-left space-y-3 hover:border-primary/20 transition-all group"
            >
              <div
                className="w-9 h-9 rounded-lg flex items-center justify-center transition-transform group-hover:scale-110"
                style={{ backgroundColor: `${f.color}15` }}
              >
                <f.icon className="w-4.5 h-4.5" style={{ color: f.color }} />
              </div>
              <h3 className="text-sm font-semibold text-foreground">{f.title}</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
