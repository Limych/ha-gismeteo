*Please :star: this repo if you find it useful*

# Gismeteo Weather Provider for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacs-shield]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

[![Community Forum][forum-shield]][forum]

_Component to integrate with Gismeteo weather provider._

This component can be used in two different ways: as a weather provider for any given coordinates and as a set of sensors for current coordinates of a house.

![Gismeteo Logo][exampleimg]

*NB. You can find a real example of using this component in [my Home Assistant configuration](https://github.com/Limych/HomeAssistantConfiguration).*

I also suggest you [visit the support topic][forum] on the community forum.

## Installation

**Note:** If you configure the integration through the Home Assistant GUI, the weather provider and sensors will be created at the same time. But you're limited to only one set of settings. When configuring via `configuration.yaml` file, you can create multiple weather providers.

### Install from HACS (recommended)

1. Have [HACS][hacs] installed, this will allow you to easily manage and track updates.
1. Search for "Gismeteo Weather Provider".
1. Click Install below the found integration.
1. _If you want to configure component via Home Assistant UI..._\
    in the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Gismeteo".
1. _If you want to configure component via `configuration.yaml`..._\
    follow instructions below, then restart Home Assistant.

### Manual installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `gismeteo`.
1. Download file `gismeteo.zip` from the [latest release section][latest-release] in this repository.
1. Extract _all_ files from this archive you downloaded in the directory (folder) `gismeteo` you created.
1. Restart Home Assistant
1. _If you want to configure component via Home Assistant UI..._\
    in the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Gismeteo".
1. _If you want to configure component via `configuration.yaml`..._\
    follow instructions below, then restart Home Assistant.

## Breaking Changes

- Since version 2.2.0 forecast sensor has the name `... 3h Forecast` instead of `... Forecast`.

## Configuration variables

### Weather Provider Configuration

The `gismeteo` weather platform uses [Gismeteo](https://www.gismeteo.ru/) as a source for current meteorological data for a specified location.

![Example](gismeteo_weather.jpg)

To add Gismeteo weather provider to your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
weather:
  - platform: gismeteo
```

You can add as many providers with different configurations as you wish.

<p align="center">* * *</p>
I put a lot of work into making this repo and component available and updated to inspire and help others! I will be glad to receive thanks from you — it will give me new strength and add enthusiasm:
<p align="center"><br>
<a href="https://www.patreon.com/join/limych?" target="_blank"><img src="http://khrolenok.ru/support_patreon.png" alt="Patreon" width="250" height="48"></a>
<br>or&nbsp;support via Bitcoin or Etherium:<br>
<a href="https://sochain.com/a/mjz640g" target="_blank"><img src="http://khrolenok.ru/support_bitcoin.png" alt="Bitcoin" width="150"><br>
16yfCfz9dZ8y8yuSwBFVfiAa3CNYdMh7Ts</a>
</p>

#### Configuration Variables

**name:**\
  _(string) (Optional)_\
  Name to use in the frontend.\
  _Default value: Gismeteo_

**mode:**\
  _(string) (Optional)_\
  Can specify `hourly` or `daily`. Select `hourly` for a three-hour forecast for 24h, `daily` for daily forecast for a week.\
  _Default value: `hourly`_

**latitude:**\
  _(float) (Optional)_\
  Latitude of the location to display the weather.\
  _Default value: The latitude in your `configuration.yaml` file._

**longitude:**\
  _(float) (Optional)_\
  Longitude of the location to display the weather.\
  _Default value: The longitude in your `configuration.yaml` file._

### Weather Sensors Configuration

The `gismeteo` sensors uses [Gismeteo](https://www.gismeteo.ru/) as a source for current meteorological data for your home location. The forecast will show you the condition in 3 h.

![Example](gismeteo_sensor.jpg)

To add Gismeteo sensors to your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
sensor:
  - platform: gismeteo
    monitored_conditions:
      - weather
```

You can add only one group of sensors.

<p align="center">* * *</p>
I put a lot of work into making this repo and component available and updated to inspire and help others! I will be glad to receive thanks from you — it will give me new strength and add enthusiasm:
<p align="center"><br>
<a href="https://www.patreon.com/join/limych?" target="_blank"><img src="http://khrolenok.ru/support_patreon.png" alt="Patreon" width="250" height="48"></a>
<br>or&nbsp;support via Bitcoin or Etherium:<br>
<a href="https://sochain.com/a/mjz640g" target="_blank"><img src="http://khrolenok.ru/support_bitcoin.png" alt="Bitcoin" width="150"><br>
16yfCfz9dZ8y8yuSwBFVfiAa3CNYdMh7Ts</a>
</p>

#### Configuration Variables

**name:**\
  _(string) (Optional)_\
  Additional name for the sensors. Default to platform name.\
  _Default value: Gismeteo_

**forecast:**\
  _(boolean) (Optional)_\
  Enables the forecast for 3h. The default is to display only the current conditions.\
  _Default value: false_

**monitored_conditions:**\
  _(list) (Required)_\
  Conditions to display in the frontend.

> **condition**\
>   A human-readable text summary.
>
> **temperature**\
>   The current temperature of air.
>
> **humidity**\
>   The relative humidity of air.
>
> **pressure**\
>   The sea-level air pressure in millibars.
>
> **wind_speed**\
>   The wind speed.
>
> **wind_bearing**\
>   The wind bearing.
>
> **clouds**\
>   Description about cloud coverage.
>
> **rain**\
>   The rain volume.
>
> **snow**\
>   The snow volume.
>
> **storm**\
>   The storm prediction.
>
> **geomagnetic**\
>   The geomagnetic field value:\
>   1 = No noticeable geomagnetic disturbance\
>   2 = Small geomagnetic disturbances\
>   3 = Weak geomagnetic storm\
>   4 = Small geomagnetic storm\
>   5 = Moderate geomagnetic storm\
>   6 = Severe geomagnetic storm\
>   7 = Hard geomagnetic storm\
>   8 = Extreme geomagnetic storm
>
> **water_temperature**\
>   The current temperature of water.

## Track updates

You can automatically track new versions of this component and update it by [HACS][hacs].

## Troubleshooting

To enable debug logs use this configuration:
```yaml
# Example configuration.yaml entry
logger:
  default: info
  logs:
    custom_components.gismeteo: debug
```
... then restart HA.

## Contributions are welcome!

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We have set up a separate document containing our [contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Authors & contributors

The original setup of this component is by [Andrey "Limych" Khrolenok](https://github.com/Limych).

For a full list of all authors and contributors, check [the contributor's page][contributors].

## License

creative commons Attribution-NonCommercial-ShareAlike 4.0 International License

See separate [license file](LICENSE.md) for full text.

***

[component]: https://github.com/Limych/ha-gismeteo
[commits-shield]: https://img.shields.io/github/commit-activity/y/Limych/ha-gismeteo.svg?style=popout
[commits]: https://github.com/Limych/ha-gismeteo/commits/master
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=popout
[hacs]: https://hacs.xyz
[exampleimg]: https://github.com/Limych/ha-gismeteo/raw/master/gismeteo_logo.jpg
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=popout
[forum]: https://community.home-assistant.io/t/gismeteo-weather-provider/109668
[license]: https://github.com/Limych/ha-gismeteo/blob/main/LICENSE.md
[license-shield]: https://img.shields.io/badge/license-Creative_Commons_BY--NC--SA_License-lightgray.svg?style=popout
[maintenance-shield]: https://img.shields.io/badge/maintainer-Andrey%20Khrolenok%20%40Limych-blue.svg?style=popout
[releases-shield]: https://img.shields.io/github/release/Limych/ha-gismeteo.svg?style=popout
[releases]: https://github.com/Limych/ha-gismeteo/releases
[releases-latest]: https://github.com/Limych/ha-gismeteo/releases/latest
[user_profile]: https://github.com/Limych
[report_bug]: https://github.com/Limych/ha-gismeteo/issues/new?template=bug_report.md
[suggest_idea]: https://github.com/Limych/ha-gismeteo/issues/new?template=feature_request.md
[contributors]: https://github.com/Limych/ha-gismeteo/graphs/contributors
