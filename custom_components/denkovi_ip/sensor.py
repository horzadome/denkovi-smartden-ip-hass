"""Analog and temperature sensors for Denkovi smartDEN IP-32IN."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
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
    """Set up analog and temperature sensors."""
    if entry.data["model"] != MODEL_IP32IN_ID:
        return
    coordinator: DenkoviCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        DenkoviMeasurementSensor(coordinator, entry, "analog_inputs", n)
        for n in range(1, 9)
    ]
    entities.extend(
        DenkoviMeasurementSensor(coordinator, entry, "temperature_inputs", n)
        for n in range(1, 9)
    )
    async_add_entities(entities)


class DenkoviMeasurementSensor(CoordinatorEntity[DenkoviCoordinator], SensorEntity):
    """Represent one analog or temperature input."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: DenkoviCoordinator, entry: ConfigEntry, input_type: str, number: int
    ) -> None:
        super().__init__(coordinator)
        self._input_type = input_type
        self._number = number
        label = "Analog input" if input_type == "analog_inputs" else "Temperature input"
        prefix = "analog" if input_type == "analog_inputs" else "temperature"
        self._attr_unique_id = f"{entry.entry_id}_{prefix}_{number}"
        self._attr_name = f"{label} {number}"
        if input_type == "temperature_inputs":
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_icon = "mdi:thermometer" if input_type == "temperature_inputs" else "mdi:chart-bell-curve"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer=MANUFACTURER,
            model=MODEL_IP32IN,
            configuration_url=coordinator.client.base_url,
        )

    @property
    def native_value(self) -> float | int | None:
        """Return numeric measurement; unavailable values are represented as None."""
        value = self.coordinator.data.get(self._input_type, {}).get(self._number, {})
        return value.get("value")

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Expose the device's configured measurement label/unit."""
        value = self.coordinator.data.get(self._input_type, {}).get(self._number, {})
        measure = value.get("measure")
        return {"device_measure": measure} if measure else {}
