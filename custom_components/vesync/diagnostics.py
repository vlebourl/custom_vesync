"""Provides diagnostics for VeSync."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


def _if_has_attr_else_none(obj, attr):
    return getattr(obj, attr) if hasattr(obj, attr) else None


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
                    "config_dict": _if_has_attr_else_none(d, "config_dict") or {},
                    "config": _if_has_attr_else_none(d, "config") or {},
                    "details": _if_has_attr_else_none(d, "details") or {},
                }
            )
    return devices
