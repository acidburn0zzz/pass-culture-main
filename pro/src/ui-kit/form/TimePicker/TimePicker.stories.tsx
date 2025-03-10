import { action } from '@storybook/addon-actions'
import type { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import TimePicker, { TimePickerProps } from './TimePicker'

export default {
  title: 'ui-kit/forms/TimePicker',
  component: TimePicker,
}

const Template: Story<TimePickerProps> = props => (
  <Formik initialValues={{ time: '' }} onSubmit={action('onSubmit')}>
    {({ getFieldProps }) => {
      return <TimePicker {...getFieldProps('time')} {...props} name="time" />
    }}
  </Formik>
)

export const WithoutLabel = Template.bind({})

export const WithLabel = Template.bind({})
WithLabel.args = { label: 'Horaire' }

export const WithClearButton = Template.bind({})
WithClearButton.args = {
  label: 'Horaire',
  clearButtonProps: {
    tooltip: "Supprimer l'horaire",
    onClick: () => alert('Clear !'),
  },
}
