"""Support for number settings on VeSync devices."""

from homeassistant.components.number import NumberEntity
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .common import VeSyncBaseEntity, has_feature
from .const import DOMAIN, VS_DISCOVERY, VS_NUMBERS

MAX_HUMIDITY = 80
MIN_HUMIDITY = 30


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up numbers."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]

    @callback
    def discover(devices):
        """Add new devices to platform."""
        _setup_entities(devices, async_add_entities, coordinator)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, VS_DISCOVERY.format(VS_NUMBERS), discover)
    )

    _setup_entities(
        hass.data[DOMAIN][config_entry.entry_id][VS_NUMBERS],
        async_add_entities,
        coordinator,
    )


@callback
def _setup_entities(devices, async_add_entities, coordinator):
    """Check if device is online and add entity."""
    entities = []
    for dev in devices:
        if has_feature(dev, "details", "mist_virtual_level"):
            entities.append(VeSyncHumidifierMistLevelHA(dev, coordinator))
        if has_feature(dev, "config", "auto_target_humidity"):
            entities.append(VeSyncHumidifierTargetLevelHA(dev, coordinator))
        if has_feature(dev, "details", "warm_mist_level"):
            entities.append(VeSyncHumidifierWarmthLevelHA(dev, coordinator))
        if has_feature(dev, "config_dict", "levels"):
            entities.append(VeSyncFanSpeedLevelHA(dev, coordinator))

    async_add_entities(entities, update_before_add=True)


class VeSyncNumberEntity(VeSyncBaseEntity, NumberEntity):
    """Representation of a number for configuring a VeSync fan."""

    def __init__(self, device, coordinator) -> None:
        """Initialize the VeSync fan device."""
        super().__init__(device, coordinator)

    @property
    def entity_category(self):
        """Return the diagnostic entity category."""
        return EntityCategory.CONFIG


class VeSyncFanSpeedLevelHA(VeSyncNumberEntity):
    """Representation of the fan speed level of a VeSync fan."""

    def __init__(self, device, coordinator) -> None:
        """Initialize the number entity."""
        super().__init__(device, coordinator)
        self._attr_native_min_value = device.config_dict["levels"][0]
        self._attr_native_max_value = device.config_dict["levels"][-1]
        self._attr_native_step = 1

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return f"{super().unique_id}-fan-speed-level"

    @property
    def name(self):
        """Return the name of the device."""
        return f"{super().name} fan speed level"

    @property
    def native_value(self):
        """Return the fan speed level."""
        return self.device.speed

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the humidifier."""
        return {"fan speed levels": self.device.config_dict["levels"]}

    def set_native_value(self, value):
        """Set the fan speed level."""
        self.device.change_fan_speed(int(value))


class VeSyncHumidifierMistLevelHA(VeSyncNumberEntity):
    """Representation of the mist level of a VeSync humidifier."""

    def __init__(self, device, coordinator) -> None:
        """Initialize the number entity."""
        super().__init__(device, coordinator)
        self._attr_native_min_value = device.config_dict["mist_levels"][0]
        self._attr_native_max_value = device.config_dict["mist_levels"][-1]
        self._attr_native_step = 1

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return f"{super().unique_id}-mist-level"

    @property
    def name(self):
        """Return the name of the device."""
        return f"{super().name} mist level"

    @property
    def native_value(self):
        """Return the mist level."""
        return self.device.details["mist_virtual_level"]

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the humidifier."""
        return {"mist levels": self.device.config_dict["mist_levels"]}

    def set_native_value(self, value):
        """Set the mist level."""
        self.device.set_mist_level(int(value))


class VeSyncHumidifierWarmthLevelHA(VeSyncNumberEntity):
    """Representation of the warmth level of a VeSync humidifier."""

    def __init__(self, device, coordinator) -> None:
        """Initialize the number entity."""
        super().__init__(device, coordinator)
        self._attr_native_min_value = device.config_dict["warm_mist_levels"][0]
        self._attr_native_max_value = device.config_dict["warm_mist_levels"][-1]
        self._attr_native_step = 1

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return f"{super().unique_id}-warm-mist"

    @property
    def name(self):
        """Return the name of the device."""
        return f"{super().name} warm mist"

    @property
    def native_value(self):
        """Return the warmth level."""
        return self.device.details["warm_mist_level"]

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the humidifier."""
        return {"warm mist levels": self.device.config_dict["warm_mist_levels"]}

    def set_native_value(self, value):
        """Set the mist level."""
        self.device.set_warm_level(int(value))


class VeSyncHumidifierTargetLevelHA(VeSyncNumberEntity):
    """Representation of the target humidity level of a VeSync humidifier."""

    def __init__(self, device, coordinator) -> None:
        """Initialize the number entity."""
        super().__init__(device, coordinator)
        self._attr_native_min_value = MIN_HUMIDITY
        self._attr_native_max_value = MAX_HUMIDITY
        self._attr_native_step = 1

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return f"{super().unique_id}-target-level"

    @property
    def name(self):
        """Return the name of the device."""
        return f"{super().name} target level"

    @property
    def native_value(self):
        """Return the current target humidity level."""
        return self.device.config["auto_target_humidity"]

    @property
    def native_unit_of_measurement(self):
        """Return the native unit of measurement for the target humidity level."""
        return PERCENTAGE

    @property
    def device_class(self):
        """
        Return the device class of the target humidity level.

        Eventually this should become NumberDeviceClass but that was introduced in 2022.12.
        For maximum compatibility, using SensorDeviceClass as recommended by deprecation notice.
        Or hard code this to "humidity"
        """

        return SensorDeviceClass.HUMIDITY

    def set_native_value(self, value):
        """Set the target humidity level."""
        self.device.set_humidity(int(value))
