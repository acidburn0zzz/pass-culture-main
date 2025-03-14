import * as yup from 'yup'

import { MAX_DETAILS_LENGTH } from 'core/OfferEducational'

const todayAtMidnight = () => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return today
}

const isBeforeEventDate = (
  bookingLimitDatetime: Date | undefined,
  context: yup.TestContext
) => {
  if (!context.parent.eventDate || !bookingLimitDatetime) {
    return true
  }

  if (
    bookingLimitDatetime.toLocaleDateString() ===
    context.parent.eventDate.toLocaleDateString()
  ) {
    return true
  }

  return bookingLimitDatetime < context.parent.eventDate
}

export const generateValidationSchema = (
  preventPriceIncrease: boolean,
  initialPrice: number | ''
) => {
  let totalPriceValidation = yup
    .number()
    .nullable()
    .min(0, 'Nombre positif attendu')
    .required('Champ requis')
  if (preventPriceIncrease && initialPrice) {
    totalPriceValidation = totalPriceValidation.max(
      initialPrice,
      'Vous ne pouvez pas définir un prix plus élevé.'
    )
  }

  return yup.object().shape({
    eventDate: yup
      .date()
      .nullable()
      .required('Champ requis')
      .when([], {
        is: () => preventPriceIncrease === false,
        then: yup
          .date()
          .min(
            todayAtMidnight(),
            "La date de l’évènement doit être supérieure à aujourd'hui"
          ),
        otherwise: yup.date(),
      }),
    eventTime: yup.string().nullable().required('Champ requis'),
    numberOfPlaces: yup
      .number()
      .nullable()
      .min(0, 'Nombre positif attendu')
      .required('Champ requis'),
    totalPrice: totalPriceValidation,
    bookingLimitDatetime: yup
      .date()
      .notRequired()
      .test({
        name: 'is-one-true',
        message:
          'La date limite de réservation doit être fixée au plus tard le jour de l’évènement',
        test: isBeforeEventDate,
      })
      .nullable(),
    priceDetail: yup.string().nullable().max(MAX_DETAILS_LENGTH),
  })
}

export const showcaseOfferValidationSchema = yup
  .object()
  .shape({ priceDetail: yup.string().nullable().max(MAX_DETAILS_LENGTH) })
