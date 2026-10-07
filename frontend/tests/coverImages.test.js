import assert from 'node:assert/strict'
import test from 'node:test'
import { safeCoverImageUrl } from '../src/utils/coverImages.js'

test('cover URLs allow HTTPS and strictly scoped bundled posters', () => {
  for (const value of ['https://images.example.org/poster.jpg', 'https://example.org/art?version=2', '/static/events/posters/sleep.svg']) {
    assert.equal(safeCoverImageUrl(value), value)
  }
})

test('cover URLs reject executable, insecure, credential and traversal addresses', () => {
  for (const value of [undefined, null, 2, '', 'javascript:alert(1)', 'data:image/svg+xml,abc',
    'http://example.org/art.png', '//example.org/art.png', 'https://user:pass@example.org/x',
    'https://example.org/white space', 'https://example.org\\@evil.org/x',
    '/static/events/posters/../secret.svg', '/static/events/posters/%2e%2e.svg',
    '/static/events/posters/a.svg?x=1', '/static/other.svg', 'https://']) {
    assert.equal(safeCoverImageUrl(value), '')
  }
})
