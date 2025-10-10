import React from 'react';
import { FewShotExample } from '../../types/prompt';
import { Button } from '../../../../shared/components/core/Button';
import { Textarea } from '../../../../shared/components/forms/Textarea';

interface FewShotExamplesProps {
  examples: FewShotExample[];
  onChange: (examples: FewShotExample[]) => void;
}

export const FewShotExamples: React.FC<FewShotExamplesProps> = ({ examples, onChange }) => {
  const addExample = () => {
    const newExample: FewShotExample = {
      id: `example-${Date.now()}-${Math.random()}`,
      input: '',
      output: '',
    };
    onChange([...examples, newExample]);
  };

  const removeExample = (id: string) => {
    onChange(examples.filter((ex) => ex.id !== id));
  };

  const updateExample = (id: string, field: 'input' | 'output', value: string) => {
    const updated = examples.map((ex) =>
      ex.id === id ? { ...ex, [field]: value } : ex
    );
    onChange(updated);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Few-Shot Examples</h3>
          <p className="text-sm text-gray-600 mt-1">
            Provide example inputs and outputs to guide the model's behavior
          </p>
        </div>
        <Button variant="secondary" size="sm" onClick={addExample}>
          Add Example
        </Button>
      </div>

      {examples.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No examples defined. Click "Add Example" to create one.
        </div>
      ) : (
        <div className="space-y-6">
          {examples.map((example, index) => (
            <div
              key={example.id}
              className="border border-gray-200 rounded-lg p-4 space-y-3 bg-gray-50"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  Example {index + 1}
                </span>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => removeExample(example.id)}
                >
                  Remove
                </Button>
              </div>

              <Textarea
                label="Input"
                value={example.input}
                onChange={(e) => updateExample(example.id, 'input', e.target.value)}
                placeholder="Example input to the model..."
                rows={3}
                required
              />

              <Textarea
                label="Output"
                value={example.output}
                onChange={(e) => updateExample(example.id, 'output', e.target.value)}
                placeholder="Expected output from the model..."
                rows={3}
                required
              />
            </div>
          ))}
        </div>
      )}

      {examples.length > 0 && (
        <div className="text-xs text-gray-500 mt-2">
          {examples.length} example{examples.length !== 1 ? 's' : ''} defined
        </div>
      )}
    </div>
  );
};
