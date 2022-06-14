"""Support for number settings on VeSync devices."""
import logging

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .common import VeSyncBaseEntity, is_air_purifier, is_humidifier
from .const import DOMAIN, VS_DISCOVERY, VS_NUMBERS

MAX_HUMIDITY = 80
MIN_HUMIDITY = 30

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up numbers."""

    @callback
    def discover(devices):
        """Add new devices to platform."""
        _setup_entities(devices, async_add_entities)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, VS_DISCOVERY.format(VS_NUMBERS), discover)
    )

    _setup_entities(
        hass.data[DOMAIN][config_entry.entry_id][VS_NUMBERS], async_add_entities
    )


@callback
def _setup_entities(devices, async_add_entities):
    """Check if device is online and add entity."""
    entities = []
    for dev in devices:
        if is_humidifier(dev.device_type):
            ext = (VeSyncHumidifierMistLevelHA(dev), VeSyncHumidifierTargetLevelHA(dev))
            if dev.warm_mist_feature:
                ext = (*ext, VeSyncHumidifierWarmthLevelHA(dev))
            entities.extend(ext)
        elif is_air_purifier(dev.device_type):
            entities.extend((VeSyncFanSpeedLevelHA(dev),))
        else:
            _LOGGER.debug(
                "%s - Unknown device type - %s", dev.device_name, dev.device_type
            )
            continue

    async_add_entities(entities, update_before_add=True)


class VeSyncFanNumberEntity(VeSyncBaseEntity, NumberEntity):
    """Representation of a number for configuring a VeSync fan."""

    def __init__(self, fan):
        """Initialize the VeSync fan device."""
        super().__init__(fan)
        self.smartfan = fan

    @property
    def entity_category(self):
        """Return the diagnostic entity category."""
        return EntityCategory.CONFIG


class VeSyncFanSpeedLevelHA(VeSyncFanNumberEntity):
    """Representation of the fan speed level of a VeSync fan."""

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return f"{super().unique_id}-fan-speed-level"

    @property
    def name(self):
        """Return the name of the device."""
        return f"{super().name} fan speed level"

    @property
    def value(self):
        """Return the fan speed level."""
        return self.device.speed

    @property
    def min_value(self) -> float:
        """Return the minimum fan speed level."""
        return self.device.config_dict["levels"][0]

    @property
    def max_value(self) -> float:
        """Return the maximum fan speed level."""
        return self.device.config_dict["levels"][-1]

    @property
    def step(self) -> float:
        """Return the steps for the fan speed level."""
        return 1.0

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the humidifier."""
        return {"fan speed levels": self.device.config_dict["levels"]}

    def set_value(self, value):
        """Set the fan speed level."""
        self.device.change_fan_speed(int(value))


class VeSyncHumidifierNumberEntity(VeSyncBaseEntity, NumberEntity):
    """Representation of a number for configuring a VeSync humidifier."""

    def __init__(self, humidifier):
        """Initialize the VeSync humidifier device."""
        super().__init__(humidifier)
        self.smarthumidifier = humidifier

    @property
    def entity_category(self):
        """Return the diagnostic entity category."""
        return EntityCategory.CONFIG


class VeSyncHumidifierMistLevelHA(VeSyncHumidifierNumberEntity):
    """Representation of the mist level of a VeSync humidifier."""

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return f"{super().unique_id}-mist-level"

    @property
    def name(self):
        """Return the name of the device."""
        return f"{super().name} mist level"

    @property
    def value(self):
        """Return the mist level."""
        return self.device.details["mist_virtual_level"]

    @property
    def min_value(self) -> float:
        """Return the minimum mist level."""
        return self.device.config_dict["mist_levels"][0]

    @property
    def max_value(self) -> float:
        """Return the maximum mist level."""
        return self.device.config_dict["mist_levels"][-1]

    @property
    def step(self) -> float:
        """Return the steps for the mist level."""
        return 1.0

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the humidifier."""
        return {"mist levels": self.device.config_dict["mist_levels"]}

    def set_value(self, value):
        """Set the mist level."""
        self.device.set_mist_level(int(value))


class VeSyncHumidifierWarmthLevelHA(VeSyncHumidifierNumberEntity):
    """Representation of the warmth level of a VeSync humidifier."""

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return f"{super().unique_id}-warmth-level"

    @property
    def name(self):
        """Return the name of the device."""
        return f"{super().name} warmth level"

    @property
    def value(self):
        """Return the warmth level."""
        return self.device.details["warm_mist_level"]

    @property
    def min_value(self) -> float:
        """Return the minimum mist level."""
        return self.device.config_dict["warm_mist_levels"][0]

    @property
    def max_value(self) -> float:
        """Return the maximum mist level."""
        return self.device.config_dict["warm_mist_levels"][-1]

    @property
    def step(self) -> float:
        """Return the steps for the mist level."""
        return 1.0

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the humidifier."""
        return {"warmth levels": self.device.config_dict["warm_mist_levels"]}

    def set_value(self, value):
        """Set the mist level."""
        self.device.set_warm_level(int(value))


class VeSyncHumidifierTargetLevelHA(VeSyncHumidifierNumberEntity):
    """Representation of the target humidity level of a VeSync humidifier."""

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return f"{super().unique_id}-target-level"

    @property
    def name(self):
        """Return the name of the device."""
        return f"{super().name} target level"

    @property
    def value(self):
        """Return the current target humidity level."""
        return self.device.config["auto_target_humidity"]

    @property
    def min_value(self) -> float:
        """Return the minimum humidity level."""
        return MIN_HUMIDITY

    @property
    def max_value(self) -> float:
        """Return the maximum humidity level."""
        return MAX_HUMIDITY

    @property
    def step(self) -> float:
        """Return the humidity change step."""
        return 1.0

    def set_value(self, value):
        """Set the target humidity level."""
        self.device.set_humidity(int(value))
