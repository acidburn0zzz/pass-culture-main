import { UploaderModeEnum } from 'components/ImageUploader/types'

export const modeValidationConstraints = {
  [UploaderModeEnum.OFFER]: {
    maxSize: 10000000,
    minWidth: 400,
    types: ['image/png', 'image/jpeg'],
  },
  [UploaderModeEnum.OFFER_COLLECTIVE]: {
    maxSize: 10000000,
    minWidth: 400,
    types: ['image/png', 'image/jpeg'],
  },
  [UploaderModeEnum.VENUE]: {
    maxSize: 10000000,
    minWidth: 600,
    types: ['image/png', 'image/jpeg'],
  },
}
