"""Support for power & energy sensors for VeSync outlets."""
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .common import VeSyncBaseEntity, is_humidifier
from .const import DOMAIN, VS_BINARY_SENSORS, VS_DISCOVERY

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors."""

    @callback
    def discover(devices):
        """Add new devices to platform."""
        _setup_entities(devices, async_add_entities)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, VS_DISCOVERY.format(VS_BINARY_SENSORS), discover)
    )

    _setup_entities(
        hass.data[DOMAIN][config_entry.entry_id][VS_BINARY_SENSORS], async_add_entities
    )


@callback
def _setup_entities(devices, async_add_entities):
    """Check if device is online and add entity."""
    entities = []
    for dev in devices:
        if is_humidifier(dev.device_type):
            entities.extend(
                (VeSyncOutOfWaterSensor(dev), VeSyncWaterTankLiftedSensor(dev))
            )

        else:
            _LOGGER.warning(
                "%s - Unknown device type - %s", dev.device_name, dev.device_type
            )

    async_add_entities(entities, update_before_add=True)


class VeSyncHumidifierBinarySensorEntity(VeSyncBaseEntity, BinarySensorEntity):
    """Representation of a binary sensor describing diagnostics of a VeSync humidifier."""

    def __init__(self, humidifier):
        """Initialize the VeSync humidifier device."""
        super().__init__(humidifier)
        self.smarthumidifier = humidifier

    @property
    def entity_category(self):
        """Return the diagnostic entity category."""
        return EntityCategory.DIAGNOSTIC


class VeSyncOutOfWaterSensor(VeSyncHumidifierBinarySensorEntity):
    """Out of Water Sensor."""

    @property
    def unique_id(self):
        """Return unique ID for out of water sensor on device."""
        return f"{super().unique_id}-out_of_water"

    @property
    def name(self):
        """Return sensor name."""
        return f"{super().name} out of water"

    @property
    def is_on(self) -> bool:
        """Return a value indicating whether the Humidifier is out of water."""
        return self.smarthumidifier.details["water_lacks"]


class VeSyncWaterTankLiftedSensor(VeSyncHumidifierBinarySensorEntity):
    """Tank Lifted Sensor."""

    @property
    def unique_id(self):
        """Return unique ID for water tank lifted sensor on device."""
        return f"{super().unique_id}-water_tank_lifted"

    @property
    def name(self):
        """Return sensor name."""
        return f"{super().name} water tank lifted"

    @property
    def is_on(self) -> bool:
        """Return a value indicating whether the Humidifier's water tank is lifted."""
        return self.smarthumidifier.details["water_tank_lifted"]
