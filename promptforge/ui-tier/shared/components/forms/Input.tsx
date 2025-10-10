import React, { forwardRef } from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helpText?: string;
  icon?: React.ReactNode;
}

// Design System: Airbnb-inspired input fields with clean aesthetics
export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helpText, icon, className = '', ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-semibold text-neutral-700 mb-2">
            {label}
            {props.required && <span className="text-[#C13515] ml-1">*</span>}
          </label>
        )}
        <div className="relative">
          {icon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-500">
              {icon}
            </div>
          )}
          <input
            ref={ref}
            className={`
              ${className}
              ${icon ? 'pl-10' : 'pl-3'}
              ${error
                ? 'border-[#C13515] focus:ring-[#C13515]/20 focus:border-[#C13515]'
                : 'border-neutral-300 focus:ring-[#FF385C]/20 focus:border-[#FF385C]'
              }
              w-full pr-3 h-10 rounded-xl
              bg-white
              text-neutral-700 text-base
              border
              focus:outline-none focus:ring-4
              disabled:bg-neutral-100 disabled:text-neutral-500 disabled:cursor-not-allowed
              transition-all duration-200
              placeholder:text-neutral-400
            `}
            {...props}
          />
        </div>
        {error && (
          <p className="mt-2 text-sm text-[#C13515] font-medium">{error}</p>
        )}
        {helpText && !error && (
          <p className="mt-2 text-sm text-neutral-500">{helpText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
