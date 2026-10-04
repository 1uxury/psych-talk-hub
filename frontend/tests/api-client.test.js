import assert from 'node:assert/strict'
import test from 'node:test'
import { ApiRequestError, readTalk, readTalks, startReadRequest } from '../src/api/client.js'

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
  })
}

function talk(id) {
  return {
    id, title: `Talk ${id}`, description: '', topic: '', speaker: '',
    starts_at: '2026-11-03T18:00:00Z', is_example: true, resource_count: 0,
    resources: [],
  }
}

test('list reads use relative GET, JSON Accept and the provided abort signal', async (t) => {
  const controller = new AbortController()
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse([]))
  assert.deepEqual(await readTalks(controller.signal), [])
  const [url, options] = fetchMock.mock.calls[0].arguments
  assert.equal(url, '/api/events/')
  assert.equal(options.method, 'GET')
  assert.equal(options.headers.Accept, 'application/json')
  assert.equal(options.signal, controller.signal)
})

test('detail keeps nullable metadata and resource order unchanged', async (t) => {
  const detail = talk(2)
  detail.resources = [{
    association_id: 7, resource_id: 3, title: 'Manual reading', authors: '',
    year: null, doi: null, original_url: 'https://example.org/reading',
    resource_type: 'article', metadata_source: 'manual',
    recommendation: '', display_order: -1,
  }, {
    association_id: 2, resource_id: 99, title: 'Shared paper', authors: 'Author A; Author B',
    year: 2026, doi: '10.1234/order', original_url: 'http://example.org/paper',
    resource_type: 'research_paper', metadata_source: 'crossref',
    recommendation: 'First line.\nSecond line.', display_order: 0,
  }, {
    association_id: 20, resource_id: 1, title: 'Another reading', authors: 'Author C',
    year: 1, doi: null, original_url: 'https://example.org/another',
    resource_type: 'article', metadata_source: 'manual',
    recommendation: '', display_order: 0,
  }]
  detail.resource_count = 3
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse(detail))
  assert.deepEqual(await readTalk('2', new AbortController().signal), detail)
  assert.equal(fetchMock.mock.calls[0].arguments[0], '/api/events/2/')
})

test('bad detail metadata or unsafe original links settle as failure with no retained reading', async (t) => {
  const reading = {
    association_id: 7, resource_id: 3, title: 'Reading', authors: '', year: null,
    doi: null, original_url: 'https://example.org/reading', resource_type: 'article',
    metadata_source: 'manual', recommendation: '', display_order: -1,
  }
  const detail = { ...talk(1), resource_count: 1, resources: [reading] }
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse(detail))
  const badDetails = [
    ...[
      { starts_at: 'not-a-date' }, { starts_at: null }, { title: '  ' },
      { description: null }, { topic: null }, { speaker: null }, { is_example: 'true' },
      { resource_count: null }, { resource_count: -1 }, { resource_count: 1.5 },
    ].map((fields) => ({ ...detail, ...fields })),
    ...[
      { association_id: '7' }, { resource_id: null }, { title: null }, { title: '  ' },
      { authors: null }, { year: undefined }, { year: '2026' }, { year: 0 },
      { year: 10000 }, { year: 2026.5 }, { recommendation: null },
      { resource_type: 'unknown' }, { original_url: null }, { original_url: '/relative' },
      { original_url: 'not-a-url' }, { original_url: 'javascript:alert(1)' },
      { original_url: 'data:text/html,example' }, { original_url: 'ftp://example.org/reading' },
    ].map((fields) => ({ ...detail, resources: [{ ...reading, ...fields }] })),
    { ...detail, resources: [null] },
  ]
  for (const badDetail of badDetails) {
    fetchMock.mock.mockImplementation(async () => jsonResponse(badDetail))
    const results = []
    await startReadRequest((signal) => readTalk('1', signal),
      (result) => results.push(result)).settled
    assert.deepEqual(results, [{ status: 'error', data: null }])
  }
})

test('404 is checked before the body is decoded', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => ({
    ok: false, status: 404,
    json() { assert.fail('An error response must not be decoded as success') },
  }))
  await assert.rejects(readTalk('999', new AbortController().signal),
    (error) => error instanceof ApiRequestError && error.status === 404)
})

test('500 with an empty-array body is a failure, not an empty success', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => jsonResponse([], 500))
  await assert.rejects(readTalks(new AbortController().signal),
    (error) => error instanceof ApiRequestError && error.status === 500)
})

test('malformed successful JSON is rejected', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => new Response('{', {
    headers: { 'Content-Type': 'application/json' },
  }))
  await assert.rejects(readTalks(new AbortController().signal), SyntaxError)
})

test('an HTML entry response cannot be mistaken for API data', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => new Response('[]', {
    headers: { 'Content-Type': 'text/html' },
  }))
  await assert.rejects(readTalks(new AbortController().signal), ApiRequestError)
})

test('a wrapped list is rejected rather than shown as empty', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => jsonResponse({ results: [] }))
  await assert.rejects(readTalks(new AbortController().signal), ApiRequestError)
})

test('invalid list entries are rejected without normalising the contract', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => jsonResponse([{ id: '1', title: 'Talk' }]))
  await assert.rejects(readTalks(new AbortController().signal), ApiRequestError)
})

test('invalid card fields become request failures rather than broken dates or invented counts', async (t) => {
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse([]))
  for (const changedFields of [
    { starts_at: '' }, { starts_at: 'not-a-date' }, { starts_at: null },
    { topic: null }, { speaker: null }, { is_example: 'true' },
    { resource_count: null }, { resource_count: '0' },
    { resource_count: -1 }, { resource_count: 1.5 },
  ]) {
    fetchMock.mock.mockImplementation(async () => jsonResponse([{ ...talk(1), ...changedFields }]))
    const results = []
    await startReadRequest(readTalks, (result) => results.push(result)).settled
    assert.deepEqual(results, [{ status: 'error', data: null }])
  }
})

test('a detail for the wrong identity or without resources is rejected', async (t) => {
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse(talk(1)))
  await assert.rejects(readTalk('2', new AbortController().signal), ApiRequestError)
  fetchMock.mock.mockImplementation(async () => jsonResponse({ id: 2, title: 'Talk 2' }))
  await assert.rejects(readTalk('2', new AbortController().signal), ApiRequestError)
})

test('empty successful data settles as success', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => jsonResponse([]))
  const results = []
  const request = startReadRequest(readTalks, (result) => results.push(result))
  await request.settled
  assert.deepEqual(results, [{ status: 'success', data: [] }])
})

test('a real detail with no readings still settles as success', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => jsonResponse(talk(3)))
  const results = []
  await startReadRequest((signal) => readTalk('3', signal),
    (result) => results.push(result)).settled
  assert.deepEqual(results, [{ status: 'success', data: talk(3) }])
})

test('missing detail settles as not_found with no retained data', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => jsonResponse({ detail: 'Not found.' }, 404))
  const results = []
  const request = startReadRequest((signal) => readTalk('999', signal),
    (result) => results.push(result))
  await request.settled
  assert.deepEqual(results, [{ status: 'not_found', data: null }])
})

test('server and network errors settle safely and allow a fresh retry', async (t) => {
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse([], 503))
  const results = []
  await startReadRequest(readTalks, (result) => results.push(result)).settled
  fetchMock.mock.mockImplementation(async () => { throw new TypeError('Private network detail') })
  await startReadRequest(readTalks, (result) => results.push(result)).settled
  fetchMock.mock.mockImplementation(async () => jsonResponse([]))
  await startReadRequest(readTalks, (result) => results.push(result)).settled
  assert.deepEqual(results, [
    { status: 'error', data: null }, { status: 'error', data: null },
    { status: 'success', data: [] },
  ])
})

test('a delayed request emits no success or empty state while pending', async (t) => {
  const pending = Promise.withResolvers()
  t.mock.method(globalThis, 'fetch', () => pending.promise)
  const results = []
  const request = startReadRequest(readTalks, (result) => results.push(result))
  await Promise.resolve()
  assert.deepEqual(results, [])
  pending.resolve(jsonResponse([]))
  await request.settled
  assert.deepEqual(results, [{ status: 'success', data: [] }])
})

test('cancellation aborts the signal and suppresses a late body result', async (t) => {
  const body = Promise.withResolvers()
  const bodyStarted = Promise.withResolvers()
  let signal
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    assert.equal(url, '/api/events/')
    signal = options.signal
    return {
      ok: true, headers: new Headers({ 'Content-Type': 'application/json' }),
      json() {
        bodyStarted.resolve()
        return body.promise
      },
    }
  })
  const results = []
  const request = startReadRequest(readTalks, (result) => results.push(result))
  await bodyStarted.promise
  request.cancel()
  assert.equal(signal.aborted, true)
  body.resolve([])
  await request.settled
  assert.deepEqual(results, [])
})

test('a late old event cannot replace the newer event even if fetch ignores abort', async (t) => {
  const oldResponse = Promise.withResolvers()
  const newResponse = Promise.withResolvers()
  t.mock.method(globalThis, 'fetch', (url) => url === '/api/events/1/'
    ? oldResponse.promise : newResponse.promise)
  const results = []
  const oldRequest = startReadRequest((signal) => readTalk('1', signal),
    (result) => results.push(result))
  await Promise.resolve()
  oldRequest.cancel()
  const newRequest = startReadRequest((signal) => readTalk('2', signal),
    (result) => results.push(result))
  newResponse.resolve(jsonResponse(talk(2)))
  await newRequest.settled
  oldResponse.resolve(jsonResponse(talk(1)))
  await oldRequest.settled
  assert.deepEqual(results, [{ status: 'success', data: talk(2) }])
})

test('cancelled rejection never becomes a visible error', async (t) => {
  const pending = Promise.withResolvers()
  t.mock.method(globalThis, 'fetch', () => pending.promise)
  const results = []
  const request = startReadRequest(readTalks, (result) => results.push(result))
  await Promise.resolve()
  request.cancel()
  pending.reject(new DOMException('Aborted', 'AbortError'))
  await request.settled
  assert.deepEqual(results, [])
})

test('immediate setup/cleanup/setup leaves only the current request active', async (t) => {
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse([]))
  const results = []
  const first = startReadRequest(readTalks, (result) => results.push(result))
  first.cancel()
  const second = startReadRequest(readTalks, (result) => results.push(result))
  await Promise.all([first.settled, second.settled])
  assert.equal(fetchMock.mock.calls.length, 1)
  assert.deepEqual(results, [{ status: 'success', data: [] }])
})
