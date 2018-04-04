import React from 'react'

import DiscoveryPage from '../pages/DiscoveryPage'
import InventoryPage from '../pages/InventoryPage'
import HomePage from '../pages/HomePage'
import OffererPage from '../pages/OffererPage'
import ProfessionalPage from '../pages/ProfessionalPage'
import ProfilePage from '../pages/ProfilePage'
import SignPage from '../pages/SignPage'
import BookingsPage from '../pages/BookingsPage'
import RedirectPage from '../pages/RedirectPage'
import BetaPage from '../pages/BetaPage'

const routes = [
  {
    exact: true,
    path: '/',
    render: () => <HomePage />
  },
  {
    exact: true,
    path: '/decouverte',
    render: () => <RedirectPage />
  },
  {
    exact: true,
    path: '/decouverte/:offerId/:mediationId?',
    render: ({ match: { mediationId, offerId }}) =>
      <DiscoveryPage mediationId={mediationId} offerId={offerId}/>
  },
  {
    exact: true,
    path: '/pro',
    render: () => <ProfessionalPage />
  },
  {
    exact: true,
    path:'/pro/:offererId',
    render: props => <OffererPage offererId={props.match.params.offererId} />
  },
  {
    exact: true,
    path: '/beta',
    render: () => <BetaPage />
  },
  {
    exact: true,
    path: '/inscription',
    render: () => <SignPage />
  },
  {
    exact: true,
    path: '/inventaire',
    render: () => <InventoryPage />
  },
  {
    exact: true,
    path: '/reservations',
    render: () => <BookingsPage />
  },
  {
    exact: true,
    path: '/profil',
    render: () => <ProfilePage />
  }
]

export default routes
