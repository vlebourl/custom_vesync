"""Support for VeSync fans."""
import math

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.percentage import (
    int_states_in_range,
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .common import VeSyncDevice, has_feature
from .const import (
    DOMAIN,
    VS_DISCOVERY,
    VS_FANS,
    VS_LEVELS,
    VS_MODE_AUTO,
    VS_MODE_MANUAL,
    VS_MODE_SLEEP,
    VS_MODES,
    VS_TO_HA_ATTRIBUTES,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the VeSync fan platform."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]

    @callback
    def discover(devices):
        """Add new devices to platform."""
        _setup_entities(devices, async_add_entities, coordinator)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, VS_DISCOVERY.format(VS_FANS), discover)
    )

    _setup_entities(
        hass.data[DOMAIN][config_entry.entry_id][VS_FANS],
        async_add_entities,
        coordinator,
    )


@callback
def _setup_entities(devices, async_add_entities, coordinator):
    """Check if device is online and add entity."""
    async_add_entities(
        [VeSyncFanHA(dev, coordinator) for dev in devices], update_before_add=True
    )


class VeSyncFanHA(VeSyncDevice, FanEntity):
    """Representation of a VeSync fan."""

    def __init__(self, fan, coordinator) -> None:
        """Initialize the VeSync fan device."""
        super().__init__(fan, coordinator)
        self.smartfan = fan
        self._speed_range = (1, 1)
        self._attr_preset_modes = [VS_MODE_MANUAL, VS_MODE_AUTO, VS_MODE_SLEEP]
        if has_feature(self.smartfan, "config_dict", VS_LEVELS):
            self._speed_range = (1, max(self.smartfan.config_dict[VS_LEVELS]))
        if has_feature(self.smartfan, "config_dict", VS_MODES):
            self._attr_preset_modes = [
                VS_MODE_MANUAL,
                *[
                    mode
                    for mode in [VS_MODE_AUTO, VS_MODE_SLEEP]
                    if mode in self.smartfan.config_dict[VS_MODES]
                ],
            ]
        if self.smartfan.device_type == "LV-PUR131S":
            self._speed_range = (1, 3)

    @property
    def supported_features(self):
        """Flag supported features."""
        return (
            FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
            if self.speed_count > 1
            else FanEntityFeature.SET_SPEED
        )

    @property
    def percentage(self):
        """Return the current speed."""
        if (
            self.smartfan.mode == VS_MODE_MANUAL
            and (current_level := self.smartfan.fan_level) is not None
        ):
            return ranged_value_to_percentage(self._speed_range, current_level)
        return None

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return int_states_in_range(self._speed_range)

    @property
    def preset_mode(self):
        """Get the current preset mode."""
        return self.smartfan.mode

    @property
    def unique_info(self):
        """Return the ID of this fan."""
        return self.smartfan.uuid

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the fan."""
        attr = {}
        for k, v in self.smartfan.details.items():
            if k in VS_TO_HA_ATTRIBUTES:
                attr[VS_TO_HA_ATTRIBUTES[k]] = v
            elif k in self.state_attributes:
                attr[f"vs_{k}"] = v
            else:
                attr[k] = v
        return attr

    def set_percentage(self, percentage):
        """Set the speed of the device."""
        if percentage == 0:
            self.smartfan.turn_off()
            return

        if not self.smartfan.is_on:
            self.smartfan.turn_on()

        self.smartfan.manual_mode()
        self.smartfan.change_fan_speed(
            math.ceil(percentage_to_ranged_value(self._speed_range, percentage))
        )
        self.schedule_update_ha_state()

    def set_preset_mode(self, preset_mode):
        """Set the preset mode of device."""
        if preset_mode not in self.preset_modes:
            raise ValueError(
                "{preset_mode} is not one of the valid preset modes: {self.preset_modes}"
            )

        if not self.smartfan.is_on:
            self.smartfan.turn_on()

        if preset_mode == VS_MODE_AUTO:
            self.smartfan.auto_mode()
        elif preset_mode == VS_MODE_SLEEP:
            self.smartfan.sleep_mode()
        elif preset_mode == VS_MODE_MANUAL:
            self.smartfan.manual_mode()

        self.schedule_update_ha_state()

    def turn_on(
        self,
        speed: str = None,
        percentage: int = None,
        preset_mode: str = None,
        **kwargs,
    ) -> None:
        """Turn the device on."""
        if preset_mode:
            self.set_preset_mode(preset_mode)
            return
        if percentage is None:
            percentage = 50
        self.set_percentage(percentage)
