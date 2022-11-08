import cx from 'classnames'
import { useField, useFormikContext } from 'formik'
import React, { KeyboardEventHandler, useEffect, useRef, useState } from 'react'

import { BaseInput } from '../shared'
import FieldLayout from '../shared/FieldLayout'

import OptionsList from './OptionsList'
import styles from './SelectAutocomplete.module.scss'
import Tags from './Tags'
import Toggle from './Toggle'

export interface SelectAutocompleteProps {
  className?: string
  disabled?: boolean
  fieldName: string
  hideArrow?: boolean
  hideFooter?: boolean
  hideTags?: boolean
  inline?: boolean
  isOptional?: boolean
  label: string
  maxHeight?: number
  multi?: boolean
  options: SelectOption[]
  placeholder?: string
  pluralLabel?: string
  smallLabel?: boolean
}

const SelectAutocomplete = ({
  className,
  disabled = false,
  fieldName,
  hideArrow,
  hideFooter = false,
  hideTags = false,
  inline,
  isOptional = false,
  label,
  maxHeight,
  multi = false,
  options,
  placeholder,
  pluralLabel,
  smallLabel = false,
}: SelectAutocompleteProps): JSX.Element => {
  const { setFieldTouched, setFieldValue } = useFormikContext<any>()

  const [field, meta] = useField<string | string[]>(fieldName)
  const [searchField, searchMeta] = useField(`search-${fieldName}`)

  const [hoveredOptionIndex, setHoveredOptionIndex] = useState<number | null>(
    null
  )
  const [optionsLabelById, setOptionsLabelById] = useState<
    Record<string, string>
  >({})

  const containerRef = useRef<HTMLDivElement>(null)
  const listRef = useRef<HTMLUListElement>(null)
  const [isOpen, setIsOpen] = useState(false)
  const [filteredOptions, setFilteredOptions] = useState(options)

  useEffect(() => {
    setFilteredOptions(options)
  }, [options])

  useEffect(() => {
    if (isOpen && searchField.value !== '')
      setFieldValue(`search-${fieldName}`, '', false)
  }, [isOpen])

  /* hashtable for the options */
  useEffect(() => {
    setOptionsLabelById(
      options.reduce<Record<string, string>>((optionsById, option) => {
        optionsById[option.value] = option.label
        return optionsById
      }, {})
    )
  }, [options])

  /* istanbul ignore next */
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent): void => {
      if (!containerRef.current?.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    if (containerRef.current) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [containerRef])

  useEffect(() => {
    const regExp = new RegExp(searchField.value, 'i')
    setFilteredOptions(
      options.filter(
        option => searchField.value === '' || option.label.match(regExp)
      )
    )
    setHoveredOptionIndex(null)
  }, [searchField.value])

  /* istanbul ignore next */
  const handleKeyDown: KeyboardEventHandler<HTMLDivElement> = event => {
    switch (event.key) {
      case 'ArrowUp':
        if (hoveredOptionIndex !== null) {
          if (hoveredOptionIndex <= 0) {
            setHoveredOptionIndex(null)
          } else {
            setHoveredOptionIndex(hoveredOptionIndex - 1)
          }
        }
        if (!isOpen) setIsOpen(true)
        listRef.current?.focus()
        break
      case 'ArrowDown':
        if (hoveredOptionIndex === null) {
          setHoveredOptionIndex(0)
        } else if (hoveredOptionIndex >= filteredOptions.length - 1) {
          setHoveredOptionIndex(filteredOptions.length - 1)
        } else {
          setHoveredOptionIndex(hoveredOptionIndex + 1)
        }
        if (!isOpen) setIsOpen(true)
        listRef.current?.focus()
        break
      case 'Space':
        openField()
        listRef.current?.focus()
        break
      case 'Enter':
        if (isOpen && hoveredOptionIndex !== null) {
          selectOption(filteredOptions[hoveredOptionIndex].value)
        }
        break
      case 'Escape':
        setHoveredOptionIndex(null)
        setIsOpen(false)
        break
      case 'Tab':
        setHoveredOptionIndex(null)
        setIsOpen(false)
        break
      default:
        //
        break
    }
  }

  const selectOption = (value: string) => {
    let updatedSelection
    if (multi) {
      if (field.value.includes(value) && Array.isArray(field.value)) {
        updatedSelection = field.value.filter(li => li !== value)
      } else {
        updatedSelection = [...field.value, value]
      }
    } else {
      updatedSelection = value
      setIsOpen(false)
      setHoveredOptionIndex(null)
      setFieldValue(
        `search-${fieldName}`,
        optionsLabelById[updatedSelection],
        false
      )
    }
    setFieldValue(fieldName, updatedSelection)
  }

  const openField = () => {
    /* istanbul ignore next */
    if (!isOpen) setIsOpen(true)
    setFieldTouched(fieldName, true)
  }

  const toggleField = () => {
    if (isOpen) {
      setIsOpen(false)
      setFieldValue(`search-${fieldName}`, '', false)
    } else {
      setIsOpen(true)
    }
    setFieldTouched(fieldName, true)
  }

  const placeholderDisplay = multi
    ? placeholder ??
      (field.value.length > 1 && pluralLabel ? pluralLabel : label)
    : ''

  return (
    <FieldLayout
      className={className}
      error={meta.error}
      hideFooter={!hideTags && field.value.length > 0 ? true : hideFooter}
      isOptional={isOptional}
      label={label}
      name={`search-${fieldName}`}
      showError={meta.touched && !!meta.error}
      smallLabel={smallLabel}
      inline={inline}
    >
      <div
        className={cx(styles['multi-select-autocomplete-container'], className)}
        onKeyDown={handleKeyDown}
        ref={containerRef}
      >
        <BaseInput
          {...(hoveredOptionIndex !== null && {
            'aria-activedescendant': `option-display-${filteredOptions[hoveredOptionIndex]?.value}`,
          })}
          onFocus={openField}
          placeholder={placeholderDisplay}
          style={{
            paddingLeft: multi && field.value.length > 0 ? '2.2rem' : '1rem',
          }}
          className={styles['multi-select-autocomplete-placeholder-input']}
          hasError={searchMeta.touched && !!searchMeta.error}
          type="text"
          disabled={disabled}
          {...searchField}
          aria-autocomplete="list"
          aria-controls={`list-${fieldName}`}
          aria-describedby={`help-${fieldName}`}
          aria-expanded={isOpen}
          aria-haspopup="listbox"
          role="combobox"
        />
        <div
          aria-live="polite"
          aria-relevant="text"
          className={styles['visually-hidden']}
          id={`help-${fieldName}`}
        >
          {multi && `${field.value.length} options sélectionnées`}
          {!multi &&
            !Array.isArray(field.value) &&
            field.value !== '' &&
            `Option sélectionnée : ${optionsLabelById[field.value]}`}
          {isOpen
            ? `${filteredOptions.length} options ${
                searchField.value === ''
                  ? 'disponibles'
                  : 'correspondant au texte saisi'
              }`
            : 'saisissez du texte pour afficher et filtrer les options'}
        </div>
        <select
          hidden
          {...(multi && { multiple: true })}
          {...field}
          data-testid="select"
        >
          {options?.map(({ label, value }) => (
            <option key={`option-${value}`} value={value}>
              {label}
            </option>
          ))}
        </select>
        <div className={styles['field-overlay']}>
          {!hideArrow && (
            <Toggle
              disabled={disabled}
              isOpen={isOpen}
              toggleField={toggleField}
            />
          )}
          {multi && field.value.length > 0 && (
            <div onClick={toggleField} className={styles['pellet']}>
              {field.value.length}
            </div>
          )}
          {isOpen && (
            <OptionsList
              className={className}
              fieldName={fieldName}
              maxHeight={maxHeight}
              selectedValues={field.value}
              filteredOptions={filteredOptions}
              setHoveredOptionIndex={setHoveredOptionIndex}
              listRef={listRef}
              hoveredOptionIndex={hoveredOptionIndex}
              selectOption={selectOption}
              multi={multi}
            />
          )}
        </div>
      </div>
      {Array.isArray(field.value) && !hideTags && field.value.length > 0 && (
        <Tags
          disabled={disabled}
          fieldName={fieldName}
          optionsLabelById={optionsLabelById}
          selectedOptions={field.value}
          removeOption={selectOption}
        />
      )}
    </FieldLayout>
  )
}

export default SelectAutocomplete
