import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import fetch from 'jest-fetch-mock'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import Notification from 'components/Notification/Notification'
import {
  ISignupJourneyContext,
  SignupJourneyContext,
} from 'context/SignupJourneyContext'
import { renderWithProviders } from 'utils/renderWithProviders'

import { Offerer } from '..'
import { DEFAULT_OFFERER_FORM_VALUES } from '../constants'

jest.mock('apiClient/api', () => ({
  api: {
    getSiretInfo: jest.fn(),
    getVenuesOfOffererFromSiret: jest.fn(),
  },
}))

// Mock l'appel à https://api-adresse.data.gouv.fr/search/?limit=${limit}&q=${address}
// Appel fait dans apiAdresse.getDataFromAddress
fetch.mockResponse(
  JSON.stringify({
    features: [
      {
        properties: {
          name: 'name',
          city: 'city',
          id: 'id',
          label: 'label',
          postcode: 'postcode',
        },
        geometry: {
          coordinates: [0, 0],
        },
      },
    ],
  }),
  { status: 200 }
)
const renderOffererScreen = (contextValue: ISignupJourneyContext) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        publicName: 'John Do',
        isAdmin: false,
        email: 'email@example.com',
      },
    },
  }

  return renderWithProviders(
    <>
      <SignupJourneyContext.Provider value={contextValue}>
        <Routes>
          <Route path="/parcours-inscription/structure" element={<Offerer />} />
          <Route
            path="/parcours-inscription/authentification"
            element={<div>Authentication screen</div>}
          />
          <Route
            path="/parcours-inscription/structure/rattachement"
            element={<div>Offerers screen</div>}
          />
        </Routes>
      </SignupJourneyContext.Provider>
      <Notification />
    </>,
    {
      storeOverrides,
      initialRouterEntries: ['/parcours-inscription/structure'],
    }
  )
}
describe('screens:SignupJourney::Offerer', () => {
  let contextValue: ISignupJourneyContext
  beforeEach(() => {
    contextValue = {
      activity: null,
      offerer: DEFAULT_OFFERER_FORM_VALUES,
      setActivity: () => {},
      setOfferer: () => {},
    }
    jest.spyOn(api, 'getSiretInfo').mockResolvedValue({
      active: true,
      address: {
        city: 'Paris',
        postalCode: '75008',
        street: 'rue du test',
      },
      name: 'Test',
      siret: '12345678933333',
    })

    jest.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      venues: [],
    })
  })

  it('should render component', async () => {
    contextValue.offerer = null
    renderOffererScreen(contextValue)

    expect(
      await screen.findByText('Renseignez le SIRET de votre structure')
    ).toBeInTheDocument()
    expect(
      await screen.findByRole('button', { name: 'Continuer' })
    ).toBeInTheDocument()
    expect(
      await screen.queryByRole('button', { name: 'Étape précédente' })
    ).not.toBeInTheDocument()

    expect(
      await screen.getByText('Votre structure dépend d’un autre SIRET ?')
    ).toBeInTheDocument()
  })

  it('should display authentication signup journey step on submit', async () => {
    contextValue.offerer = {
      siret: '12345678933333',
      name: 'Test',
    }

    renderOffererScreen(contextValue)
    expect(
      await screen.findByText('Renseignez le SIRET de votre structure')
    ).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
    expect(screen.getByText('Authentication screen')).toBeInTheDocument()
  })

  it('should not display authentication screen on submit with form error', async () => {
    jest.spyOn(api, 'getSiretInfo').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 422,
          body: [{ error: ['No SIRET'] }],
        } as ApiResult,
        ''
      )
    )

    renderOffererScreen(contextValue)

    expect(
      await screen.getByText('Renseignez le SIRET de votre structure')
    ).toBeInTheDocument()

    await userEvent.type(
      screen.getByLabelText('Numéro de SIRET à 14 chiffres'),
      '12345678999999'
    )

    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(await screen.findByText('Le SIRET n’existe pas')).toBeInTheDocument()
    expect(api.getSiretInfo).toHaveBeenCalledTimes(1)
    expect(screen.queryByText('Authentication screen')).not.toBeInTheDocument()
    expect(
      await screen.getByText('Renseignez le SIRET de votre structure')
    ).toBeInTheDocument()
  })

  it('should redirect to offerers screen if venue exist', async () => {
    jest.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValueOnce({
      venues: [
        { id: '1', name: 'First Venue' },
        { id: '2', name: 'Second Venue' },
      ],
    })
    await renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText('Numéro de SIRET à 14 chiffres'),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
    await waitFor(() => {
      expect(screen.getByText('Offerers screen')).toBeInTheDocument()
    })
  })

  it('should redirect to offerers screen if venue exist', async () => {
    jest.spyOn(api, 'getVenuesOfOffererFromSiret').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 500,
          body: [{ error: ['ERROR'] }],
        } as ApiResult,
        ''
      )
    )
    await renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText('Numéro de SIRET à 14 chiffres'),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
    await waitFor(() => {
      expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument()
    })
  })
})
