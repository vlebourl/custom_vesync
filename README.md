[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/iMicknl/ha-tahoma.svg)](https://GitHub.com/vlebourl/vesync-bpo/releases/)
[![Discord](https://img.shields.io/discord/968515496217567293?label=Discord)](https://discord.gg/MbDM9WQf)

# VeSync custom component for Home Assistant

Custom component for Home Assistant to interact with smart devices via the VeSync platform.

## Installation

You can install this integration via [HACS](#hacs) or [manually](#manual).
This integration will override the core VeSync integration.

### HACS

This integration can be installed by adding this repository to HACS __AS A CUSTOM REPOSITORY__, then searching for `Custom VeSync`, and choosing install. Reboot Home Assistant and configure the 'VeSync' integration via the integrations page or press the blue button below.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=vesync)

### Manual

Copy the `custom_components/vesync` to your `custom_components` folder. Reboot Home Assistant and configure the 'VeSync' integration via the integrations page or press the blue button below.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=vesync)

### Enable debug logging

The [logger](https://www.home-assistant.io/integrations/logger/) integration lets you define the level of logging activities in Home Assistant. Turning on debug mode will show more information about unsupported devices in your logbook.

```yaml
logger:
  default: error
  logs:
    custom_components.vesync: debug
    pyvesync: debug
```

This integration is heavily based on [VeSync_bpo](https://github.com/borpin/vesync-bpo) and [pyvesync](https://github.com/webdjoe/pyvesync)
