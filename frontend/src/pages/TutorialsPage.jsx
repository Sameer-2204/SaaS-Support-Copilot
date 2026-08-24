import { useState } from 'react';
import { BookOpen, Clock, ChevronRight, ChevronLeft, CheckCircle2, ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui/button';
import tutorialsData from '../data/tutorials-data';

/**
 * TutorialsPage — Interactive step-by-step guides organized by platform.
 * Users can browse tutorials and walk through steps with progress tracking.
 */
export default function TutorialsPage() {
  const [selectedTutorial, setSelectedTutorial] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState(new Set());
  const [filterPlatform, setFilterPlatform] = useState(null);

  const platforms = [...new Set(tutorialsData.map((t) => t.platform))];

  const filteredTutorials = filterPlatform
    ? tutorialsData.filter((t) => t.platform === filterPlatform)
    : tutorialsData;

  const markStepComplete = (stepIdx) => {
    setCompletedSteps((prev) => new Set([...prev, `${selectedTutorial.id}-${stepIdx}`]));
  };

  const isStepComplete = (stepIdx) =>
    completedSteps.has(`${selectedTutorial?.id}-${stepIdx}`);

  const getDifficultyColor = (d) => {
    if (d === 'Beginner') return 'text-emerald-400 bg-emerald-400/10';
    if (d === 'Intermediate') return 'text-amber-400 bg-amber-400/10';
    return 'text-red-400 bg-red-400/10';
  };

  // Format step content with basic markdown
  const formatContent = (text) => {
    return text
      .split('\n')
      .map((line) => {
        line = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        line = line.replace(/`(.+?)`/g, '<code class="px-1 py-0.5 rounded bg-secondary text-xs font-mono">$1</code>');
        if (/^\d+\.\s/.test(line)) return `<div class="ml-4 mb-1">${line}</div>`;
        if (line.startsWith('- ')) return `<div class="ml-4 mb-1">• ${line.slice(2)}</div>`;
        if (line.trim() === '') return '<div class="h-2"></div>';
        return `<div class="mb-1">${line}</div>`;
      })
      .join('');
  };

  // Tutorial viewer (step-by-step)
  if (selectedTutorial) {
    const tutorial = selectedTutorial;
    const step = tutorial.steps[currentStep];
    const progress = ((currentStep + 1) / tutorial.steps.length) * 100;

    return (
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Back Button */}
        <button
          onClick={() => {
            setSelectedTutorial(null);
            setCurrentStep(0);
          }}
          className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to tutorials
        </button>

        {/* Tutorial Header */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-2xl">{tutorial.icon}</span>
            <h1 className="text-2xl font-bold text-foreground">{tutorial.title}</h1>
          </div>
          <div className="flex items-center gap-3 text-xs text-muted-foreground">
            <span className={`px-2 py-0.5 rounded-full ${getDifficultyColor(tutorial.difficulty)}`}>
              {tutorial.difficulty}
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {tutorial.estimatedTime}
            </span>
            <span>
              Step {currentStep + 1} of {tutorial.steps.length}
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="h-1.5 bg-secondary/40 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${progress}%`,
              backgroundColor: tutorial.color,
            }}
          />
        </div>

        {/* Step Navigation (mini dots) */}
        <div className="flex items-center gap-1.5 justify-center">
          {tutorial.steps.map((_, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentStep(idx)}
              className={`w-2.5 h-2.5 rounded-full transition-all ${
                idx === currentStep
                  ? 'scale-125'
                  : isStepComplete(idx)
                  ? 'opacity-80'
                  : 'opacity-30'
              }`}
              style={{
                backgroundColor:
                  idx === currentStep || isStepComplete(idx)
                    ? tutorial.color
                    : '#666',
              }}
            />
          ))}
        </div>

        {/* Step Content Card */}
        <div className="glass-card p-6 space-y-4 fade-in" key={currentStep}>
          <div className="flex items-center gap-2">
            <div
              className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-white"
              style={{ backgroundColor: tutorial.color }}
            >
              {isStepComplete(currentStep) ? (
                <CheckCircle2 className="w-4 h-4" />
              ) : (
                currentStep + 1
              )}
            </div>
            <h2 className="text-lg font-semibold text-foreground">{step.title}</h2>
          </div>

          <div
            className="text-sm text-muted-foreground leading-relaxed"
            dangerouslySetInnerHTML={{ __html: formatContent(step.content) }}
          />

          {/* Mark Complete */}
          {!isStepComplete(currentStep) && (
            <button
              onClick={() => markStepComplete(currentStep)}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-emerald-400 transition-colors"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              Mark as complete
            </button>
          )}
        </div>

        {/* Navigation Buttons */}
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentStep((s) => s - 1)}
            disabled={currentStep === 0}
            className="gap-1"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            Previous
          </Button>

          {currentStep < tutorial.steps.length - 1 ? (
            <Button
              size="sm"
              onClick={() => {
                markStepComplete(currentStep);
                setCurrentStep((s) => s + 1);
              }}
              className="gap-1"
              style={{ backgroundColor: tutorial.color }}
            >
              Next Step
              <ChevronRight className="w-3.5 h-3.5" />
            </Button>
          ) : (
            <Button
              size="sm"
              onClick={() => {
                markStepComplete(currentStep);
                setSelectedTutorial(null);
                setCurrentStep(0);
              }}
              className="gap-1 bg-emerald-600 hover:bg-emerald-500"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              Complete Tutorial
            </Button>
          )}
        </div>
      </div>
    );
  }

  // Tutorial listing
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold gradient-text flex items-center gap-3">
          <BookOpen className="w-8 h-8" />
          Tutorials & Guides
        </h1>
        <p className="text-muted-foreground">
          Step-by-step guides to help you get the most out of your tools.
        </p>
      </div>

      {/* Platform Filters */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setFilterPlatform(null)}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            filterPlatform === null
              ? 'bg-primary/20 text-primary ring-1 ring-primary/30'
              : 'bg-secondary/50 text-muted-foreground hover:bg-secondary'
          }`}
        >
          All Platforms
        </button>
        {platforms.map((p) => (
          <button
            key={p}
            onClick={() => setFilterPlatform(filterPlatform === p ? null : p)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              filterPlatform === p
                ? 'bg-primary/20 text-primary ring-1 ring-primary/30'
                : 'bg-secondary/50 text-muted-foreground hover:bg-secondary'
            }`}
          >
            {p}
          </button>
        ))}
      </div>

      {/* Tutorial Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {filteredTutorials.map((tutorial) => {
          const completedCount = tutorial.steps.filter((_, idx) =>
            completedSteps.has(`${tutorial.id}-${idx}`)
          ).length;
          const isCompleted = completedCount === tutorial.steps.length;

          return (
            <button
              key={tutorial.id}
              onClick={() => {
                setSelectedTutorial(tutorial);
                setCurrentStep(0);
              }}
              className="glass-card p-5 text-left space-y-3 hover:border-primary/20 transition-all group"
            >
              <div className="flex items-start justify-between">
                <span className="text-3xl">{tutorial.icon}</span>
                {isCompleted && (
                  <span className="text-xs text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" />
                    Done
                  </span>
                )}
              </div>
              <div>
                <h3 className="text-sm font-semibold text-foreground group-hover:text-primary transition-colors">
                  {tutorial.title}
                </h3>
                <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
                  {tutorial.description}
                </p>
              </div>
              <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                <span
                  className={`px-1.5 py-0.5 rounded-full ${getDifficultyColor(tutorial.difficulty)}`}
                >
                  {tutorial.difficulty}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-2.5 h-2.5" />
                  {tutorial.estimatedTime}
                </span>
                <span>{tutorial.steps.length} steps</span>
                {completedCount > 0 && !isCompleted && (
                  <span className="text-primary">
                    {completedCount}/{tutorial.steps.length} done
                  </span>
                )}
              </div>
              {/* Progress bar */}
              {completedCount > 0 && (
                <div className="h-1 bg-secondary/40 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: `${(completedCount / tutorial.steps.length) * 100}%`,
                      backgroundColor: tutorial.color,
                    }}
                  />
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
