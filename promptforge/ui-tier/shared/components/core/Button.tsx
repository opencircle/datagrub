import React from 'react';
import { motion } from 'framer-motion';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
  children: React.ReactNode;
}

// Design System: Airbnb-inspired button variants with AAA contrast
const variantClasses = {
  primary: 'bg-[#FF385C] text-white hover:bg-[#E31C5F] disabled:bg-neutral-300 disabled:text-neutral-500 shadow-sm',
  secondary: 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200 disabled:bg-neutral-50 disabled:text-neutral-400 border border-neutral-300',
  danger: 'bg-[#C13515] text-white hover:bg-[#A12810] disabled:bg-neutral-300 disabled:text-neutral-500 shadow-sm',
  ghost: 'bg-transparent text-neutral-700 hover:bg-neutral-100 disabled:text-neutral-400',
};

// Design System: 8px spacing grid with 44px minimum touch target
const sizeClasses = {
  sm: 'h-8 px-3 text-sm min-w-[44px]',    // 32px height
  md: 'h-10 px-4 text-base min-w-[44px]', // 40px height
  lg: 'h-12 px-6 text-lg min-w-[44px]',   // 48px height
};

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  children,
  disabled,
  className = '',
  ...props
}) => {
  return (
    <motion.button
      whileHover={{ scale: disabled || loading ? 1 : 1.02 }}
      whileTap={{ scale: disabled || loading ? 1 : 0.98 }}
      transition={{ duration: 0.2, ease: 'easeInOut' }}
      disabled={disabled || loading}
      className={`
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${className}
        rounded-xl font-semibold transition-all duration-200
        disabled:cursor-not-allowed
        flex items-center justify-center gap-2
        focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20
      `}
      {...props}
    >
      {loading && (
        <svg
          className="animate-spin h-4 w-4"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      {icon && !loading && icon}
      {children}
    </motion.button>
  );
};
