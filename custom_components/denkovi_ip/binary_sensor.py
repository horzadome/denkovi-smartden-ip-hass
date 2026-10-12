"""Binary sensors for the Denkovi smartDEN IP-32IN."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL_IP32IN, MODEL_IP32IN_ID
from .coordinator import DenkoviCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up digital input entities."""
    if entry.data["model"] != MODEL_IP32IN_ID:
        return
    coordinator: DenkoviCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        DenkoviDigitalInput(coordinator, entry, number)
        for number in range(1, 17)
    )


class DenkoviDigitalInput(CoordinatorEntity[DenkoviCoordinator], BinarySensorEntity):
    """Represent one digital input."""

    _attr_has_entity_name = True
    _attr_device_class = None
    _attr_icon = "mdi:sign-direction"

    def __init__(self, coordinator: DenkoviCoordinator, entry: ConfigEntry, number: int) -> None:
        super().__init__(coordinator)
        self._number = number
        self._attr_unique_id = f"{entry.entry_id}_digital_input_{number}"
        self._attr_name = f"Digital input {number}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer=MANUFACTURER,
            model=MODEL_IP32IN,
            configuration_url=coordinator.client.base_url,
        )

    @property
    def is_on(self) -> bool | None:
        """Return the input state."""
        return self.coordinator.data.get("digital_inputs", {}).get(self._number)
