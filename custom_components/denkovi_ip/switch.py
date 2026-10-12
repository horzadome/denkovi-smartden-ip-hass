"""Switch platform for Denkovi smartDEN IP Devices."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import DenkoviApiError
from .const import DOMAIN, MANUFACTURER, MODEL_IP16R, MODEL_IP16R_ID
from .coordinator import DenkoviCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up relay switches."""
    coordinator: DenkoviCoordinator = hass.data[DOMAIN][entry.entry_id]
    if entry.data["model"] == MODEL_IP16R_ID:
        async_add_entities(
            DenkoviRelaySwitch(coordinator, entry, relay)
            for relay in range(1, 17)
        )


class DenkoviRelaySwitch(CoordinatorEntity[DenkoviCoordinator], SwitchEntity):
    """Represent one IP-16R relay."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:electric-switch"

    def __init__(
        self, coordinator: DenkoviCoordinator, entry: ConfigEntry, relay: int
    ) -> None:
        super().__init__(coordinator)
        self._relay = relay
        self._attr_unique_id = f"{entry.entry_id}_relay_{relay}"
        self._attr_name = f"Relay {relay}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer=MANUFACTURER,
            model=MODEL_IP16R,
            configuration_url=coordinator.client.base_url,
        )

    @property
    def is_on(self) -> bool | None:
        """Return current relay state."""
        return self.coordinator.data.get("relays", {}).get(self._relay)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the relay on."""
        await self._set_state(True)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the relay off."""
        await self._set_state(False)

    async def _set_state(self, state: bool) -> None:
        try:
            await self.coordinator.client.async_set_relay(self._relay, state)
            await self.coordinator.async_request_refresh()
        except DenkoviApiError as err:
            raise HomeAssistantError(
                f"Failed to set Denkovi relay {self._relay}"
            ) from err
