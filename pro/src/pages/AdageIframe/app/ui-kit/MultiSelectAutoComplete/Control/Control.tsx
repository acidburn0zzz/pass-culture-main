import cn from 'classnames'
import React from 'react'
import { components } from 'react-select'
import type { ControlProps } from 'react-select'

import { Option } from 'pages/AdageIframe/app/types'

import './Control.scss'
import { Pellet } from '../..'

const Control = <T,>({
  children,
  ...props
}: ControlProps<Option<T>>): JSX.Element => {
  const selectedValues = props.selectProps.value as Option[] | null
  const hasMulitpleSelectedValues = selectedValues && selectedValues.length > 0

  return (
    <components.Control
      {...props}
      className={cn({
        'multi-select-autocomplete-input--has-selected-value':
          hasMulitpleSelectedValues,
      })}
    >
      {hasMulitpleSelectedValues ? (
        <Pellet
          className="multi-select-autocomplete-input-pellet"
          label={selectedValues.length}
        />
      ) : null}
      {children}
    </components.Control>
  )
}

export default Control
