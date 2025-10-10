import React, { forwardRef } from 'react';

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helpText?: string;
}

// Design System: Airbnb-inspired textarea fields with clean aesthetics
export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, helpText, className = '', ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-semibold text-neutral-700 mb-2">
            {label}
            {props.required && <span className="text-[#C13515] ml-1" aria-label="required">*</span>}
          </label>
        )}
        <textarea
          ref={ref}
          className={`
            ${className}
            ${error
              ? 'border-[#C13515] focus:ring-[#C13515]/20 focus:border-[#C13515]'
              : 'border-neutral-300 focus:ring-[#FF385C]/20 focus:border-[#FF385C]'
            }
            w-full px-3 py-2.5 rounded-xl
            bg-white
            text-neutral-700 text-base leading-relaxed
            border
            focus:outline-none focus:ring-4
            disabled:bg-neutral-100 disabled:text-neutral-500 disabled:cursor-not-allowed
            transition-all duration-200
            resize-vertical
            min-h-[100px]
            placeholder:text-neutral-400
          `}
          {...props}
        />
        {error && (
          <p className="mt-2 text-sm text-[#C13515] font-medium" role="alert">{error}</p>
        )}
        {helpText && !error && (
          <p className="mt-2 text-sm text-neutral-500">{helpText}</p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';
