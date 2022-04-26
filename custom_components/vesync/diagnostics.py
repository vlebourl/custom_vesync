"""Provides diagnostics for VeSync."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    devices = {"fans": [], "outlets": [], "switches": [], "bulbs": []}
    for type in ["fans", "outlets", "switches", "bulbs"]:
        for d in data["manager"]._dev_list[type]:
            devices[type].append(
                {
                    "device": d.config_dict or {},
                    "config": d.config or {},
                    "details": d.details or {},
                }
            )
    return devices
