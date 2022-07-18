"""Common utilities for VeSync Component."""
import logging

from homeassistant.helpers.entity import Entity, ToggleEntity
from pyvesync.vesyncfan import model_features

from .const import (
    DOMAIN,
    VS_BINARY_SENSORS,
    VS_FANS,
    VS_HUMIDIFIERS,
    VS_LIGHTS,
    VS_NUMBERS,
    VS_SENSORS,
    VS_SWITCHES,
)

_LOGGER = logging.getLogger(__name__)


def is_humidifier(device_type: str) -> bool:
    """Return true if the device type is a humidifier."""
    return model_features(device_type)["module"].find("VeSyncHumid") > -1


def is_air_purifier(device_type: str) -> bool:
    """Return true if the device type is a an air purifier."""
    return model_features(device_type)["module"].find("VeSyncAirBypass") > -1


async def async_process_devices(hass, manager):
    """Assign devices to proper component."""
    devices = {
        VS_SWITCHES: [],
        VS_FANS: [],
        VS_LIGHTS: [],
        VS_SENSORS: [],
        VS_HUMIDIFIERS: [],
        VS_NUMBERS: [],
        VS_BINARY_SENSORS: [],
    }

    await hass.async_add_executor_job(manager.update)

    if manager.fans:
        for fan in manager.fans:
            # VeSync classifies humidifiers as fans
            _LOGGER.debug("Found a fan: %s", fan.__dict__)
            if is_humidifier(fan.device_type):
                devices[VS_HUMIDIFIERS].append(fan)
            else:
                devices[VS_FANS].append(fan)
            devices[VS_NUMBERS].append(fan)  # for night light and mist level
            devices[VS_SWITCHES].append(fan)  # for automatic stop and display
            devices[VS_SENSORS].append(fan)  # for humidity sensor
            devices[VS_BINARY_SENSORS].append(
                fan
            )  # for out of water and water tank lifted sensors
            devices[VS_LIGHTS].append(fan)  # for night light

        _LOGGER.info("%d VeSync fans found", len(manager.fans))

    if manager.bulbs:
        devices[VS_LIGHTS].extend(manager.bulbs)
        _LOGGER.info("%d VeSync lights found", len(manager.bulbs))

    if manager.outlets:
        devices[VS_SWITCHES].extend(manager.outlets)
        # Expose outlets' power & energy usage as separate sensors
        devices[VS_SENSORS].extend(manager.outlets)
        _LOGGER.info("%d VeSync outlets found", len(manager.outlets))

    if manager.switches:
        for switch in manager.switches:
            if not switch.is_dimmable():
                devices[VS_SWITCHES].append(switch)
            else:
                devices[VS_LIGHTS].append(switch)
        _LOGGER.info("%d VeSync switches found", len(manager.switches))

    return devices


class VeSyncBaseEntity(Entity):
    """Base class for VeSync Entity Representations."""

    def __init__(self, device):
        """Initialize the VeSync device."""
        self.device = device

    @property
    def base_unique_id(self):
        """Return the ID of this device."""
        if isinstance(self.device.sub_device_no, int):
            return f"{self.device.cid}{str(self.device.sub_device_no)}"
        return self.device.cid

    @property
    def unique_id(self):
        """Return the ID of this device."""
        # The unique_id property may be overridden in subclasses, such as in sensors. Maintaining base_unique_id allows
        # us to group related entities under a single device.
        return self.base_unique_id

    @property
    def base_name(self):
        """Return the name of the device."""
        return self.device.device_name

    @property
    def name(self):
        """Return the name of the entity (may be overridden)."""
        return self.base_name

    @property
    def available(self) -> bool:
        """Return True if device is available."""
        return self.device.connection_status == "online"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.base_unique_id)},
            "name": self.base_name,
            "model": self.device.device_type,
            "default_manufacturer": "VeSync",
            "sw_version": self.device.current_firm_version,
        }

    def update(self):
        """Update vesync device."""
        self.device.update()


class VeSyncDevice(VeSyncBaseEntity, ToggleEntity):
    """Base class for VeSync Device Representations."""

    @property
    def is_on(self):
        """Return True if device is on."""
        return self.device.device_status == "on"

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self.device.turn_off()
