import React from 'react';
import { Variable } from '../../types/prompt';
import { Button } from '../../../../shared/components/core/Button';
import { Input } from '../../../../shared/components/forms/Input';
import { Select } from '../../../../shared/components/forms/Select';

interface VariableEditorProps {
  variables: Variable[];
  onChange: (variables: Variable[]) => void;
}

export const VariableEditor: React.FC<VariableEditorProps> = ({ variables, onChange }) => {
  const addVariable = () => {
    const newVariable: Variable = {
      name: '',
      type: 'string',
      required: false,
      description: '',
    };
    onChange([...variables, newVariable]);
  };

  const removeVariable = (index: number) => {
    onChange(variables.filter((_, i) => i !== index));
  };

  const updateVariable = (index: number, field: keyof Variable, value: any) => {
    const updated = [...variables];
    updated[index] = { ...updated[index], [field]: value };
    onChange(updated);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Variables</h3>
        <Button variant="secondary" size="sm" onClick={addVariable}>
          Add Variable
        </Button>
      </div>

      {variables.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No variables defined. Click "Add Variable" to create one.
        </div>
      ) : (
        <div className="space-y-4">
          {variables.map((variable, index) => (
            <div
              key={index}
              className="border border-gray-200 rounded-lg p-4 space-y-3 bg-gray-50"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <Input
                  label="Variable Name"
                  value={variable.name}
                  onChange={(e) => updateVariable(index, 'name', e.target.value)}
                  placeholder="e.g., user_query, context"
                  required
                />
                <Select
                  label="Type"
                  value={variable.type}
                  onChange={(e) => updateVariable(index, 'type', e.target.value as Variable['type'])}
                  options={[
                    { value: 'string', label: 'String' },
                    { value: 'number', label: 'Number' },
                    { value: 'boolean', label: 'Boolean' },
                  ]}
                />
              </div>

              <Input
                label="Description (optional)"
                value={variable.description || ''}
                onChange={(e) => updateVariable(index, 'description', e.target.value)}
                placeholder="Describe this variable's purpose"
              />

              <div className="flex items-center justify-between">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={variable.required}
                    onChange={(e) => updateVariable(index, 'required', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">Required</span>
                </label>

                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => removeVariable(index)}
                >
                  Remove
                </Button>
              </div>

              {variable.type !== 'boolean' && (
                <Input
                  label="Default Value (optional)"
                  value={variable.defaultValue || ''}
                  onChange={(e) => updateVariable(index, 'defaultValue', e.target.value)}
                  type={variable.type === 'number' ? 'number' : 'text'}
                  placeholder={`Default ${variable.type} value`}
                />
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
