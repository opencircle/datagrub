import React, { useRef } from 'react';
import { FileText, Upload, Shield } from 'lucide-react';
import type { InsightsFormState } from '../../types/insights';

interface Props {
  formState: InsightsFormState;
  setFormState: React.Dispatch<React.SetStateAction<InsightsFormState>>;
}

/**
 * Transcript Input Section
 *
 * Features:
 * - Large text area for transcript input
 * - File upload support (.txt, .docx)
 * - Character count
 * - PII redaction toggle
 * - Project selection
 */
export const TranscriptInputSection: React.FC<Props> = ({ formState, setFormState }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Only allow .txt files for now (docx would require additional library)
    if (!file.name.endsWith('.txt')) {
      alert('Only .txt files are supported');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      setFormState(prev => ({ ...prev, transcript: content }));
    };
    reader.readAsText(file);
  };

  const handleTranscriptChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setFormState(prev => ({ ...prev, transcript: e.target.value }));
  };

  const handlePiiToggle = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormState(prev => ({ ...prev, enablePiiRedaction: e.target.checked }));
  };

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormState(prev => ({ ...prev, transcriptTitle: e.target.value }));
  };

  const characterCount = formState.transcript.length;
  const isOverLimit = characterCount > 100000;
  const isUnderMinimum = characterCount > 0 && characterCount < 100;

  return (
    <div className="bg-white border border-neutral-200 rounded-xl p-6 space-y-5">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-[#FF385C]" />
          <h3 className="font-semibold text-neutral-700">Call Transcript</h3>
        </div>

        {/* File Upload Button */}
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className="flex items-center gap-2 text-sm text-[#FF385C] hover:text-[#E31C5F] font-semibold transition-colors"
        >
          <Upload className="h-4 w-4" />
          Upload File
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt"
          onChange={handleFileUpload}
          className="hidden"
        />
      </div>

      {/* Transcript Title (Required) */}
      <div>
        <label className="block text-sm font-semibold text-neutral-700 mb-2">
          Title <span className="text-[#FF385C]">*</span>
        </label>
        <input
          type="text"
          value={formState.transcriptTitle}
          onChange={handleTitleChange}
          placeholder="e.g., Q4 Earnings Call with ABC Corp"
          maxLength={500}
          className="w-full h-10 px-3 rounded-xl border border-neutral-300 text-neutral-700 focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/20 transition-all duration-200 placeholder:text-neutral-400"
        />
        <p className="mt-1 text-xs text-neutral-500">
          Give this analysis a descriptive title to identify it in history, traces, and evaluations.
        </p>
      </div>

      {/* Project ID (Optional) */}
      <div>
        <label className="block text-sm font-semibold text-neutral-700 mb-2">
          Project (Optional)
        </label>
        <input
          type="text"
          value={formState.projectId}
          onChange={(e) => setFormState(prev => ({ ...prev, projectId: e.target.value }))}
          placeholder="Enter project UUID to associate this analysis"
          className="w-full h-10 px-3 rounded-xl border border-neutral-300 text-neutral-700 focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/20 transition-all duration-200 placeholder:text-neutral-400"
        />
      </div>

      {/* Transcript Text Area */}
      <div>
        <label className="block text-sm font-semibold text-neutral-700 mb-2">
          Transcript Text
        </label>
        <textarea
          value={formState.transcript}
          onChange={handleTranscriptChange}
          placeholder="Paste your advisor-client call transcript here... (minimum 100 characters)"
          rows={12}
          className={`w-full px-3 py-3 rounded-xl border ${
            isOverLimit || isUnderMinimum
              ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20'
              : 'border-neutral-300 focus:border-[#FF385C] focus:ring-[#FF385C]/20'
          } text-neutral-700 focus:outline-none focus:ring-4 transition-all duration-200 resize-none placeholder:text-neutral-400 font-mono text-sm leading-relaxed`}
        />

        {/* Character Count */}
        <div className="flex items-center justify-between mt-2">
          <div className="text-xs text-neutral-500">
            {characterCount === 0 ? (
              'No transcript entered'
            ) : isUnderMinimum ? (
              <span className="text-orange-600 font-semibold">
                Minimum 100 characters required ({100 - characterCount} more needed)
              </span>
            ) : isOverLimit ? (
              <span className="text-red-600 font-semibold">
                Exceeds maximum length (100,000 characters)
              </span>
            ) : (
              <span className="text-green-600 font-semibold">
                {characterCount.toLocaleString()} characters
              </span>
            )}
          </div>

          {/* PII Redaction Toggle */}
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={formState.enablePiiRedaction}
              onChange={handlePiiToggle}
              className="w-4 h-4 accent-[#FF385C] rounded"
            />
            <div className="flex items-center gap-1.5 text-sm font-semibold text-neutral-700">
              <Shield className="h-4 w-4 text-green-600" />
              Enable PII Redaction
            </div>
          </label>
        </div>
      </div>

      {/* Help Text */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <div className="text-xs text-blue-700">
          <div className="font-semibold mb-1">Tips for best results:</div>
          <ul className="list-disc list-inside space-y-0.5 text-blue-600">
            <li>Provide complete conversation context (both advisor and client)</li>
            <li>Include timestamps if available for better structure</li>
            <li>Enable PII redaction if transcript contains sensitive information</li>
            <li>Minimum 100 characters, maximum 100,000 characters</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default TranscriptInputSection;
