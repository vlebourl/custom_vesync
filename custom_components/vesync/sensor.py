"""Support for power & energy sensors for VeSync outlets."""
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ENERGY_KILO_WATT_HOUR, PERCENTAGE, POWER_WATT
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .common import VeSyncBaseEntity, has_feature
from .const import DEV_TYPE_TO_HA, DOMAIN, VS_DISCOVERY, VS_SENSORS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switches."""

    @callback
    def discover(devices):
        """Add new devices to platform."""
        _setup_entities(devices, async_add_entities)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, VS_DISCOVERY.format(VS_SENSORS), discover)
    )

    _setup_entities(
        hass.data[DOMAIN][config_entry.entry_id][VS_SENSORS], async_add_entities
    )


@callback
def _setup_entities(devices, async_add_entities):
    """Check if device is online and add entity."""
    entities = []
    for dev in devices:
        if DEV_TYPE_TO_HA.get(dev.device_type) == "outlet":
            entities.extend((VeSyncPowerSensor(dev), VeSyncEnergySensor(dev)))
        if has_feature(dev, "details", "humidity"):
            entities.append(VeSyncHumiditySensor(dev))
        if has_feature(dev, "details", "air_quality"):
            entities.append(VeSyncAirQualitySensor(dev))
        if has_feature(dev, "details", "filter_life"):
            entities.append(VeSyncFilterLifeSensor(dev))

    async_add_entities(entities, update_before_add=True)


class VeSyncOutletSensorEntity(VeSyncBaseEntity, SensorEntity):
    """Representation of a sensor describing diagnostics of a VeSync outlet."""

    def __init__(self, plug):
        """Initialize the VeSync outlet device."""
        super().__init__(plug)
        self.smartplug = plug

    @property
    def entity_category(self):
        """Return the diagnostic entity category."""
        return EntityCategory.DIAGNOSTIC


class VeSyncPowerSensor(VeSyncOutletSensorEntity):
    """Representation of current power use for a VeSync outlet."""

    @property
    def unique_id(self):
        """Return unique ID for power sensor on device."""
        return f"{super().unique_id}-power"

    @property
    def name(self):
        """Return sensor name."""
        return f"{super().name} current power"

    @property
    def device_class(self):
        """Return the power device class."""
        return SensorDeviceClass.POWER

    @property
    def native_value(self):
        """Return the current power usage in W."""
        return self.smartplug.power

    @property
    def native_unit_of_measurement(self):
        """Return the Watt unit of measurement."""
        return POWER_WATT

    @property
    def state_class(self):
        """Return the measurement state class."""
        return SensorStateClass.MEASUREMENT

    def update(self):
        """Update outlet details and energy usage."""
        self.smartplug.update()
        self.smartplug.update_energy()


class VeSyncEnergySensor(VeSyncOutletSensorEntity):
    """Representation of current day's energy use for a VeSync outlet."""

    def __init__(self, plug):
        """Initialize the VeSync outlet device."""
        super().__init__(plug)
        self.smartplug = plug

    @property
    def unique_id(self):
        """Return unique ID for power sensor on device."""
        return f"{super().unique_id}-energy"

    @property
    def name(self):
        """Return sensor name."""
        return f"{super().name} energy use today"

    @property
    def device_class(self):
        """Return the energy device class."""
        return SensorDeviceClass.ENERGY

    @property
    def native_value(self):
        """Return the today total energy usage in kWh."""
        return self.smartplug.energy_today

    @property
    def native_unit_of_measurement(self):
        """Return the kWh unit of measurement."""
        return ENERGY_KILO_WATT_HOUR

    @property
    def state_class(self):
        """Return the total_increasing state class."""
        return SensorStateClass.TOTAL_INCREASING

    def update(self):
        """Update outlet details and energy usage."""
        self.smartplug.update()
        self.smartplug.update_energy()


class VeSyncHumidifierSensorEntity(VeSyncBaseEntity, SensorEntity):
    """Representation of a sensor describing diagnostics of a VeSync humidifier."""

    def __init__(self, humidifier):
        """Initialize the VeSync humidifier device."""
        super().__init__(humidifier)
        self.smarthumidifier = humidifier

    @property
    def entity_category(self):
        """Return the diagnostic entity category."""
        return EntityCategory.DIAGNOSTIC


class VeSyncAirQualitySensor(VeSyncHumidifierSensorEntity):
    """Representation of an air quality sensor."""

    @property
    def unique_id(self):
        """Return unique ID for air quality sensor on device."""
        return f"{super().unique_id}-air-quality"

    @property
    def name(self):
        """Return sensor name."""
        return f"{super().name} air quality"

    @property
    def device_class(self):
        """Return the air quality device class."""
        return SensorDeviceClass.AQI

    @property
    def native_value(self):
        """Return the air quality index."""
        return self.smarthumidifier.details["air_quality_value"]

    @property
    def native_unit_of_measurement(self):
        """Return the % unit of measurement."""
        return " "

    @property
    def state_class(self):
        """Return the measurement state class."""
        return SensorStateClass.MEASUREMENT


class VeSyncFilterLifeSensor(VeSyncHumidifierSensorEntity):
    """Representation of a filter life sensor."""

    @property
    def unique_id(self):
        """Return unique ID for filter life sensor on device."""
        return f"{super().unique_id}-filter-life"

    @property
    def name(self):
        """Return sensor name."""
        return f"{super().name} filter life"

    @property
    def device_class(self):
        """Return the filter life device class."""
        return None

    @property
    def native_value(self):
        """Return the filter life index."""
        return self.smarthumidifier.details["filter_life"]

    @property
    def native_unit_of_measurement(self):
        """Return the % unit of measurement."""
        return PERCENTAGE

    @property
    def state_class(self):
        """Return the measurement state class."""
        return SensorStateClass.MEASUREMENT


class VeSyncHumiditySensor(VeSyncHumidifierSensorEntity):
    """Representation of current humidity for a VeSync humidifier."""

    @property
    def unique_id(self):
        """Return unique ID for humidity sensor on device."""
        return f"{super().unique_id}-humidity"

    @property
    def name(self):
        """Return sensor name."""
        return f"{super().name} current humidity"

    @property
    def device_class(self):
        """Return the humidity device class."""
        return SensorDeviceClass.HUMIDITY

    @property
    def native_value(self):
        """Return the current humidity in percent."""
        return self.smarthumidifier.details["humidity"]

    @property
    def native_unit_of_measurement(self):
        """Return the % unit of measurement."""
        return PERCENTAGE

    @property
    def state_class(self):
        """Return the measurement state class."""
        return SensorStateClass.MEASUREMENT
