"""Tests for the EVSE Load Balancer number platform."""

import asyncio
from unittest.mock import MagicMock

import pytest

from custom_components.evse_load_balancer.number import MaxChargerCurrentNumber


@pytest.fixture
def coordinator():
    """Return a coordinator stub for number entity tests."""
    coordinator = MagicMock()
    coordinator.config_entry.entry_id = "test_entry"
    coordinator.max_charger_current = 16
    coordinator.set_max_charger_current = MagicMock()
    return coordinator


def test_max_charger_current_number_range(coordinator) -> None:
    """The current control exposes the requested 1–32 A range."""
    number = MaxChargerCurrentNumber(coordinator)

    assert number.native_min_value == 1
    assert number.native_max_value == 32
    assert number.native_step == 1
    assert number.native_unit_of_measurement == "A"
    assert number.native_value == 16


def test_setting_number_updates_coordinator(coordinator) -> None:
    """A slider change updates the allocator's runtime cap."""
    number = MaxChargerCurrentNumber(coordinator)

    asyncio.run(number.async_set_native_value(10))

    coordinator.set_max_charger_current.assert_called_once_with(10)
    assert number.native_value == 10


@pytest.mark.parametrize("value", [0, 10.5, 33])
def test_setting_number_rejects_out_of_range_value(coordinator, value) -> None:
    """Reject values outside the exposed slider range."""
    number = MaxChargerCurrentNumber(coordinator)

    expected_message = "whole number of amps" if value == 10.5 else "between 1 and 32 A"
    with pytest.raises(ValueError, match=expected_message):
        asyncio.run(number.async_set_native_value(value))

    coordinator.set_max_charger_current.assert_not_called()
