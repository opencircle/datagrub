import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '../../../../shared/components/core/Button';
import { Select } from '../../../../shared/components/forms/Select';

export interface PaginationProps {
  currentPage: number;
  totalCount: number;
  rowsPerPage: number;
  onPageChange: (page: number) => void;
  onRowsPerPageChange: (rowsPerPage: number) => void;
}

const ROWS_PER_PAGE_OPTIONS = [
  { value: '10', label: '10 per page' },
  { value: '20', label: '20 per page' },
  { value: '50', label: '50 per page' },
  { value: '100', label: '100 per page' },
];

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalCount,
  rowsPerPage,
  onPageChange,
  onRowsPerPageChange,
}) => {
  const totalPages = Math.ceil(totalCount / rowsPerPage);
  const startIndex = (currentPage - 1) * rowsPerPage + 1;
  const endIndex = Math.min(currentPage * rowsPerPage, totalCount);

  const handlePrevious = () => {
    if (currentPage > 1) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1);
    }
  };

  const handleRowsPerPageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newRowsPerPage = parseInt(e.target.value, 10);
    onRowsPerPageChange(newRowsPerPage);
    // Reset to page 1 when changing rows per page
    onPageChange(1);
  };

  return (
    <div className="flex flex-col gap-3 px-4 py-4 bg-white border-t border-neutral-200 md:flex-row md:items-center md:justify-between md:px-6">
      {/* Info Text */}
      <div className="text-sm text-neutral-600 font-medium text-center md:text-left">
        {totalCount > 0 ? (
          <>
            Showing {startIndex}-{endIndex} of {totalCount}
          </>
        ) : (
          'No results'
        )}
      </div>

      {/* Controls */}
      <div className="flex flex-col gap-3 md:flex-row md:items-center">
        <div className="flex gap-3">
          {/* Previous Button */}
          <Button
            variant="secondary"
            size="md"
            onClick={handlePrevious}
            disabled={currentPage === 1}
            aria-label="Go to previous page"
            aria-disabled={currentPage === 1}
            className="flex-1 md:flex-none"
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Button>

          {/* Next Button */}
          <Button
            variant="secondary"
            size="md"
            onClick={handleNext}
            disabled={currentPage === totalPages || totalCount === 0}
            aria-label="Go to next page"
            aria-disabled={currentPage === totalPages}
            className="flex-1 md:flex-none"
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>

        {/* Rows Per Page */}
        <Select
          value={rowsPerPage.toString()}
          onChange={handleRowsPerPageChange}
          options={ROWS_PER_PAGE_OPTIONS}
          className="w-full md:w-32"
          aria-label="Rows per page"
        />
      </div>
    </div>
  );
};
