import { useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { Mode, OfferEducationalStockFormValues } from 'core/OfferEducational'
import { EuroIcon } from 'icons'
import { DatePicker, TextInput, TimePicker } from 'ui-kit'

import {
  BOOKING_LIMIT_DATETIME_LABEL,
  EVENT_DATE_LABEL,
  EVENT_TIME_LABEL,
  NUMBER_OF_PLACES_LABEL,
  TOTAL_PRICE_LABEL,
} from '../constants/labels'

export interface IFormStockProps {
  mode: Mode
  disablePriceAndParticipantInputs: boolean
  preventPriceIncrease: boolean
}

const FormStock = ({
  mode,
  disablePriceAndParticipantInputs,
}: IFormStockProps): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<OfferEducationalStockFormValues>()

  return (
    <FormLayout.Row inline>
      <DatePicker
        disabled={mode === Mode.READ_ONLY}
        label={EVENT_DATE_LABEL}
        minDateTime={new Date()}
        name="eventDate"
        smallLabel
        onChange={(name, date) => {
          if (mode === Mode.EDITION) {
            setFieldValue('bookingLimitDatetime', date)
          }
        }}
      />
      <TimePicker
        disabled={mode === Mode.READ_ONLY}
        label={EVENT_TIME_LABEL}
        name="eventTime"
        smallLabel
      />
      <TextInput
        disabled={disablePriceAndParticipantInputs}
        label={NUMBER_OF_PLACES_LABEL}
        name="numberOfPlaces"
        placeholder="Ex : 30"
        smallLabel
        type="number"
      />
      <TextInput
        disabled={disablePriceAndParticipantInputs}
        label={TOTAL_PRICE_LABEL}
        name="totalPrice"
        smallLabel
        step={0.01} // allow user to enter a price with cents
        type="number"
        rightIcon={() => <EuroIcon />}
      />
      <DatePicker
        disabled={mode === Mode.READ_ONLY}
        label={BOOKING_LIMIT_DATETIME_LABEL}
        maxDateTime={values.eventDate ? values.eventDate : undefined}
        name="bookingLimitDatetime"
        smallLabel
      />
    </FormLayout.Row>
  )
}

export default FormStock
