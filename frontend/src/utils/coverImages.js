/** Images load in the browser only; allow HTTPS or our bundled poster paths. */
export function safeCoverImageUrl(value) {
  if (typeof value !== 'string' || !value || /[\s\\]/u.test(value)) return ''
  if (/^\/static\/events\/posters\/[a-z0-9-]+\.svg$/u.test(value)) return value
  if (!value.startsWith('https://')) return ''
  try {
    const url = new URL(value)
    return url.protocol === 'https:' && url.hostname && !url.username && !url.password
      ? value : ''
  } catch {
    return ''
  }
}
