import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { OfferStockResponse } from 'apiClient/adage'

import PrebookingButton from '../PrebookingButton'

jest.mock('repository/pcapi/pcapi', () => ({
  preBookStock: jest.fn(),
}))

jest.mock('apiClient/api', () => ({
  apiAdage: { bookCollectiveOffer: jest.fn() },
}))

describe('offer', () => {
  let stock: OfferStockResponse
  beforeEach(() => {
    stock = {
      id: 117,
      beginningDatetime: '03/01/2023',
      bookingLimitDatetime: '01/01/2023',
      isBookable: true,
      price: 20,
      numberOfTickets: 3,
      educationalPriceDetail: '1200',
    }
  })

  describe('offer item', () => {
    it('should not display when prebooking is not activated', async () => {
      // Given
      render(
        <PrebookingButton
          canPrebookOffers={false}
          offerId={1}
          queryId="aez"
          stock={stock}
        />
      )
      // When - Then
      expect(screen.queryByText('Préréserver')).not.toBeInTheDocument()
    })

    it('should display when prebooking is activated', async () => {
      // Given
      render(
        <PrebookingButton
          canPrebookOffers
          offerId={1}
          queryId="aez"
          stock={stock}
        />
      )
      // When - Then
      expect(screen.getByText('Préréserver')).toBeInTheDocument()
    })
    it('should display modal on click', async () => {
      // Given
      render(
        <PrebookingButton
          canPrebookOffers
          offerId={1}
          queryId="aez"
          stock={stock}
        />
      )
      // When
      const preBookButton = screen.getByRole('button', { name: 'Préréserver' })
      await userEvent.click(preBookButton)

      // Then
      expect(
        screen.getByText('Êtes-vous sûr de vouloir préréserver ?')
      ).toBeInTheDocument()
    })
  })
})
