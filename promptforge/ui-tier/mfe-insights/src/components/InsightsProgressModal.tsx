import React, { useState, useEffect } from 'react';
import { Sparkles, Loader2, CheckCircle2 } from 'lucide-react';

interface Props {
  isVisible: boolean;
}

/**
 * Insights Analysis Progress Modal
 *
 * Displays a visual progress tracker for the 3-stage DTA pipeline:
 * - Stage 1: Fact Extraction
 * - Stage 2: Reasoning & Insights
 * - Stage 3: Summary Synthesis
 *
 * Simulates progress through stages based on typical execution time (~30-45 seconds)
 */
export const InsightsProgressModal: React.FC<Props> = ({ isVisible }) => {
  const [currentStage, setCurrentStage] = useState<number>(0);

  // Progress simulation effect
  useEffect(() => {
    if (!isVisible) {
      setCurrentStage(0);
      return;
    }

    // Simulate progress through 3 stages over ~40 seconds
    const stageTimings = [0, 12000, 25000, 40000]; // Stage start times in ms
    const timers: NodeJS.Timeout[] = [];

    stageTimings.forEach((delay, index) => {
      const timer = setTimeout(() => {
        setCurrentStage(index);
      }, delay);
      timers.push(timer);
    });

    return () => {
      timers.forEach((timer) => clearTimeout(timer));
    };
  }, [isVisible]);

  if (!isVisible) {
    return null;
  }

  const stages = [
    { id: 0, label: 'Stage 1: Fact Extraction', emoji: '📋', description: 'Extracting verified facts and key details...' },
    { id: 1, label: 'Stage 2: Reasoning & Insights', emoji: '🧠', description: 'Generating actionable insights and patterns...' },
    { id: 2, label: 'Stage 3: Summary Synthesis', emoji: '📝', description: 'Creating concise summary of key points...' },
  ];

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4">
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-[#FF385C]/10 rounded-full mb-4">
            <Sparkles className="h-8 w-8 text-[#FF385C] animate-pulse" />
          </div>
          <h3 className="text-2xl font-bold text-neutral-800 mb-2">
            Analyzing Transcript
          </h3>
          <p className="text-sm text-neutral-600">
            Running 3-stage Dynamic Temperature Adjustment pipeline...
          </p>
        </div>

        {/* Stage Progress */}
        <div className="space-y-3 mb-6">
          {stages.map((stage) => (
            <div
              key={stage.id}
              className={`flex items-center gap-3 p-3 rounded-lg transition-all ${
                currentStage === stage.id
                  ? 'bg-[#FF385C]/10 border-2 border-[#FF385C]'
                  : currentStage > stage.id
                  ? 'bg-green-50 border-2 border-green-300'
                  : 'bg-neutral-50 border-2 border-neutral-200'
              }`}
            >
              <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-white">
                {currentStage > stage.id ? (
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                ) : currentStage === stage.id ? (
                  <Loader2 className="h-5 w-5 text-[#FF385C] animate-spin" />
                ) : (
                  <span className="text-lg">{stage.emoji}</span>
                )}
              </div>
              <div className="flex-1">
                <div
                  className={`text-sm font-semibold ${
                    currentStage === stage.id
                      ? 'text-[#FF385C]'
                      : currentStage > stage.id
                      ? 'text-green-700'
                      : 'text-neutral-600'
                  }`}
                >
                  {stage.label}
                </div>
                {currentStage === stage.id && (
                  <div className="text-xs text-neutral-500 mt-0.5">
                    {stage.description}
                  </div>
                )}
              </div>
              {currentStage === stage.id && (
                <div className="text-xs text-[#FF385C] font-semibold">
                  In Progress...
                </div>
              )}
              {currentStage > stage.id && (
                <div className="text-xs text-green-600 font-semibold">Complete</div>
              )}
            </div>
          ))}
        </div>

        {/* Progress Bar */}
        <div className="relative h-2 bg-neutral-200 rounded-full overflow-hidden">
          <div
            className="absolute inset-y-0 left-0 bg-gradient-to-r from-[#FF385C] to-pink-500 transition-all duration-1000 ease-linear"
            style={{ width: `${(currentStage / 2) * 100}%` }}
          />
        </div>

        <div className="mt-4 text-center text-xs text-neutral-500">
          This typically takes 30-45 seconds. Please wait...
        </div>
      </div>
    </div>
  );
};

export default InsightsProgressModal;
