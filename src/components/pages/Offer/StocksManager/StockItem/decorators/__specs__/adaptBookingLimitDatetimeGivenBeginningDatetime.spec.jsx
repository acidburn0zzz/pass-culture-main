import { mount } from 'enzyme'
import React from 'react'
import { Field, Form } from 'react-final-form'

import adaptBookingLimitDatetimeGivenBeginningDatetime from '../adaptBookingLimitDatetimeGivenBeginningDatetime'

describe('src | pages | Offer | StocksManager | StockItem | decorators | adaptaBookingLimitDatetimeGivenBeginningDatetime', () => {
  const onSubmitMock = jest.fn()
  describe('when beginningDatetime is not the same day that bookingLimitDatetime', () => {
    it('should set bookingLimitDatetime at 23h59 plus 3 hours for america/cayenne (because utc)', () => {
      // given
      const initialValues = {
        beginningDatetime: '2019-04-28T19:00:00.000Z',
        bookingLimitDatetime: '2019-04-20T15:00:00.000Z',
      }

      // when
      const wrapper = mount(
        <Form
          decorators={[
            adaptBookingLimitDatetimeGivenBeginningDatetime({
              isEvent: true,
              timezone: 'America/Cayenne',
            }),
          ]}
          initialValues={initialValues}
          onSubmit={onSubmitMock}
          render={({ handleSubmit }) => (
            <form>
              <Field
                name="beginningDatetime"
                render={({ input }) => <input {...input} />}
              />
              <Field
                name="bookingLimitDatetime"
                render={({ input }) => <input {...input} />}
              />
              <button
                onClick={handleSubmit}
                type="submit"
              >
                {'Submit'}
              </button>
            </form>
          )}
        />
      )

      // then
      const input = wrapper
        .find(Field)
        .find({ name: 'bookingLimitDatetime' })
        .find('input')
      expect(input.props().value).toStrictEqual('2019-04-21T02:59:00.000Z')
    })
  })

  describe('when beginningDatetime is the same day that bookingLimitDatetime', () => {
    it('should put bookingLimitDatetime the same value than beginningDatetime no matter the timezone', () => {
      // given
      const initialValues = {
        beginningDatetime: '2020-01-18T19:00:59.984000Z',
        bookingLimitDatetime: '2020-01-18T19:00:59.984000Z',
      }

      // when
      const wrapper = mount(
        <Form
          decorators={[
            adaptBookingLimitDatetimeGivenBeginningDatetime({
              isEvent: true,
              timezone: 'Europe/Paris',
            }),
          ]}
          initialValues={initialValues}
          onSubmit={onSubmitMock}
          render={({ handleSubmit }) => (
            <form>
              <Field
                name="beginningDatetime"
                render={({ input }) => <input {...input} />}
              />
              <Field
                name="bookingLimitDatetime"
                render={({ input }) => <input {...input} />}
              />
              <Field
                name="beginningTime"
                render={({ input }) => <input {...input} />}
              />
              <button
                onClick={handleSubmit}
                type="submit"
              >
                {'Submit'}
              </button>
            </form>
          )}
        />
      )

      const inputBookingLimitDatetime = wrapper
        .find(Field)
        .find({ name: 'bookingLimitDatetime' })
        .find('input')

      // then
      expect(inputBookingLimitDatetime.props().value).toStrictEqual("2020-01-18T19:00:59.984000Z")
    })
  })
})
