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
VS_MODE_HUMIDITY = "humidity"
VS_MODE_MANUAL = "manual"
VS_MODE_SLEEP = "sleep"

VS_TO_HA_ATTRIBUTES = {"humidity": "current_humidity"}

VS_FAN_TYPES = ["VeSyncAirBypass", "VeSyncAir131", "VeSyncVital"]
VS_HUMIDIFIERS_TYPES = ["VeSyncHumid200300S", "VeSyncHumid200S", "VeSyncHumid1000S"]

DEV_TYPE_TO_HA = {
    "ESL100": "bulb-dimmable",
    "ESL100CW": "bulb-tunable-white",
    "ESO15-TB": "outlet",
    "ESW03-USA": "outlet",
    "ESW01-EU": "outlet",
    "ESW15-USA": "outlet",
    "wifi-switch-1.3": "outlet",
    "ESWL01": "switch",
    "ESWL03": "switch",
    "ESD16": "walldimmer",
    "ESWD16": "walldimmer",
}
