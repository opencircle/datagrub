import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  children: React.ReactNode;
  footer?: React.ReactNode;
  showCloseButton?: boolean;
}

// Updated size classes following Modal Design System standards
const sizeClasses = {
  sm: '32rem',  // 512px
  md: '48rem',  // 768px
  lg: '56rem',  // 896px - matches TraceDetailModal
  xl: '72rem',  // 1152px
  full: '95vw',
};

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  size = 'md',
  children,
  footer,
  showCloseButton = true,
}) => {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  // Modal content following Modal Design System standards
  const modalContent = (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop - Design System: 60% opacity, 8px blur */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            style={{
              position: 'fixed',
              inset: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.6)',
              backdropFilter: 'blur(8px)',
              zIndex: 9999
            }}
          />

          {/* Modal Container - Design System: Centered, generous spacing */}
          <div
            style={{
              position: 'fixed',
              inset: 0,
              zIndex: 9999,
              display: 'flex',
              minHeight: '100%',
              alignItems: 'flex-start',
              justifyContent: 'center',
              padding: '3rem 1rem 2rem 1rem'
            }}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ duration: 0.2 }}
              onClick={(e) => e.stopPropagation()}
              style={{
                position: 'relative',
                width: '100%',
                maxWidth: sizeClasses[size],
                backgroundColor: 'white',
                borderRadius: '1rem',
                boxShadow: '0 20px 40px -8px rgba(0, 0, 0, 0.15), 0 8px 16px -4px rgba(0, 0, 0, 0.08)',
                maxHeight: '90vh',
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden'
              }}
            >
              {/* Header - Design System: 2rem 3rem padding */}
              <div
                className="flex items-center justify-between border-b border-neutral-200 bg-white rounded-t-2xl sticky top-0 z-10"
                style={{ padding: '2rem 3rem' }}
              >
                <h2 className="text-2xl font-semibold text-neutral-900">
                  {title}
                </h2>
                {showCloseButton && (
                  <button
                    onClick={onClose}
                    className="text-neutral-500 hover:text-neutral-700 transition-all duration-200 rounded-xl p-2.5 hover:bg-neutral-100"
                    aria-label="Close modal"
                  >
                    <X className="h-5 w-5" />
                  </button>
                )}
              </div>

              {/* Content - Design System: 3rem padding */}
              <div
                className="flex-1 overflow-y-auto"
                style={{ padding: '3rem' }}
              >
                {children}
              </div>

              {/* Footer - Design System: Consistent padding */}
              {footer && (
                <div
                  className="border-t border-neutral-200 bg-neutral-50"
                  style={{ padding: '1.5rem 3rem' }}
                >
                  {footer}
                </div>
              )}
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );

  // Render in portal to escape stacking contexts
  return createPortal(modalContent, document.body);
};
