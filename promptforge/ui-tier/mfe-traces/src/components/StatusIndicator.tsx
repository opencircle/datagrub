import React from 'react';

interface StatusIndicatorProps {
  status: 'success' | 'error' | 'timeout' | 'retry' | 'pending';
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status }) => {
  const config = {
    success: { color: 'text-green-700', label: 'Success' },
    error: { color: 'text-red-700', label: 'Error' },
    timeout: { color: 'text-amber-700', label: 'Timeout' },
    retry: { color: 'text-amber-700', label: 'Retry' },
    pending: { color: 'text-neutral-700', label: 'Pending' },
  };

  const { color, label } = config[status] || config.pending;

  return (
    <span className={`text-sm font-medium ${color}`}>
      {label}
    </span>
  );
};

export default StatusIndicator;
