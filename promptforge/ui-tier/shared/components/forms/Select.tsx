import React, { forwardRef } from 'react';
import { ChevronDown } from 'lucide-react';

export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  helpText?: string;
  options: SelectOption[];
}

// Design System: Airbnb-inspired select fields with clean aesthetics
export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, helpText, options, className = '', ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-semibold text-neutral-700 mb-2">
            {label}
            {props.required && <span className="text-[#C13515] ml-1" aria-label="required">*</span>}
          </label>
        )}
        <div className="relative">
          <select
            ref={ref}
            className={`
              ${className}
              ${error
                ? 'border-[#C13515] focus:ring-[#C13515]/20 focus:border-[#C13515]'
                : 'border-neutral-300 focus:ring-[#FF385C]/20 focus:border-[#FF385C]'
              }
              w-full pl-3 pr-10 h-10 rounded-xl
              bg-white
              text-neutral-700 text-base
              border
              focus:outline-none focus:ring-4
              disabled:bg-neutral-100 disabled:text-neutral-500 disabled:cursor-not-allowed
              transition-all duration-200
              appearance-none
            `}
            {...props}
          >
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
            <ChevronDown className="w-4 h-4 text-neutral-400" />
          </div>
        </div>
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

Select.displayName = 'Select';
