/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import get from 'lodash.get'
import PropTypes from 'prop-types'
import { Logger, Icon, requestData } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose, bindActionCreators } from 'redux'

import ShareButton from './share/ShareButton'
import VersoBookingButton from './VersoBookingButton'
import { getShareURL, isRecommendationFinished } from '../helpers'
import { selectBookings } from '../selectors/selectBookings'
import currentRecommendationSelector from '../selectors/currentRecommendation'

class VersoControl extends React.PureComponent {
  constructor(props) {
    super(props)
    const { dispatch } = this.props
    const actions = { requestData }
    this.actions = bindActionCreators(actions, dispatch)
  }

  componentWillMount() {
    Logger.fixme('VersoControl ---> componentWillMount')
  }

  componentWillUnmount() {
    Logger.fixme('VersoControl ---> componentWillUnmount')
  }

  onClickFavorite = () => {
    const { isFavorite, recommendationId } = this.props
    const method = 'PATCH'
    const url = `currentRecommendations/${recommendationId}`
    const opts = {
      body: { isFavorite: !isFavorite },
      key: 'currentRecommendations',
    }
    this.actions.requestData(method, url, opts)
  }

  render() {
    const {
      booking,
      isFavorite,
      isFinished,
      location,
      offer,
      recommendation,
      url,
      user,
      wallet,
    } = this.props

    const shareURL = getShareURL(location, user)
    const shareTitle = recommendation.offer.eventOrThing.name
    return (
      <ul className="verso-control">
        <li>
          <small className="pass-label">Mon Pass</small>
          <span className="pass-value">{wallet}€</span>
        </li>
        <li>
          <button
            type="button"
            className="button is-secondary"
            onClick={this.onClickFavorite}
          >
            <Icon
              alt={isFavorite ? 'Retirer des favoris' : 'Ajouter aux favoris'}
              svg={isFavorite ? 'ico-like-w-on' : 'ico-like-w'}
            />
          </button>
        </li>
        <li>
          <ShareButton shareURL={shareURL} shareTitle={shareTitle} />
        </li>
        <li>
          <VersoBookingButton
            isFinished={isFinished}
            booking={booking}
            offer={offer}
            url={url}
          />
        </li>
      </ul>
    )
  }
}

VersoControl.defaultProps = {
  booking: null,
  isFavorite: false,
  isFinished: false,
  offer: null,
  recommendation: null,
  recommendationId: null,
  wallet: null,
}

VersoControl.propTypes = {
  booking: PropTypes.object,
  dispatch: PropTypes.func.isRequired,
  isFavorite: PropTypes.bool,
  isFinished: PropTypes.bool,
  location: PropTypes.object.isRequired,
  offer: PropTypes.object,
  recommendation: PropTypes.object,
  recommendationId: PropTypes.string,
  url: PropTypes.string.isRequired,
  user: PropTypes.object.isRequired,
  wallet: PropTypes.number,
}

const mapStateToProps = (state, ownProps) => {
  const { user } = state
  const { mediationId, offerId } = ownProps.match.params
  const { wallet_balance: wallet } = user
  const recommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  )
  // NOTE -> on ne peut pas faire confiance a bookingsIds
  // bookingsIds n'est pas mis à jour avec le state
  const stocks = get(recommendation, 'offer.stocks')
  const stockIds = (stocks || []).map(o => o.id)
  const bookings = selectBookings(state)
  const booking = bookings.find(b => stockIds.includes(b.stockId))
  const isFinished = isRecommendationFinished(recommendation, offerId)
  return {
    booking,
    isFavorite: recommendation && recommendation.isFavorite,
    isFinished,
    offer: recommendation.offer,
    recommendation,
    recommendationId: recommendation.id,
    url: ownProps.match.url,
    user,
    wallet,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(VersoControl)
