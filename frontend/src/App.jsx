import { Routes, Route, NavLink } from 'react-router-dom';
import { MessageSquare, BarChart3, Orbit, HelpCircle, BookOpen } from 'lucide-react';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import VisualizerPage from './pages/VisualizerPage';
import FaqPage from './pages/FaqPage';
import TutorialsPage from './pages/TutorialsPage';
import Footer from './components/Footer';

function Navbar() {
  const linkClass = ({ isActive }) =>
    `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
      isActive
        ? 'bg-primary/20 text-primary-foreground shadow-sm'
        : 'text-muted-foreground hover:text-foreground hover:bg-secondary/50'
    }`;

  return (
    <nav className="border-b border-border/40 bg-background/80 backdrop-blur-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
            <MessageSquare className="w-4 h-4 text-white" />
          </div>
          <span className="font-semibold text-lg gradient-text">Support Copilot</span>
        </div>
        <div className="flex items-center gap-1">
          <NavLink to="/" className={linkClass}>
            <MessageSquare className="w-4 h-4" />
            Tickets
          </NavLink>
          <NavLink to="/faq" className={linkClass}>
            <HelpCircle className="w-4 h-4" />
            FAQ
          </NavLink>
          <NavLink to="/tutorials" className={linkClass}>
            <BookOpen className="w-4 h-4" />
            Tutorials
          </NavLink>
          <NavLink to="/dashboard" className={linkClass}>
            <BarChart3 className="w-4 h-4" />
            Dashboard
          </NavLink>
          <NavLink to="/visualizer" className={linkClass}>
            <Orbit className="w-4 h-4" />
            Embeddings
          </NavLink>
        </div>
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      <main className="max-w-7xl mx-auto px-6 py-8 flex-1 w-full">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/faq" element={<FaqPage />} />
          <Route path="/tutorials" element={<TutorialsPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/visualizer" element={<VisualizerPage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

