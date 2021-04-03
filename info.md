{% if prerelease %}
### NB!: This is a Beta version!
{% endif %}

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacs-shield]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

[![Community Forum][forum-shield]][forum]

_Component to integrate with Gismeteo weather provider._

![Gismeteo Logo][exampleimg]

## Features:

- Weather provider with hourly forecast for up to 48 hours or daily forecast for 7 days;
- Sensors of current weather:
  - air temperature,
  - air relative humidity,
  - air pressure,
  - wind bearing and speed,
  - cloud coverage,
  - rain and snow volume,
  - storm prediction,
  - geomagnetic field value,
  - water temperature;
- Weather forecast sensor for 3 hours;

{% if not installed %}
## Installation

1. Click install.
1. _If you want to configure component via Home Assistant UI..._\
    in the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Gismeteo".
1. _If you want to configure component via `configuration.yaml`..._\
    follow instructions in [Documentation][component], then restart Home Assistant.

{% endif %}
## Breaking Changes

- Since version 2.2.0 forecast sensor has the name `... 3h Forecast` instead of `... Forecast`.

## Useful Links

- [Documentation][component]
- [Report a Bug][report_bug]
- [Suggest an idea][suggest_idea]

<p align="center">* * *</p>
I put a lot of work into making this repo and component available and updated to inspire and help others! I will be glad to receive thanks from you — it will give me new strength and add enthusiasm:
<p align="center"><br>
<a href="https://www.patreon.com/join/limych?" target="_blank"><img src="http://khrolenok.ru/support_patreon.png" alt="Patreon" width="250" height="48"></a>
<br>or&nbsp;support via Bitcoin or Etherium:<br>
<a href="https://sochain.com/a/mjz640g" target="_blank"><img src="http://khrolenok.ru/support_bitcoin.png" alt="Bitcoin" width="150"><br>
16yfCfz9dZ8y8yuSwBFVfiAa3CNYdMh7Ts</a>
</p>

***

[component]: https://github.com/Limych/ha-gismeteo
[commits-shield]: https://img.shields.io/github/commit-activity/y/Limych/ha-gismeteo.svg?style=popout
[commits]: https://github.com/Limych/ha-gismeteo/commits/dev
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=popout
[hacs]: https://hacs.xyz
[exampleimg]: https://github.com/Limych/ha-gismeteo/raw/dev/gismeteo_logo.jpg
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
