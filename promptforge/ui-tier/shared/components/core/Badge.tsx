import React from 'react';

export interface BadgeProps {
  variant: 'success' | 'warning' | 'error' | 'info' | 'neutral' | 'green' | 'yellow' | 'red' | 'blue' | 'purple' | 'orange' | 'gray';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

const variantClasses = {
  success: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
  error: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  info: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  neutral: 'bg-neutral-100 text-neutral-800 dark:bg-neutral-800 dark:text-neutral-300',
  green: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  yellow: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
  red: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  blue: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  purple: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
  orange: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
  gray: 'bg-neutral-100 text-neutral-800 dark:bg-neutral-800 dark:text-neutral-300',
};

const sizeClasses = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1.5 text-base',
};

export const Badge: React.FC<BadgeProps> = ({
  variant,
  size = 'md',
  icon,
  children,
  className = '',
}) => {
  return (
    <span
      className={`
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${className}
        inline-flex items-center gap-1 rounded-full font-medium
      `}
    >
      {icon}
      {children}
    </span>
  );
};
