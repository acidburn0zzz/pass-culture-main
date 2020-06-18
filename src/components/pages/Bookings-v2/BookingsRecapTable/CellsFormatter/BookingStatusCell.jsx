import React from 'react'
import PropTypes from 'prop-types'
import {
  computeStatusClassName,
  getBookingStatusDisplayInformationsOrDefault,
} from './utils/bookingStatusConverter'
import BookingStatusCellHistory from './BookingStatusCellHistory'

const BookingStatusCell = ({ bookingRecapInfo }) => {
  let bookingStatus = bookingRecapInfo.original.booking_status
  const offerName = bookingRecapInfo.original.stock.offer_name
  bookingStatus = bookingStatus.toLowerCase()

  const bookingStatusDisplayInformations = getBookingStatusDisplayInformationsOrDefault(
    bookingStatus
  )
  const statusClassName = computeStatusClassName(bookingStatusDisplayInformations)
  const statusName = bookingStatusDisplayInformations.status
    ? bookingStatusDisplayInformations.status
    : bookingStatus
  const amount = bookingRecapInfo.original.booking_amount
    ? `${bookingRecapInfo.original.booking_amount}\u00a0€`
    : 'Gratuit'

  return (
    <div className="booking-status-wrapper">
      <span className={`booking-status-label ${statusClassName}`}>
        {statusName}
      </span>
      <div className="bs-tooltip">
        <div className="bs-offer-title">
          {offerName}
        </div>
        <div className="bs-offer-amount">
          {`Prix : ${amount.replace('.', ',')}`}
        </div>
        <div className="bs-history-title">
          {'Historique'}
        </div>
        <BookingStatusCellHistory
          bookingStatusHistory={bookingRecapInfo.original.booking_status_history}
        />
      </div>
    </div>
  )
}

BookingStatusCell.propTypes = {
  bookingRecapInfo: PropTypes.shape().isRequired,
}

export default BookingStatusCell
