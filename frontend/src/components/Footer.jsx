import { Github, ExternalLink, Heart } from 'lucide-react';

/**
 * Footer — Minimal, elegant footer with links and tech stack info.
 */
export default function Footer() {
  return (
    <footer className="border-t border-border/30 mt-16">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-md bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
                <span className="text-white text-xs font-bold">S</span>
              </div>
              <span className="font-semibold text-sm gradient-text">
                Support Copilot
              </span>
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              AI-powered e-commerce support automation built with
              RAG, LangGraph, and hybrid search.
            </p>
          </div>

          {/* Tech Stack */}
          <div className="space-y-3">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Tech Stack
            </p>
            <div className="flex flex-wrap gap-1.5">
              {[
                'FastAPI', 'LangGraph', 'Groq', 'pgvector',
                'React', 'Vite', 'TailwindCSS',
              ].map((tech) => (
                <span
                  key={tech}
                  className="px-2 py-0.5 rounded text-[10px] bg-secondary/40 text-muted-foreground border border-border/20"
                >
                  {tech}
                </span>
              ))}
            </div>
          </div>

          {/* Links */}
          <div className="space-y-3">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Links
            </p>
            <div className="flex flex-col gap-2">
              <a
                href="#"
                className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                <Github className="w-3.5 h-3.5" />
                View Source on GitHub
              </a>
              <a
                href="#"
                className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                API Documentation
              </a>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-8 pt-4 border-t border-border/20 flex items-center justify-between">
          <p className="text-[10px] text-muted-foreground/60">
            © {new Date().getFullYear()} Support Copilot — Portfolio Project
          </p>
          <p className="text-[10px] text-muted-foreground/60 flex items-center gap-1">
            Built with <Heart className="w-2.5 h-2.5 text-red-400" /> using AI
          </p>
        </div>
      </div>
    </footer>
  );
}
