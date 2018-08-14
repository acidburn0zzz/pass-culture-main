from unittest.mock import Mock

import pytest

from domain.expenses import get_expenses
from models import Booking, Thing, Offer, Stock, Event
from utils.test_utils import create_user


@pytest.mark.standalone
def test_get_expenses_returns_max_500_and_actual_150_at_for_all_bookings():
    # Given
    user = create_user()
    booking_1 = create_booking_for_thing(amount=90)
    booking_2 = create_booking_for_event(amount=60)
    find_bookings_by_user_id = Mock(return_value=[booking_1, booking_2])

    # When
    expenses = get_expenses(user, find_bookings_by_user_id=find_bookings_by_user_id)

    # Then
    assert expenses['all'] == {'max': 500, 'actual': 150}


@pytest.mark.standalone
def test_get_expenses_returns_max_100_and_actual_50_for_physical_bookings():
    # Given
    user = create_user()
    booking_1 = create_booking_for_thing(amount=50)
    booking_2 = create_booking_for_thing(url='http://test.com', amount=60)

    find_bookings_by_user_id = Mock(return_value=[booking_1, booking_2])

    # When
    expenses = get_expenses(user, find_bookings_by_user_id=find_bookings_by_user_id)

    # Then
    assert expenses['physical'] == {'max': 100, 'actual': 50}


@pytest.mark.standalone
def test_get_expenses_returns_max_200_and_actual_110_for_digital_bookings():
    # Given
    user = create_user()
    booking_1 = create_booking_for_thing(amount=50)
    booking_2 = create_booking_for_thing(url='http://test.com', amount=110)

    find_bookings_by_user_id = Mock(return_value=[booking_1, booking_2])

    # When
    expenses = get_expenses(user, find_bookings_by_user_id=find_bookings_by_user_id)

    # Then
    assert expenses['digital'] == {'max': 200, 'actual': 110}


def create_booking_for_thing(url=None, amount=50):
    thing = Thing(from_dict={'url': url})
    offer = Offer()
    stock = Stock()
    booking = Booking(from_dict={'amount': amount})
    offer.thing = thing
    stock.offer = offer
    booking.stock = stock
    return booking


def create_booking_for_event(amount=50):
    event = Event()
    offer = Offer()
    stock = Stock()
    booking = Booking(from_dict={'amount': amount})
    offer.event = event
    stock.offer = offer
    booking.stock = stock
    return booking
