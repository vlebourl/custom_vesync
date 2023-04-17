"""Support for VeSync humidifiers."""

from homeassistant.components.humidifier import HumidifierEntity
from homeassistant.components.humidifier.const import (
    MODE_AUTO,
    MODE_NORMAL,
    MODE_SLEEP,
    SUPPORT_MODES,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback


from pyvesync.vesyncfan import VeSyncHumid200300S


from .common import VeSyncDevice
from .const import (
    DOMAIN,
    VS_DISCOVERY,
    VS_HUMIDIFIERS,
    VS_MODE_AUTO,
    VS_MODE_MANUAL,
    VS_MODE_SLEEP,
    VS_TO_HA_ATTRIBUTES,
)

MAX_HUMIDITY = 80
MIN_HUMIDITY = 30

MODES = [MODE_AUTO, MODE_NORMAL, MODE_SLEEP]


VS_TO_HA_MODE_MAP = {
    VS_MODE_MANUAL: MODE_NORMAL,
    VS_MODE_AUTO: MODE_AUTO,
    VS_MODE_SLEEP: MODE_SLEEP,
}

HA_TO_VS_MODE_MAP = {v: k for k, v in VS_TO_HA_MODE_MAP.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the VeSync humidifier platform."""

    @callback
    def discover(devices):
        """Add new devices to platform."""
        _setup_entities(devices, async_add_entities)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, VS_DISCOVERY.format(VS_HUMIDIFIERS), discover)
    )

    _setup_entities(
        hass.data[DOMAIN][config_entry.entry_id][VS_HUMIDIFIERS], async_add_entities
    )


@callback
def _setup_entities(devices, async_add_entities):
    """Check if device is online and add entity."""
    async_add_entities(
        [VeSyncHumidifierHA(dev) for dev in devices], update_before_add=True
    )


class VeSyncHumidifierHA(VeSyncDevice, HumidifierEntity):
    """Representation of a VeSync humidifier."""

    _attr_max_humidity = MAX_HUMIDITY
    _attr_min_humidity = MIN_HUMIDITY

    def __init__(self, humidifier: VeSyncHumid200300S):
        """Initialize the VeSync humidifier device."""
        super().__init__(humidifier)
        self.smarthumidifier = humidifier

    @property
    def available_modes(self):
        """Return the available mist modes."""
        return MODES

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_MODES

    @property
    def target_humidity(self):
        """Return the humidity we try to reach."""
        return self.smarthumidifier.config["auto_target_humidity"]

    @property
    def mode(self):
        """Get the current preset mode."""
        return VS_TO_HA_MODE_MAP[self.smarthumidifier.details["mode"]]

    @property
    def is_on(self):
        """Return True if humidifier is on."""
        return self.smarthumidifier.enabled  # device_status is always on

    @property
    def unique_info(self):
        """Return the ID of this humidifier."""
        return self.smarthumidifier.uuid

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the humidifier."""

        attr = {}
        for k, v in self.smarthumidifier.details.items():
            if k in VS_TO_HA_ATTRIBUTES:
                attr[VS_TO_HA_ATTRIBUTES[k]] = v
            elif k in self.state_attributes:
                attr[f"vs_{k}"] = v
            else:
                attr[k] = v
        return attr

    def set_humidity(self, humidity: int):
        """Set the target humidity of the device."""
        if humidity not in range(self.min_humidity, self.max_humidity + 1):
            raise ValueError(
                "{humidity} is not between {self.min_humidity} and {self.max_humidity} (inclusive)"
            )
        self.smarthumidifier.set_humidity(humidity)
        self.schedule_update_ha_state()

    def set_mode(self, mode: str):
        """Set the mode of the device."""
        if mode not in self.available_modes:
            raise ValueError(
                "{mode} is not one of the valid available modes: {self.available_modes}"
            )
        self.smarthumidifier.set_humidity_mode(HA_TO_VS_MODE_MAP[mode])
        self.schedule_update_ha_state()

    def turn_on(
        self,
        **kwargs,
    ) -> None:
        """Turn the device on."""
        self.smarthumidifier.turn_on()

    def turn_off(self, **kwargs):
        self.smarthumidifier.turn_off()
