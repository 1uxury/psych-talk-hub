const londonTime = new Intl.DateTimeFormat('en-GB', {
  timeZone: 'Europe/London',
  day: 'numeric',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  hourCycle: 'h23',
  timeZoneName: 'short',
})

/**
 * Use one supplied instant for both groups; never sort the API array in place.
 * @param {import('../api/types.js').EventSummary[]} talks
 * @param {number} now Current instant in milliseconds since the epoch.
 */
export function groupTalks(talks, now) {
  const upcoming = []
  const past = []

  for (const talk of talks) {
    const group = getTalkStatus(talk.starts_at, now) === 'Upcoming' ? upcoming : past
    group.push(talk)
  }

  upcoming.sort((a, b) => Date.parse(a.starts_at) - Date.parse(b.starts_at) || a.id - b.id)
  past.sort((a, b) => Date.parse(b.starts_at) - Date.parse(a.starts_at) || a.id - b.id)
  return { upcoming, past }
}

/** Classify a stored instant against the page's explicit snapshot, without a timer. */
export function getTalkStatus(startsAt, now) {
  return Date.parse(startsAt) > now ? 'Upcoming' : 'Past'
}

/** Display the same stored instant in London, regardless of the device zone. */
export function formatTalkTime(startsAt) {
  // Some browsers use offset names even with en-GB; normalise only the zone part.
  const zoneLabels = { 'GMT+0': 'GMT', 'GMT+00:00': 'GMT', 'GMT+1': 'BST', 'GMT+01:00': 'BST' }
  return londonTime.formatToParts(new Date(startsAt))
    .map(({ type, value }) => type === 'timeZoneName' ? (zoneLabels[value] ?? value) : value)
    .join('')
}
