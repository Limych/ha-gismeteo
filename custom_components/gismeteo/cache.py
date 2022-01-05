#  Copyright (c) 2018, Vladimir Maksimenko <vl.maksime@gmail.com>
#  Copyright (c) 2019-2022, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#
# Version 3.1.0
"""Cache controller."""

import logging
import os
import time
from typing import Any, Dict, Optional

_LOGGER = logging.getLogger(__name__)


class Cache:
    """Data caching class."""

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        """Initialize cache."""
        _LOGGER.debug("Initializing cache")
        params = params or {}

        self._cache_dir = params.get("cache_dir", "")
        self._cache_time = params.get("cache_time", 0)
        self._domain = params.get("domain")

        if self._cache_dir:
            self._cache_dir = os.path.abspath(self._cache_dir)

        if params.get("clean_dir", False):
            self._clean_dir()

    def _clean_dir(self, cache_time: int = 0) -> None:
        """Clean cache."""
        now_time = time.time()
        cache_time = max(cache_time, self._cache_time)

        if self._cache_dir and os.path.exists(self._cache_dir):
            _LOGGER.debug("Cleaning cache directory %s", self._cache_dir)
            files = os.listdir(self._cache_dir)
            _LOGGER.debug(files)
            for file_name in files:
                file_path = os.path.join(self._cache_dir, file_name)
                try:
                    file_time = os.path.getmtime(file_path)
                    if (file_time + cache_time) <= now_time:
                        os.remove(file_path)
                except FileNotFoundError:  # pragma: no cover
                    pass

    def _get_file_path(self, file_name: str) -> str:
        """Get path of cache file."""
        if self._domain:
            file_name = ".".join((self._domain, file_name))
        return os.path.join(self._cache_dir, file_name)

    def cached_for(self, file_name: str) -> Optional[float]:
        """Return caching time of file if exists. Otherwise None."""
        file_path = self._get_file_path(file_name)
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return None

        file_time = os.path.getmtime(file_path)
        return time.time() - file_time

    def is_cached(self, file_name: str, cache_time: int = 0) -> bool:
        """Return True if cache file is exists."""
        file_path = self._get_file_path(file_name)
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return False

        file_time = os.path.getmtime(file_path)
        cache_time = max(cache_time, self._cache_time)
        return (file_time + cache_time) > time.time()

    def read_cache(self, file_name: str, cache_time: int = 0) -> Optional[Any]:
        """Read cached data."""
        file_path = self._get_file_path(file_name)
        _LOGGER.debug("Read cache file %s", file_path)
        if not self.is_cached(file_name, cache_time):
            return None

        with open(file_path, encoding="utf-8") as fp:
            return fp.read()

    def save_cache(self, file_name: str, content: Any) -> None:
        """Save data to cache."""
        if self._cache_dir:
            if not os.path.exists(self._cache_dir):
                os.makedirs(self._cache_dir)

            file_path = self._get_file_path(file_name)
            _LOGGER.debug("Store cache file %s", file_path)

            with open(file_path, "w", encoding="utf-8") as fp:
                fp.write(content)
