import { useEffect, useState } from 'react'
import { startReadRequest } from '../api/client.js'

/** A stable imported loader plus its route argument identifies the current read. */
export default function useApiRequest(load, argument) {
  const [attempt, setAttempt] = useState(0)
  const [result, setResult] = useState(null)

  useEffect(() => {
    const request = startReadRequest(
      (signal) => argument === undefined ? load(signal) : load(argument, signal),
      (nextResult) => setResult({ ...nextResult, load, argument, attempt }),
    )
    return request.cancel
  }, [load, argument, attempt])

  // Hide any earlier result immediately, before the effect's next setup runs.
  const current = result?.load === load && result?.argument === argument
    && result?.attempt === attempt
    ? result : { status: 'loading', data: null }

  return {
    status: current.status,
    data: current.data,
    retry: () => setAttempt((previous) => previous + 1),
  }
}
