import { ValidatorFn } from '@angular/forms';

export interface FormFieldConfig {
  name: string;
  type: 'text' | 'select' | 'autocomplete' | 'number';
  validators?: ValidatorFn[];
}
