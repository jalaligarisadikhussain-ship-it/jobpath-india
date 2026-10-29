import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const read = path => readFileSync(new URL('../' + path, import.meta.url), 'utf8');
test('GA4 is optional, consent-controlled and configured for JobPath India', () => {
  const analytics = read('assets/js/analytics.mjs');
  assert.match(analytics, /G-HFKPWNKDBY/);
  assert.match(analytics, /currentChoice\(\) === 'allow'/);
  assert.match(analytics, /data-analytics-allow/);
  assert.match(analytics, /data-analytics-decline/);
  assert.match(analytics, /googletagmanager\.com\/gtag\/js/);
  assert.match(read('scripts/build_final.py'), /assets\/js\/analytics\.mjs/);
  assert.match(read('assets/js/app.mjs'), /data-analytics-choices/);
  assert.match(read('assets/js/app.mjs'), /Google Analytics 4/);
});
