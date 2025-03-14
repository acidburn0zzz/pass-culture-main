import { DEFAULT_PRICING_POINT_FORM_VALUES } from '../../pages/Offerers/Offerer/VenueV1/fields/PricingPoint/constant'

import { DEFAULT_ACCESSIBILITY_FORM_VALUES } from './Accessibility'
import { DEFAULT_ACTIVITY_FORM_VALUES } from './Activity'
import { DEFAULT_ADDRESS_FORM_VALUES } from './Address'
import { DEFAULT_CONTACT_FORM_VALUES } from './Contact'
import { DEFAULT_IMAGE_UPLOADER_FORM_VALUES } from './ImageUploaderVenue/'
import { DEFAULT_INFORMATIONS_FORM_VALUES } from './Informations'
import { DEFAULT_REIMBURSEMENT_POINT_FORM_VALUES } from './ReimbursementPoint'
import { DEFAULT_WITHDRAWAL_FORM_VALUES } from './WithdrawalDetails/constants'

export const DEFAULT_FORM_VALUES = {
  ...DEFAULT_INFORMATIONS_FORM_VALUES,
  ...DEFAULT_ADDRESS_FORM_VALUES,
  ...DEFAULT_ACTIVITY_FORM_VALUES,
  ...DEFAULT_ACCESSIBILITY_FORM_VALUES,
  ...DEFAULT_CONTACT_FORM_VALUES,
  ...DEFAULT_IMAGE_UPLOADER_FORM_VALUES,
  ...DEFAULT_WITHDRAWAL_FORM_VALUES,
  ...DEFAULT_REIMBURSEMENT_POINT_FORM_VALUES,
  ...DEFAULT_PRICING_POINT_FORM_VALUES,
}
