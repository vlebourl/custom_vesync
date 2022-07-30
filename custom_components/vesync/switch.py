"""Support for VeSync switches."""
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .common import VeSyncBaseEntity, VeSyncDevice
from .const import DEV_TYPE_TO_HA, DOMAIN, VS_DISCOVERY, VS_SWITCHES

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
        async_dispatcher_connect(hass, VS_DISCOVERY.format(VS_SWITCHES), discover)
    )

    _setup_entities(
        hass.data[DOMAIN][config_entry.entry_id][VS_SWITCHES], async_add_entities
    )


@callback
def _setup_entities(devices, async_add_entities):
    """Check if device is online and add entity."""
    entities = []
    for dev in devices:
        if DEV_TYPE_TO_HA.get(dev.device_type) == "outlet":
            entities.append(VeSyncSwitchHA(dev))
        if DEV_TYPE_TO_HA.get(dev.device_type) == "switch":
            entities.append(VeSyncLightSwitch(dev))
        if getattr(dev, "set_auto_mode", None):
            entities.append(VeSyncHumidifierAutoOnHA(dev))
        if getattr(dev, "automatic_stop_on", None):
            entities.append(VeSyncHumidifierAutomaticStopHA(dev))
        if getattr(dev, "turn_on_display", None):
            entities.append(VeSyncHumidifierDisplayHA(dev))
        if getattr(dev, "child_lock_on", None):
            entities.append(VeSyncFanChildLockHA(dev))

    async_add_entities(entities, update_before_add=True)


class VeSyncBaseSwitch(VeSyncDevice, SwitchEntity):
    """Base class for VeSync switch Device Representations."""

    def turn_on(self, **kwargs):
        """Turn the device on."""
        self.device.turn_on()


class VeSyncSwitchHA(VeSyncBaseSwitch, SwitchEntity):
    """Representation of a VeSync switch."""

    def __init__(self, plug):
        """Initialize the VeSync switch device."""
        super().__init__(plug)
        self.smartplug = plug

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the device."""
        return (
            {
                "voltage": self.smartplug.voltage,
                "weekly_energy_total": self.smartplug.weekly_energy_total,
                "monthly_energy_total": self.smartplug.monthly_energy_total,
                "yearly_energy_total": self.smartplug.yearly_energy_total,
            }
            if hasattr(self.smartplug, "weekly_energy_total")
            else {}
        )

    def update(self):
        """Update outlet details and energy usage."""
        self.smartplug.update()
        self.smartplug.update_energy()


class VeSyncLightSwitch(VeSyncBaseSwitch, SwitchEntity):
    """Handle representation of VeSync Light Switch."""

    def __init__(self, switch):
        """Initialize Light Switch device class."""
        super().__init__(switch)
        self.switch = switch


class VeSyncSwitchEntity(VeSyncBaseEntity, SwitchEntity):
    """Representation of a switch for configuring a VeSync humidifier."""

    def __init__(self, humidifier):
        """Initialize the VeSync humidifier device."""
        super().__init__(humidifier)
        self.smarthumidifier = humidifier

    @property
    def entity_category(self):
        """Return the configuration entity category."""
        return EntityCategory.CONFIG


class VeSyncFanChildLockHA(VeSyncSwitchEntity):
    """Representation of the child lock switch."""

    @property
    def unique_id(self):
        """Return the ID of this display."""
        return f"{super().unique_id}-child-lock"

    @property
    def name(self):
        """Return the name of the entity."""
        return f"{super().name} child lock"

    @property
    def is_on(self):
        """Return True if it is locked."""
        return self.device.details["child_lock"]

    def turn_on(self, **kwargs):
        """Turn the lock on."""
        self.device.child_lock_on()

    def turn_off(self, **kwargs):
        """Turn the lock off."""
        self.device.child_lock_off()


class VeSyncHumidifierDisplayHA(VeSyncSwitchEntity):
    """Representation of the child lock switch."""

    @property
    def unique_id(self):
        """Return the ID of this display."""
        return f"{super().unique_id}-display"

    @property
    def name(self):
        """Return the name of the entity."""
        return f"{super().name} display"

    @property
    def is_on(self):
        """Return True if it is locked."""
        return self.device.details["display"]

    def turn_on(self, **kwargs):
        """Turn the lock on."""
        self.device.turn_on_display()

    def turn_off(self, **kwargs):
        """Turn the lock off."""
        self.device.turn_off_display()


class VeSyncHumidifierAutomaticStopHA(VeSyncSwitchEntity):
    """Representation of the automatic stop toggle on a VeSync humidifier."""

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return f"{super().unique_id}-automatic-stop"

    @property
    def name(self):
        """Return the name of the device."""
        return f"{super().name} automatic stop"

    @property
    def is_on(self):
        """Return True if automatic stop is on."""
        return self.device.config["automatic_stop"]

    def turn_on(self, **kwargs):
        """Turn the automatic stop on."""
        self.device.automatic_stop_on()

    def turn_off(self, **kwargs):
        """Turn the automatic stop off."""
        self.device.automatic_stop_off()


class VeSyncHumidifierAutoOnHA(VeSyncSwitchEntity):
    """Provide switch to turn off auto mode and set manual mist level 1 on a VeSync humidifier."""

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return f"{super().unique_id}-auto-mode"

    @property
    def name(self):
        """Return the name of the device."""
        return f"{super().name} auto mode"

    @property
    def is_on(self):
        """Return True if in auto mode."""
        return self.device.details["mode"] == "auto"

    def turn_on(self, **kwargs):
        """Turn auto mode on."""
        self.device.set_auto_mode()

    def turn_off(self, **kwargs):
        """Turn auto off by setting manual and mist level 1."""
        self.device.set_manual_mode()
        self.device.set_mist_level(1)
