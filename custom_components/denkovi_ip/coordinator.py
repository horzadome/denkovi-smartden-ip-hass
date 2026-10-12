"""Data update coordinator for Denkovi smartDEN IP Devices."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DenkoviApiError, DenkoviClient
from .const import CONF_MODEL, CONF_PORT, CONF_SCAN_INTERVAL, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

type DenkoviConfigEntry = ConfigEntry[DenkoviClient]


class DenkoviCoordinator(DataUpdateCoordinator[dict]):
    """Coordinate polling and commands for a Denkovi device."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.client = DenkoviClient(
            hass,
            host=entry.data[CONF_HOST],
            port=entry.data.get(CONF_PORT, DEFAULT_PORT),
            password=entry.data[CONF_PASSWORD],
            model=entry.data[CONF_MODEL],
        )
        interval = entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=interval),
            config_entry=entry,
        )

    async def _async_update_data(self) -> dict[int, bool]:
        """Fetch relay states."""
        try:
            return await self.client.async_get_data()
        except DenkoviApiError as err:
            raise UpdateFailed(str(err)) from err
