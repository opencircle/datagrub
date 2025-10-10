import React from 'react';
import { Layers, FlaskConical, HelpCircle } from 'lucide-react';

interface SourceBadgeProps {
  source: string;
  className?: string;
}

const SourceBadge: React.FC<SourceBadgeProps> = ({ source, className = '' }) => {
  const getSourceConfig = (source: string) => {
    switch (source) {
      case 'Call Insights':
        return {
          icon: Layers,
          bgColor: 'bg-blue-100',
          textColor: 'text-blue-800',
          borderColor: 'border-blue-200',
          label: 'Insights',
        };
      case 'Playground':
        return {
          icon: FlaskConical,
          bgColor: 'bg-purple-100',
          textColor: 'text-purple-800',
          borderColor: 'border-purple-200',
          label: 'Playground',
        };
      default:
        return {
          icon: HelpCircle,
          bgColor: 'bg-gray-100',
          textColor: 'text-gray-800',
          borderColor: 'border-gray-200',
          label: 'Other',
        };
    }
  };

  const config = getSourceConfig(source);
  const Icon = config.icon;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border text-xs font-medium ${config.bgColor} ${config.textColor} ${config.borderColor} ${className}`}
      aria-label={`Trace source: ${config.label}`}
    >
      <Icon className="h-3 w-3" />
      {config.label}
    </span>
  );
};

export default SourceBadge;
