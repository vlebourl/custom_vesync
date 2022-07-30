"""Constants for VeSync Component."""

DOMAIN = "vesync"
VS_DISCOVERY = "vesync_discovery_{}"
SERVICE_UPDATE_DEVS = "update_devices"

VS_SWITCHES = "switches"
VS_FAN = "fan"
VS_FANS = "fans"
VS_LIGHTS = "lights"
VS_SENSORS = "sensors"
VS_HUMIDIFIERS = "humidifiers"
VS_NUMBERS = "numbers"
VS_BINARY_SENSORS = "binary_sensors"
VS_MANAGER = "manager"

VS_LEVELS = "levels"
VS_MODES = "modes"

VS_MODE_AUTO = "auto"
VS_MODE_MANUAL = "manual"
VS_MODE_SLEEP = "sleep"

VS_TO_HA_ATTRIBUTES = {"humidity": "current_humidity"}

DEV_TYPE_TO_HA = {
    "Core200S": "fan",
    "Core300S": "fan",
    "Core400S": "fan",
    "LAP-C201S-AUSR": "fan",
    "LAP-C202S-WUSR": "fan",
    "LAP-C401S-WUSR": "fan",
    "LAP-C601S-WUS": "fan",
    "LAP-C601S-WEU": "fan",
    "LV-PUR131S": "fan",
    "Classic300S": "humidifier",
    "ESD16": "walldimmer",
    "ESWD16": "walldimmer",
    "ESL100": "bulb-dimmable",
    "ESL100CW": "bulb-tunable-white",
    "wifi-switch-1.3": "outlet",
    "ESW03-USA": "outlet",
    "ESW01-EU": "outlet",
    "ESW15-USA": "outlet",
    "ESWL01": "switch",
    "ESWL03": "switch",
    "ESO15-TB": "outlet",
}
