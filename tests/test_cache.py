#  Copyright (c) 2019-2022, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>

# pylint: disable=redefined-outer-name,protected-access
"""Tests for Cache controller."""
import os
import random
from time import time

import pytest

from custom_components.gismeteo.cache import Cache


@pytest.fixture()
def config(tmpdir):
    """Cache controller tests."""
    return {
        "cache_dir": str(tmpdir),
        "cache_time": 60,
    }


@pytest.fixture()
def cache_dir(config):
    """Fill in temp dir with test files."""
    now = time()
    old = random.randint(1, 7)
    res = {"old": {}, "new": {}}

    for _ in range(old):
        file_name = os.urandom(4).hex()
        content = os.urandom(7).hex()
        file_path = os.path.join(config["cache_dir"], file_name)
        with open(file_path, "w", encoding="utf8") as fp:
            fp.write(content)

        mtime = now - 60 - random.randint(0, 180)
        os.utime(file_path, (mtime, mtime))
        res["old"][file_name] = content

    for _ in range(8 - old):
        file_name = os.urandom(4).hex()
        content = os.urandom(7).hex()
        file_path = os.path.join(config["cache_dir"], file_name)
        with open(file_path, "w", encoding="utf8") as fp:
            fp.write(content)

        mtime = now - random.randint(0, 59)
        os.utime(file_path, (mtime, mtime))
        res["new"][file_name] = content

    return res


def test__clean_dir(config, cache_dir):
    """Cache controller tests."""
    assert len(os.listdir(config["cache_dir"])) == len(cache_dir["old"]) + len(
        cache_dir["new"]
    )

    config["clean_dir"] = True
    Cache(config)

    assert len(os.listdir(config["cache_dir"])) == len(cache_dir["new"])


def test__get_file_path():
    """Cache controller tests."""
    cache = Cache(
        {
            "cache_dir": "/some/dir",
        }
    )

    assert cache._get_file_path("file_name.ext") == "/some/dir/file_name.ext"

    cache = Cache(
        {
            "cache_dir": "/some/strange/../dir",
        }
    )

    assert cache._get_file_path("file_name.ext") == "/some/dir/file_name.ext"

    cache = Cache(
        {
            "cache_dir": "/some/dir",
            "domain": "dmn",
        }
    )

    assert cache._get_file_path("file_name.ext") == "/some/dir/dmn.file_name.ext"

    cache = Cache(
        {
            "cache_dir": "/some/strange/../dir",
            "domain": "dmn",
        }
    )

    assert cache._get_file_path("file_name.ext") == "/some/dir/dmn.file_name.ext"


def test_is_cached(config, cache_dir):
    """Cache controller tests."""
    config["clean_dir"] = False
    cache = Cache(config)

    for i in cache_dir["old"].keys():
        assert cache.is_cached(i) is False

    for i in cache_dir["new"].keys():
        assert cache.is_cached(i) is True

    for _ in range(8):
        file_name = os.urandom(3).hex()
        assert cache.is_cached(file_name) is False


def test_read_cache(config, cache_dir):
    """Cache controller tests."""
    cache = Cache(config)

    for i in cache_dir["old"].keys():
        assert cache.read_cache(i) is None

    for i, con in cache_dir["new"].items():
        assert cache.read_cache(i) == con


def test_save_cache(config):
    """Cache controller tests."""
    config["cache_dir"] = os.path.join(config["cache_dir"], os.urandom(3).hex())
    cache = Cache(config)

    for _ in range(8):
        file_name = os.urandom(5).hex()
        content = os.urandom(7).hex()
        cache.save_cache(file_name, content)

        assert cache.read_cache(file_name) == content
