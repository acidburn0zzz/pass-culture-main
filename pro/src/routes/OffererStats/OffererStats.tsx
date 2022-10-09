import React from 'react'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import { useGetOffererNames } from 'core/Offerers/adapters'
import { OffererStatsScreen } from 'screens/OffererStats'
import { sortByDisplayName } from 'utils/strings'

const OffererStats = (): JSX.Element | null => {
  const notify = useNotification()
  const { isLoading, error, data: offererNames } = useGetOffererNames({})
  if (isLoading) {
    return <Spinner />
  }
  if (error) {
    notify.error(error.message)
    return null
  }
  const offererOptions = sortByDisplayName(
    offererNames.map(offerer => ({
      id: offerer.id,
      displayName: offerer.name,
    }))
  )
  return <OffererStatsScreen offererOptions={offererOptions} />
}

export default OffererStats
