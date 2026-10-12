"""Asynchronous JSON client for Denkovi smartDEN IP devices."""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant

from .const import MODEL_IP16R_ID, MODEL_IP32IN_ID


class DenkoviApiError(Exception):
    """Base API error."""


class DenkoviConnectionError(DenkoviApiError):
    """Connection or response error."""


class DenkoviAuthenticationError(DenkoviApiError):
    """Authentication failed."""


class DenkoviClient:
    """Client for Denkovi devices using their JSON endpoint."""

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        host: str,
        port: int,
        password: str,
        model: str,
    ) -> None:
        self._hass = hass
        self.host = host
        self.port = port
        self.password = password
        self.model = model
        self._session: aiohttp.ClientSession | None = None
        self._lock = asyncio.Lock()

    @property
    def base_url(self) -> str:
        """Return the device base URL."""
        return f"http://{self.host}:{self.port}"

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def async_close(self) -> None:
        """Close the HTTP session."""
        if self._session is not None and not self._session.closed:
            await self._session.close()

    async def _request(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        query = dict(params or {})
        query["pw"] = self.password
        session = await self._get_session()
        try:
            async with session.get(
                f"{self.base_url}/current_state.json",
                params=query,
                timeout=aiohttp.ClientTimeout(total=8),
            ) as response:
                response.raise_for_status()
                try:
                    data = await response.json(content_type=None)
                except (ValueError, aiohttp.ContentTypeError) as err:
                    raise DenkoviConnectionError("Device returned invalid JSON") from err
        except DenkoviApiError:
            raise
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise DenkoviConnectionError(
                f"Unable to reach {self.host}:{self.port}"
            ) from err

        if not isinstance(data, dict) or not isinstance(data.get("CurrentState"), dict):
            raise DenkoviAuthenticationError(
                "Unexpected JSON response; check password and JSON API settings"
            )
        state = data["CurrentState"]
        if "LoginKey" in state:
            raise DenkoviAuthenticationError(
                "Device rejected authentication or the login session expired"
            )
        return state

    async def async_get_data(self) -> dict[str, Any]:
        """Fetch and parse all data supported by the selected model."""
        async with self._lock:
            state = await self._request()

        if self.model == MODEL_IP16R_ID:
            return {"relays": self._parse_named_values(state.get("Output"), "RELAY", 16, binary=True)}
        if self.model == MODEL_IP32IN_ID:
            return {
                "digital_inputs": self._parse_digital_inputs(
                    state.get("DigitalInput")
                ),
                "analog_inputs": self._parse_measurements(
                    state.get("AnalogInput"), "AI", 8
                ),
                "temperature_inputs": self._parse_measurements(
                    state.get("TemperatureInput"), "TI", 8
                ),
                "device": state.get("Device", {}),
            }
        raise DenkoviConnectionError(f"Unsupported model: {self.model}")

    async def async_get_relays(self) -> dict[int, bool]:
        """Compatibility helper returning relay states."""
        return (await self.async_get_data())["relays"]

    async def async_set_relay(self, relay: int, state: bool) -> None:
        """Set a relay state on an IP-16R."""
        if self.model != MODEL_IP16R_ID:
            raise DenkoviConnectionError("Relay control is only supported on IP-16R")
        if not 1 <= relay <= 16:
            raise ValueError("Relay number must be between 1 and 16")
        async with self._lock:
            await self._request({f"Relay{relay}": int(state)})
            result = await self._request()
        relays = self._parse_named_values(result.get("Output"), "RELAY", 16, binary=True)
        if relays.get(relay) is not state:
            raise DenkoviConnectionError(f"Relay {relay} state verification failed")

    @classmethod
    def _parse_digital_inputs(cls, items: Any) -> dict[int, bool]:
        """Parse IP-32IN digital inputs (firmware uses DI or DIn names)."""
        if not isinstance(items, list):
            raise DenkoviConnectionError("Missing digital input list")
        normalized = []
        for item in items:
            if not isinstance(item, dict):
                continue
            name = item.get("Name")
            if isinstance(name, str):
                if name.startswith("DIn"):
                    name = "DI" + name[3:]
                item = {**item, "Name": name}
            normalized.append(item)
        return cls._parse_named_values(normalized, "DI", 16, binary=True)

    @staticmethod
    def _parse_named_values(
        items: Any, prefix: str, count: int, *, binary: bool
    ) -> dict[int, bool]:
        """Parse named digital states."""
        if not isinstance(items, list):
            raise DenkoviConnectionError(f"Missing {prefix} input/output list")
        values: dict[int, bool] = {}
        for item in items:
            if not isinstance(item, dict):
                continue
            name = item.get("Name")
            if not isinstance(name, str) or not name.startswith(prefix):
                continue
            suffix = name[len(prefix):]
            if not suffix.isdigit():
                continue
            number = int(suffix)
            if not 1 <= number <= count:
                continue
            value = str(item.get("Value", ""))
            if value not in ("0", "1"):
                raise DenkoviConnectionError(f"Invalid binary value for {name}: {value!r}")
            values[number] = value == "1"
        if len(values) != count:
            raise DenkoviConnectionError(
                f"Expected {count} {prefix} values, received {len(values)}"
            )
        return values

    @staticmethod
    def _parse_measurements(items: Any, prefix: str, count: int) -> dict[int, dict[str, Any]]:
        """Parse analog or temperature measurements without inventing unavailable values."""
        if not isinstance(items, list):
            raise DenkoviConnectionError(f"Missing {prefix} measurement list")
        values: dict[int, dict[str, Any]] = {}
        for item in items:
            if not isinstance(item, dict):
                continue
            name = item.get("Name")
            if not isinstance(name, str) or not name.startswith(prefix):
                continue
            suffix = name[len(prefix):]
            if not suffix.isdigit():
                continue
            number = int(suffix)
            if not 1 <= number <= count:
                continue
            raw_value = item.get("Value")
            measure = item.get("Measure")
            parsed_value: float | int | None
            try:
                numeric = float(raw_value)
                parsed_value = int(numeric) if numeric.is_integer() else numeric
            except (TypeError, ValueError):
                parsed_value = None
            values[number] = {
                "name": name,
                "value": parsed_value,
                "measure": measure if isinstance(measure, str) else None,
            }
        if len(values) != count:
            raise DenkoviConnectionError(
                f"Expected {count} {prefix} values, received {len(values)}"
            )
        return values
