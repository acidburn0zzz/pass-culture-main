import cn from 'classnames'
import React, { useState, useCallback } from 'react'

import { PriceCategoryResponseModel } from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { useOfferWizardMode } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
import { TrashFilledIcon } from 'icons'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Pagination } from 'ui-kit/Pagination'
import { formatPrice } from 'utils/formatPrice'
import { formatLocalTimeDateString } from 'utils/timezone'

import styles from './StocksEventList.module.scss'

const STOCKS_PER_PAGE = 20

export interface IStocksEvent {
  id?: string
  beginningDatetime: string
  bookingLimitDatetime: string
  priceCategoryId: number
  quantity: number | null
}

interface IStocksEventListProps {
  stocks: IStocksEvent[]
  priceCategories: PriceCategoryResponseModel[]
  className?: string
  departmentCode?: string
  offerId: string
  setStocks: (stocks: IStocksEvent[]) => void
}

const sortStocks = (stocks: IStocksEvent[]): IStocksEvent[] => {
  return stocks.sort(
    (a, b) => Date.parse(a.beginningDatetime) - Date.parse(b.beginningDatetime)
  )
}

const StocksEventList = ({
  stocks,
  priceCategories,
  className,
  departmentCode,
  offerId,
  setStocks,
}: IStocksEventListProps): JSX.Element => {
  const mode = useOfferWizardMode()
  const { logEvent } = useAnalytics()
  const [isCheckedArray, setIsCheckedArray] = useState<boolean[]>(
    Array(stocks.length).fill(false)
  )
  const [page, setPage] = useState(1)
  const previousPage = useCallback(() => setPage(page => page - 1), [])
  const nextPage = useCallback(() => setPage(page => page + 1), [])
  const stocksPage = sortStocks(stocks).slice(
    (page - 1) * STOCKS_PER_PAGE,
    page * STOCKS_PER_PAGE
  )
  const areAllChecked = isCheckedArray.every(isChecked => isChecked)

  const handleOnChangeSelected = (index: number) => {
    const newArray = isCheckedArray.map(isChecked => isChecked)
    newArray[index] = !newArray[index]
    setIsCheckedArray(newArray)
  }

  const handleOnChangeSelectAll = () => {
    if (areAllChecked) {
      setIsCheckedArray(stocks.map(() => false))
    } else {
      setIsCheckedArray(stocks.map(() => true))
    }
  }

  const onDeleteStock = (index: number) => {
    // handle checkbox selection
    const newArray = [...isCheckedArray]
    newArray.splice(index, 1)
    setIsCheckedArray(newArray)

    stocks.splice(index, 1)
    setStocks([...stocks])
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_WIZARD_STEP_IDS.STOCKS,
      to: OFFER_WIZARD_STEP_IDS.STOCKS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.STOCK_EVENT_DELETE,
      isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
      isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
      offerId: offerId,
    })
  }

  const onBulkDelete = () => {
    const newStocks = stocks.filter((stock, index) => !isCheckedArray[index])
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_WIZARD_STEP_IDS.STOCKS,
      to: OFFER_WIZARD_STEP_IDS.STOCKS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.STOCK_EVENT_BULK_DELETE,
      isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
      isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
      offerId: offerId,
      deletionCount: `${stocks.length - newStocks.length}`,
    })
    setIsCheckedArray(stocks.map(() => false))
    setStocks([...newStocks])
  }

  const onCancelClick = () => {
    setIsCheckedArray(stocks.map(() => false))
  }

  const selectedDateText =
    isCheckedArray.filter(e => e === true).length > 1
      ? `${isCheckedArray.filter(e => e === true).length} dates sélectionnées`
      : '1 date sélectionnée'

  const isAtLeastOneStockChecked = isCheckedArray.some(e => e)

  return (
    <>
      <table className={cn(styles['stock-event-table'], className)}>
        <caption className={styles['table-caption']}>
          Liste des dates et capacités
        </caption>
        <thead>
          <tr>
            <th
              scope="col"
              className={cn(styles['checkbox-column'], styles['header'])}
            >
              <input
                checked={areAllChecked}
                onChange={handleOnChangeSelectAll}
                type="checkbox"
                aria-label="Sélectionner toutes les lignes"
              />
            </th>
            <th
              scope="col"
              className={cn(styles['date-column'], styles['header'])}
            >
              Date
            </th>
            <th
              scope="col"
              className={cn(styles['time-column'], styles['header'])}
            >
              Horaire
            </th>
            <th scope="col" className={styles['header']}>
              Tarif
            </th>
            <th
              scope="col"
              className={cn(
                styles['booking-limit-date-column'],
                styles['header']
              )}
            >
              Date limite
              <br />
              de réservation
            </th>
            <th
              scope="col"
              className={cn(styles['quantity-column'], styles['header'])}
            >
              Places
            </th>
            <th className={cn(styles['actions-column'], styles['header'])} />
          </tr>
        </thead>

        <tbody>
          {stocksPage.map((stock, index) => {
            const beginningDay = formatLocalTimeDateString(
              stock.beginningDatetime,
              departmentCode,
              'eee'
            ).replace('.', '')

            const beginningDate = formatLocalTimeDateString(
              stock.beginningDatetime,
              departmentCode,
              'dd/MM/yyyy'
            )

            const beginningHour = formatLocalTimeDateString(
              stock.beginningDatetime,
              departmentCode,
              'HH:mm'
            )
            const bookingLimitDate = formatLocalTimeDateString(
              stock.bookingLimitDatetime,
              departmentCode,
              'dd/MM/yyyy'
            )
            const priceCategory = priceCategories.find(
              pC => pC.id === stock.priceCategoryId
            )

            let price = ''
            /* istanbul ignore next priceCategory would never be null */
            if (priceCategory) {
              price = `${formatPrice(priceCategory.price)} - ${
                priceCategory?.label
              }`
            }

            return (
              <tr key={index} className={styles['row']}>
                <td className={styles['data']}>
                  <input
                    checked={isCheckedArray[index]}
                    onChange={() => handleOnChangeSelected(index)}
                    type="checkbox"
                  />
                </td>
                <td className={cn(styles['data'], styles['capitalize'])}>
                  <div className={styles['date-cell-wrapper']}>
                    <div className={styles['day']}>
                      <strong>{beginningDay}</strong>
                    </div>
                    <div>{beginningDate}</div>
                  </div>
                </td>
                <td className={styles['data']}>{beginningHour}</td>
                <td className={styles['data']}>{price}</td>
                <td className={styles['data']}>{bookingLimitDate}</td>
                <td className={styles['data']}>
                  {stock.quantity === null ? 'Illimité' : stock.quantity}
                </td>
                <td className={cn(styles['data'], styles['clear-icon'])}>
                  <Button
                    variant={ButtonVariant.TERNARY}
                    onClick={() => onDeleteStock(index)}
                    Icon={TrashFilledIcon}
                    hasTooltip
                  >
                    Supprimer
                  </Button>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>

      <Pagination
        currentPage={page}
        pageCount={Math.ceil(stocks.length / STOCKS_PER_PAGE)}
        onPreviousPageClick={previousPage}
        onNextPageClick={nextPage}
      />

      {isAtLeastOneStockChecked && (
        <ActionsBarSticky className={styles['actions']}>
          <ActionsBarSticky.Left>{selectedDateText}</ActionsBarSticky.Left>
          <ActionsBarSticky.Right>
            {
              <>
                <Button
                  onClick={onCancelClick}
                  variant={ButtonVariant.SECONDARY}
                >
                  Annuler
                </Button>
                <Button onClick={onBulkDelete}>Supprimer ces dates</Button>
              </>
            }
          </ActionsBarSticky.Right>
        </ActionsBarSticky>
      )}
    </>
  )
}

export default StocksEventList
