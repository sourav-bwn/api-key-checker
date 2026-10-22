// Offline tests for js/checker.js. The DOM is stubbed before loading it.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);

const elementStub = () => ({
  addEventListener() {},
  appendChild() {},
  remove() {},
  classList: { add() {}, remove() {} },
  style: {},
  innerHTML: '',
  textContent: '',
  disabled: false,
  value: '',
});
globalThis.document = { getElementById: () => elementStub(), createElement: () => elementStub() };

const { PROVIDERS, pickProviders } = require('../js/checker.js');

const names = (key) => pickProviders(key).map((p) => p.name);

test('an Anthropic key matches only Anthropic', () => {
  // sk-ant- also starts with sk-; OpenAI/DeepSeek/Stability must not claim it.
  assert.deepEqual(names('sk-ant-api03-abcdef1234567890'), ['Anthropic']);
});

test('an OpenRouter key matches only OpenRouter', () => {
  assert.deepEqual(names('sk-or-v1-abcdef1234567890'), ['OpenRouter']);
});

test('a generic sk- key keeps the ambiguous providers', () => {
  const n = names('sk-abcdef1234567890abcdef');
  assert.ok(n.includes('OpenAI'));
  assert.ok(n.includes('DeepSeek'));
  assert.ok(!n.includes('Anthropic'));
});

test('other prefixes detect their single provider', () => {
  assert.deepEqual(names('gsk_abc'), ['Groq']);
  assert.deepEqual(names('AIzaSyabc'), ['Google Gemini']);
  assert.deepEqual(names('ghp_abc'), ['GitHub']);
  assert.deepEqual(names('nvapi-abc'), ['NVIDIA']);
  assert.deepEqual(names('zzz-nothing'), []);
});

test('Gemini validator rejects HTTP 400 (bad API key)', async () => {
  const gemini = PROVIDERS.find((p) => p.name === 'Google Gemini');
  assert.equal(await gemini.validate({ status: 400, ok: false }), false);
  assert.equal(await gemini.validate({ status: 200, ok: true }), true);
  assert.equal(await gemini.validate({ status: 429, ok: false }), true);
});

test('Replicate uses the documented Bearer scheme', () => {
  const replicate = PROVIDERS.find((p) => p.name === 'Replicate');
  assert.equal(replicate.headers('r8_abc').Authorization, 'Bearer r8_abc');
});
