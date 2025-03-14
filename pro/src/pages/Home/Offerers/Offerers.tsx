import React, { useCallback, useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import {
  GetOffererResponseModel,
  GetOfferersNamesResponseModel,
} from 'apiClient/v1'
import RedirectDialog from 'components/Dialog/RedirectDialog'
import SoftDeletedOffererWarning from 'components/SoftDeletedOffererWarning'
import {
  Events,
  OFFER_FORM_HOMEPAGE,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { useNewOfferCreationJourney } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
import { ReactComponent as StatusPendingFullIcon } from 'icons/ico-status-pending-full.svg'
import { ReactComponent as SuccessIcon } from 'icons/ico-success.svg'
import { OffererVenues } from 'pages/Home/OffererVenues'
import { VenueList } from 'pages/Home/Venues'
import Spinner from 'ui-kit/Spinner/Spinner'
import { sortByDisplayName } from 'utils/strings'

import OffererCreationLinks from './OffererCreationLinks'
import OffererDetails from './OffererDetails'
import VenueCreationLinks from './VenueCreationLinks'

export const CREATE_OFFERER_SELECT_ID = 'creation'

interface IOfferersProps {
  receivedOffererNames?: GetOfferersNamesResponseModel | null
  onSelectedOffererChange: (offererId: string) => void
  cancelLoading: () => void
  selectedOfferer?: GetOffererResponseModel | null
  isLoading: boolean
  isUserOffererValidated: boolean
  venues: OffererVenues
}
const Offerers = ({
  receivedOffererNames,
  onSelectedOffererChange,
  cancelLoading,
  selectedOfferer,
  isLoading,
  isUserOffererValidated,
  venues,
}: IOfferersProps) => {
  const [offererOptions, setOffererOptions] = useState<SelectOptionsRFF>([])
  const [openSuccessDialog, setOpenSuccessDialog] = useState(false)

  const location = useLocation()
  const navigate = useNavigate()

  const hasNewOfferCreationJourney = useNewOfferCreationJourney()
  const { logEvent } = useAnalytics()

  const setQuery = (offererId: string) => {
    const frenchQueryString = `structure=${offererId}`
    navigate(`${location.pathname}?${frenchQueryString}`)
  }

  const { structure: offererId } = Object.fromEntries(
    new URLSearchParams(location.search)
  )

  useEffect(() => {
    if (receivedOffererNames) {
      if (receivedOffererNames.offerersNames.length > 0) {
        const initialOffererOptions = sortByDisplayName(
          receivedOffererNames.offerersNames.map(item => ({
            id: item['nonHumanizedId'].toString(),
            displayName: item['name'],
          }))
        )
        onSelectedOffererChange(offererId ?? initialOffererOptions[0].id)
        setOffererOptions([
          ...initialOffererOptions,
          {
            displayName: '+ Ajouter une structure',
            id: CREATE_OFFERER_SELECT_ID,
          },
        ])
      } else {
        cancelLoading()
      }
    }
  }, [offererId, receivedOffererNames])

  useEffect(() => {
    if (hasNewOfferCreationJourney) {
      location.search === '?success' && setOpenSuccessDialog(true)
    }
  }, [hasNewOfferCreationJourney])

  const handleChangeOfferer = useCallback(
    (event: React.ChangeEvent<HTMLSelectElement>) => {
      const newOffererId = event.target.value
      if (newOffererId === CREATE_OFFERER_SELECT_ID) {
        navigate('/structures/creation')
      } else if (newOffererId !== selectedOfferer?.id) {
        onSelectedOffererChange(newOffererId)
        setQuery(newOffererId)
      }
    },
    [navigate, selectedOfferer, setQuery]
  )

  if (isLoading) {
    return (
      <div className="h-card h-card-secondary h-card-placeholder">
        <div className="h-card-inner">
          <Spinner />
        </div>
      </div>
    )
  }

  const removeSuccessParams = () => {
    if (hasNewOfferCreationJourney) {
      const queryParams = new URLSearchParams(location.search)
      if (queryParams.has('success')) {
        queryParams.delete('success')
        navigate(
          {
            search: queryParams.toString(),
          },
          { replace: true }
        )
      }
    }
  }

  const isOffererSoftDeleted =
    selectedOfferer && selectedOfferer.isActive === false
  const userHasOfferers = offererOptions.length > 0
  const creationLinkCondition =
    (hasNewOfferCreationJourney && venues.physicalVenues.length > 0) ||
    (!hasNewOfferCreationJourney &&
      isUserOffererValidated &&
      !isOffererSoftDeleted &&
      venues.physicalVenues.length > 0)
  return (
    <>
      {userHasOfferers && selectedOfferer && (
        <>
          {openSuccessDialog && (
            <RedirectDialog
              icon={SuccessIcon}
              redirectText="Créer une offre"
              redirectLink={{
                to: `/offre/creation?structure=${selectedOfferer.id}`,
                isExternal: false,
              }}
              cancelText="Plus tard"
              withRedirectLinkIcon={false}
              title="Félicitations,"
              secondTitle="vous avez créé votre lieu !"
              onRedirect={() =>
                logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                  from: OFFER_FORM_NAVIGATION_IN.HOME,
                  to: OFFER_FORM_HOMEPAGE,
                  used: OFFER_FORM_NAVIGATION_MEDIUM.CREATE_OFFER_POPIN,
                  isEdition: false,
                })
              }
              onCancel={() => {
                removeSuccessParams()
                setTimeout(() => window.hj?.('event', 'click_on_later'), 200)
                logEvent?.(
                  Events.CLICKED_SEE_LATER_FROM_SUCCESS_VENUE_CREATION_MODAL,
                  {
                    from: location.pathname,
                  }
                )
                setOpenSuccessDialog(false)
              }}
              cancelIcon={StatusPendingFullIcon}
            >
              <p>Vous pouvez dès à présent créer une offre.</p>
            </RedirectDialog>
          )}
          <h2 className="h-section-title">Structures et lieux</h2>
          <OffererDetails
            handleChangeOfferer={handleChangeOfferer}
            isUserOffererValidated={isUserOffererValidated}
            offererOptions={offererOptions}
            selectedOfferer={selectedOfferer}
          />

          {!isOffererSoftDeleted && (
            <VenueList
              physicalVenues={venues.physicalVenues}
              selectedOffererId={selectedOfferer.id}
              virtualVenue={
                selectedOfferer.hasDigitalVenueAtLeastOneOffer
                  ? venues.virtualVenue
                  : null
              }
            />
          )}
        </>
      )}
      {
        /* istanbul ignore next: DEBT, TO FIX */ isUserOffererValidated &&
          isOffererSoftDeleted && <SoftDeletedOffererWarning />
      }
      {!userHasOfferers && <OffererCreationLinks />}
      {creationLinkCondition && (
        <VenueCreationLinks
          hasPhysicalVenue={venues.physicalVenues.length > 0}
          hasVirtualOffers={
            Boolean(venues.virtualVenue) &&
            Boolean(selectedOfferer?.hasDigitalVenueAtLeastOneOffer)
          }
          offererId={
            /* istanbul ignore next: DEBT, TO FIX */ selectedOfferer
              ? selectedOfferer.id
              : null
          }
        />
      )}
    </>
  )
}

export default Offerers
