"""EVSE Load Balancer number platform."""

from collections.abc import Callable

from homeassistant import config_entries, core
from homeassistant.components.number import (
    NumberEntityDescription,
    NumberMode,
    RestoreNumber,
)
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .coordinator import EVSELoadBalancerCoordinator

MAX_CHARGER_CURRENT = 32
MIN_CHARGER_CURRENT = 1


class MaxChargerCurrentNumber(RestoreNumber):
    """Number entity for the EVSE's manual maximum charging current."""

    entity_description = NumberEntityDescription(
        key="max_charger_current",
        translation_key="evse_max_charger_current",
        native_min_value=MIN_CHARGER_CURRENT,
        native_max_value=MAX_CHARGER_CURRENT,
        native_step=1,
        native_unit_of_measurement="A",
        mode=NumberMode.SLIDER,
    )

    def __init__(self, coordinator: EVSELoadBalancerCoordinator) -> None:
        """Initialize the current limit control."""
        super().__init__()
        self._coordinator = coordinator
        self._attr_has_entity_name = True
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_max_charger_current"
        )
        self._attr_native_value = coordinator.max_charger_current
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name="EVSE Load Balancer",
            manufacturer="EnergyLabs",
            configuration_url="https://github.com/dirkgroenen/hass-evse-load-balancer",
        )

    async def async_added_to_hass(self) -> None:
        """Restore the previous value and apply it to the coordinator."""
        await super().async_added_to_hass()
        restored_data = await self.async_get_last_number_data()
        if restored_data is None or restored_data.native_value is None:
            return

        restored_current = int(restored_data.native_value)
        if MIN_CHARGER_CURRENT <= restored_current <= MAX_CHARGER_CURRENT:
            self._attr_native_value = restored_current
            self._coordinator.set_max_charger_current(restored_current)

    async def async_set_native_value(self, value: float) -> None:
        """Set the EVSE's manual maximum charging current."""
        if not value.is_integer():
            msg = "Maximum charger current must be a whole number of amps"
            raise ValueError(msg)
        current_limit = int(value)
        if not MIN_CHARGER_CURRENT <= current_limit <= MAX_CHARGER_CURRENT:
            msg = (
                f"Maximum charger current must be between "
                f"{MIN_CHARGER_CURRENT} and {MAX_CHARGER_CURRENT} A"
            )
            raise ValueError(msg)

        self._attr_native_value = current_limit
        self._coordinator.set_max_charger_current(current_limit)
        if self.hass is not None:
            self.async_write_ha_state()


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities: Callable,
) -> None:
    """Set up the EVSE current limit number entity."""
    coordinator: EVSELoadBalancerCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([MaxChargerCurrentNumber(coordinator)], update_before_add=False)
