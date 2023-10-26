"""Support for VeSync button."""
import logging


from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .common import VeSyncBaseEntity
from .const import DOMAIN, VS_DISCOVERY, VS_BUTTON

_LOGGER = logging.getLogger(__name__)


SENSOR_TYPES_CS158 = {
    # unique_id,name # icon,
    "end": [
        "end",
        "End cooking or preheating ",
        "mdi:stop",
    ],
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switches."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]

    @callback
    def discover(devices):
        """Add new devices to platform."""
        _setup_entities(devices, async_add_entities, coordinator)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, VS_DISCOVERY.format(VS_BUTTON), discover)
    )

    _setup_entities(
        hass.data[DOMAIN][config_entry.entry_id][VS_BUTTON],
        async_add_entities,
        coordinator,
    )


@callback
def _setup_entities(devices, async_add_entities, coordinator):
    """Check if device is online and add entity."""
    entities = []
    for dev in devices:
        if hasattr(dev, "cook_set_temp"):
            for stype in SENSOR_TYPES_CS158.values():
                entities.append(
                    VeSyncairfryerButton(
                        dev,
                        coordinator,
                        stype,
                    )
                )

    async_add_entities(entities, update_before_add=True)


class VeSyncairfryerButton(VeSyncBaseEntity, ButtonEntity):
    """Base class for VeSync switch Device Representations."""

    def __init__(self, airfryer, coordinator, stype) -> None:
        """Initialize the VeSync humidifier device."""
        super().__init__(airfryer, coordinator)
        self.airfryer = airfryer
        self.stype = stype

    @property
    def unique_id(self):
        """Return unique ID for water tank lifted sensor on device."""
        return f"{super().unique_id}-" + self.stype[0]

    @property
    def name(self):
        """Return sensor name."""
        return self.stype[1]

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return self.stype[2]

    def press(self) -> None:
        """Return True if device is on."""
        self.airfryer.end()
