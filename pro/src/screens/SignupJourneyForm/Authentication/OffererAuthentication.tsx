import { FormikProvider, useFormik } from 'formik'
import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

import FormLayout from 'components/FormLayout'
import { useSignupJourneyContext } from 'context/SignupJourneyContext'

import { ActionBar } from '../ActionBar'
import { DEFAULT_OFFERER_FORM_VALUES } from '../Offerer/constants'

import OffererAuthenticationForm, {
  IOffererAuthenticationFormValues,
} from './OffererAuthenticationForm'
import { validationSchema } from './validationSchema'

const OffererAuthentication = (): JSX.Element => {
  const navigate = useNavigate()

  const { offerer, setOfferer } = useSignupJourneyContext()

  const initialValues: IOffererAuthenticationFormValues = {
    ...DEFAULT_OFFERER_FORM_VALUES,
    ...offerer,
  }

  const handlePreviousStep = () => {
    navigate('/parcours-inscription/structure')
  }

  const onSubmitOffererAuthentication = async (
    formValues: IOffererAuthenticationFormValues
  ): Promise<void> => {
    setOfferer(formValues)
    navigate('/parcours-inscription/activite')
  }

  const formik = useFormik({
    initialValues,
    onSubmit: onSubmitOffererAuthentication,
    validationSchema,
    enableReinitialize: true,
  })

  useEffect(() => {
    if (offerer?.siret === '' || offerer?.name === '') {
      handlePreviousStep()
    }
  }, [])

  return (
    <FormLayout>
      <FormikProvider value={formik}>
        <form
          onSubmit={formik.handleSubmit}
          data-testid="signup-offerer-authentication-form"
        >
          <FormLayout.MandatoryInfo />
          <OffererAuthenticationForm />
          <ActionBar
            onClickPrevious={handlePreviousStep}
            previousStepTitle="Retour"
            isDisabled={formik.isSubmitting}
          />
        </form>
      </FormikProvider>
    </FormLayout>
  )
}

export default OffererAuthentication
