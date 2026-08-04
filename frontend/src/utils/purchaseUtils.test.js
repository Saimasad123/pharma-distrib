import test from 'node:test';
import assert from 'node:assert/strict';

import { formatCurrency, getPurchaseStatusClass } from './purchaseUtils.js';

test('formatCurrency formats amounts with rupee prefix', () => {
  assert.equal(formatCurrency(1250.5), 'Rs. 1,250.50');
  assert.equal(formatCurrency(0), 'Rs. 0.00');
});

test('getPurchaseStatusClass maps statuses correctly', () => {
  assert.equal(getPurchaseStatusClass('RECEIVED'), 'status-badge status-confirmed');
  assert.equal(getPurchaseStatusClass('PENDING'), 'status-badge status-pending');
});
