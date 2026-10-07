/** Read-only API access; fields remain defined in tech-stack.md's contract. */
export class ApiRequestError extends Error {
  constructor(status = 0) {
    super('Public API request failed')
    this.name = 'ApiRequestError'
    this.status = status
  }
}

async function requestJson(url, signal) {
  const response = await fetch(url, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    signal,
  })

  // Check HTTP status before decoding: a 404/500 is never an empty success.
  if (!response.ok) throw new ApiRequestError(response.status)
  const contentType = response.headers.get('content-type')?.split(';')[0].trim()
  if (contentType?.toLowerCase() !== 'application/json') {
    throw new ApiRequestError()
  }
  return response.json()
}

function hasTalkFields(talk) {
  return Boolean(talk && Number.isInteger(talk.id) && typeof talk.title === 'string'
    && talk.title.trim()
    && typeof talk.starts_at === 'string' && Number.isFinite(Date.parse(talk.starts_at))
    && typeof talk.topic === 'string' && typeof talk.speaker === 'string'
    && typeof talk.is_example === 'boolean'
    && (talk.cover_image_url === undefined || typeof talk.cover_image_url === 'string')
    && (talk.cover_image_alt === undefined || typeof talk.cover_image_alt === 'string')
    && Number.isInteger(talk.resource_count) && talk.resource_count >= 0)
}

function isOriginalUrl(value) {
  if (typeof value !== 'string') return false
  try {
    const url = new URL(value)
    return url.protocol === 'http:' || url.protocol === 'https:'
  } catch {
    return false
  }
}

function hasReadingFields(reading) {
  return Boolean(reading && Number.isInteger(reading.association_id)
    && Number.isInteger(reading.resource_id)
    && typeof reading.title === 'string' && reading.title.trim()
    && typeof reading.authors === 'string'
    && (reading.year === null || (Number.isInteger(reading.year)
      && reading.year >= 1 && reading.year <= 9999))
    && isOriginalUrl(reading.original_url)
    && ['research_paper', 'article'].includes(reading.resource_type)
    && typeof reading.recommendation === 'string')
}

/** @param {AbortSignal} signal @returns {Promise<import('./types.js').EventSummary[]>} */
export async function readTalks(signal) {
  const talks = await requestJson('/api/events/', signal)
  if (!Array.isArray(talks) || talks.some((talk) => !hasTalkFields(talk))) {
    throw new ApiRequestError()
  }
  return talks
}

/**
 * @param {string} id
 * @param {AbortSignal} signal
 * @returns {Promise<import('./types.js').EventDetail>}
 */
export async function readTalk(id, signal) {
  const talk = await requestJson(`/api/events/${encodeURIComponent(id)}/`, signal)
  if (!hasTalkFields(talk) || String(talk.id) !== String(Number(id))
    || typeof talk.description !== 'string' || !Array.isArray(talk.resources)
    || talk.resources.some((reading) => !hasReadingFields(reading))) {
    throw new ApiRequestError()
  }
  return talk
}

/**
 * One request lifetime. Cleanup both aborts fetch and suppresses late settlements
 * even if a transport/body reader does not honour cancellation.
 * @template T
 * @param {(signal: AbortSignal) => Promise<T>} load
 * @param {(result: {status: 'success'|'not_found'|'error', data: T|null}) => void} onResult
 */
export function startReadRequest(load, onResult) {
  const controller = new AbortController()
  let active = true
  const settled = Promise.resolve()
    .then(() => {
      if (!active) return
      return load(controller.signal)
    })
    .then(
      (data) => {
        if (active) onResult({ status: 'success', data })
      },
      (error) => {
        if (!active || controller.signal.aborted) return
        onResult({
          status: error instanceof ApiRequestError && error.status === 404
            ? 'not_found' : 'error',
          data: null,
        })
      },
    )

  return {
    settled,
    cancel() {
      active = false
      controller.abort()
    },
  }
}
