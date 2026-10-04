import assert from 'node:assert/strict'
import test from 'node:test'
import { formatTalkTime, getTalkStatus, groupTalks } from '../src/utils/talks.js'

const now = Date.parse('2026-10-04T12:00:00Z')

function talk(id, startsAt) {
  return Object.freeze({
    id, title: `Talk ${id}`, description: '', topic: '', speaker: '',
    starts_at: startsAt, is_example: false, resource_count: 0,
  })
}

function ids(talks) {
  return talks.map(({ id }) => id)
}

test('detail status uses the same exact-instant boundary as Home grouping', () => {
  for (const [startsAt, expected] of [
    ['2026-10-04T12:00:00.001Z', 'Upcoming'],
    ['2026-10-04T12:00:00Z', 'Past'],
    ['2026-10-04T11:59:59.999Z', 'Past'],
  ]) {
    assert.equal(getTalkStatus(startsAt, now), expected)
    const groups = groupTalks([talk(1, startsAt)], now)
    assert.equal(groups[expected === 'Upcoming' ? 'upcoming' : 'past'].length, 1)
  }
})

test('future is upcoming; the exact start instant and earlier instants are past', () => {
  const talks = [
    talk(1, '2026-10-04T12:00:00.001Z'),
    talk(2, '2026-10-04T12:00:00Z'),
    talk(3, '2026-10-04T11:59:59.999Z'),
  ]
  const groups = groupTalks(talks, now)
  assert.deepEqual(ids(groups.upcoming), [1])
  assert.deepEqual(ids(groups.past), [2, 3])
  assert.deepEqual([...groups.upcoming, ...groups.past].map(({ id }) => id).sort(), [1, 2, 3])
})

test('both groups sort by time then numeric ID without changing the API array or objects', () => {
  const talks = Object.freeze([
    talk(10, '2026-10-06T12:00:00Z'),
    talk(20, '2026-10-05T12:00:00Z'),
    talk(2, '2026-10-05T12:00:00Z'),
    talk(30, '2026-10-01T12:00:00Z'),
    talk(12, '2026-10-03T12:00:00Z'),
    talk(3, '2026-10-03T12:00:00Z'),
  ])
  const before = ids(talks)
  const { upcoming, past } = groupTalks(talks, now)
  assert.deepEqual(ids(upcoming), [2, 20, 10])
  assert.deepEqual(ids(past), [3, 12, 30])
  assert.deepEqual(ids(talks), before)
  assert.equal(upcoming[0], talks[2])
  assert.equal(past[0], talks[5])
})

test('only upcoming talks leaves a separate empty past group, including zero-resource talks', () => {
  const upcomingTalk = talk(1, '2026-10-05T12:00:00Z')
  assert.deepEqual(groupTalks([upcomingTalk], now), { upcoming: [upcomingTalk], past: [] })
})

test('only past talks leaves a separate empty upcoming group', () => {
  const pastTalk = talk(1, '2026-10-03T12:00:00Z')
  assert.deepEqual(groupTalks([pastTalk], now), { upcoming: [], past: [pastTalk] })
})

test('an empty successful list keeps both empty groups', () => {
  assert.deepEqual(groupTalks([], now), { upcoming: [], past: [] })
})

test('London display uses GMT in winter and BST in summer', () => {
  assert.equal(formatTalkTime('2026-01-15T18:30:00Z'), '15 Jan 2026, 18:30 GMT')
  assert.equal(formatTalkTime('2026-07-15T18:30:00Z'), '15 Jul 2026, 19:30 BST')
  assert.equal(formatTalkTime('2026-07-15T23:30:00Z'), '16 Jul 2026, 00:30 BST')
})

test('browser offset-name fallbacks display canonical GMT or BST without changing the date', (t) => {
  const partsMock = t.mock.method(Intl.DateTimeFormat.prototype, 'formatToParts')
  for (const [browserZone, expectedZone] of [
    ['GMT+0', 'GMT'], ['GMT+00:00', 'GMT'], ['GMT+1', 'BST'],
    ['GMT+01:00', 'BST'], ['GMT', 'GMT'], ['BST', 'BST'],
  ]) {
    partsMock.mock.mockImplementation(() => [
      { type: 'day', value: '15' }, { type: 'literal', value: ' Jul 2026, 19:30 ' },
      { type: 'timeZoneName', value: browserZone },
    ])
    assert.equal(formatTalkTime('2026-07-15T18:30:00Z'), `15 Jul 2026, 19:30 ${expectedZone}`)
  }
})

test('spring clock change skips the missing London hour while grouping compares instants', () => {
  assert.equal(formatTalkTime('2026-03-29T00:30:00Z'), '29 Mar 2026, 00:30 GMT')
  assert.equal(formatTalkTime('2026-03-29T01:30:00Z'), '29 Mar 2026, 02:30 BST')
  const groups = groupTalks([
    talk(1, '2026-03-29T00:30:00Z'), talk(2, '2026-03-29T01:30:00Z'),
  ], Date.parse('2026-03-29T01:00:00Z'))
  assert.deepEqual(ids(groups.past), [1])
  assert.deepEqual(ids(groups.upcoming), [2])
})

test('repeated autumn local hours retain GMT/BST labels and UTC ordering', () => {
  assert.equal(formatTalkTime('2026-10-25T00:30:00Z'), '25 Oct 2026, 01:30 BST')
  assert.equal(formatTalkTime('2026-10-25T01:30:00Z'), '25 Oct 2026, 01:30 GMT')
  const groups = groupTalks([
    talk(2, '2026-10-25T01:30:00Z'), talk(1, '2026-10-25T00:30:00Z'),
  ], Date.parse('2026-10-25T00:00:00Z'))
  assert.deepEqual(ids(groups.upcoming), [1, 2])
})
