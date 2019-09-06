#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)

import json
import logging
import os
import re

# http://docs.python.org/2/howto/logging.html#library-config
# Avoids spurious error messages if no logger is configured by the user
logging.getLogger(__name__).addHandler(logging.NullHandler())

# logging.basicConfig(level=logging.DEBUG)

_LOGGER = logging.getLogger(__name__)


def fallback_version(localpath):
    """Return version from regex match."""
    return_value = ''
    if os.path.isfile(localpath):
        with open(localpath, 'r') as local:
            ret = re.compile(
                r"^\b(VERSION|__version__)\s*=\s*['\"](.*)['\"]")
            for line in local.readlines():
                matcher = ret.match(line)
                if matcher:
                    return_value = str(matcher.group(2))
    return return_value


def get_component_version(localpath, name):
    """Return the local version if any."""
    _LOGGER.debug('Started for ' + localpath)
    if '.' in name:
        name = "{}.{}".format(name.split('.')[1], name.split('.')[0])
    return_value = ''
    if os.path.isfile(localpath):
        package = "custom_components.{}".format(name)
        try:
            name = "__version__"
            return_value = getattr(
                __import__(package, fromlist=[name]), name)
        except Exception as err:  # pylint: disable=W0703
            _LOGGER.debug(str(err))
        if return_value == '':
            try:
                name = "VERSION"
                return_value = getattr(
                    __import__(package, fromlist=[name]), name)
            except Exception as err:  # pylint: disable=W0703
                _LOGGER.debug(str(err))
    if return_value == '':
        return_value = fallback_version(localpath)
    _LOGGER.debug(str(return_value))
    return return_value


with open('tracker.json', 'r') as tracker_file:
    tracker = json.load(tracker_file)
for package in tracker:
    _LOGGER.info('Updating version for %s', package)
    local_path = tracker[package]['local_location'].lstrip('/\\')
    tracker[package]['version'] = \
        get_component_version(local_path, package)
    base_path = os.path.split(local_path)[0]
    base_url = os.path.split(tracker[package]['remote_location'])[0]
    resources = []
    for current_path, dirs, files in os.walk(base_path):
        if current_path.find('__pycache__') != -1:
            continue
        for file in files:
            file = os.path.join(current_path, file).replace('\\', '/')
            if file != local_path:
                resources.append(base_url + file[len(base_path):])
    tracker[package]['resources'] = resources
with open('tracker.json', 'w') as tracker_file:
    json.dump(tracker, tracker_file, indent=4)
