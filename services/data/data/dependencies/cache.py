"""Provides caching functions."""

import logging
from json import dumps, loads
from os import path
from typing import List

from dynaconf import settings

LOGGER = logging.getLogger("standardlog")


def cache_json(records: list, path_to_cache: str) -> None:
    """Store records to a json file for caching.

    Args:
        records: List of fetched records.
        path_to_cache: The path to the cached file. The filename must either be 'collection'/'collection_dc' or the
            identifier of the product.
    """
    if not records:
        return

    json_dump = dumps(records)
    with open(path_to_cache, "w") as f:
        f.write(json_dump)


def get_json_cache(path_to_cache: str) -> List[dict]:
    """Fetch the item(s) from the json cache.

    Args:
        path_to_cache: The path to the cached file.

    Returns:
        List of dictionaries containing cached data
    """
    try:
        LOGGER.debug("Getting json cache %s", path_to_cache)
        with open(path_to_cache, "r") as f:
            data = loads(f.read())
    except FileNotFoundError:
        data = []
    return data


def get_collection_cache_path(cache_path_dir: str, data_access: str = None) -> str:
    """Get the path to the cached collection summary depending on data_access.

    If data_access is empty of not equal to the required data_access of the second CSW the main collections.json file
    - describing the data available on the main CSW - is returned.
    """
    if data_access == settings.DATA_ACCESS_DC:
        return path.join(cache_path_dir, "collections_dc.json")
    else:
        return path.join(cache_path_dir, "collections.json")


def get_cache_path(
    cache_path_dir: str, product: str = None, series: bool = False, data_access: str = None
) -> str:
    """Get the path to a cached single product or to the summary collection.

    Args:
        cache_path_dir: Path to the cache directory.
        product: The identifier of a product.
        series: Boolean flag if the summary collection is request.
        data_access: The data access of the associated CSW server, defaults to the main one.

    Returns:
        The path to the cached file.

    Raises:
        OSError: Product and series flag or non of them is set. Only one of them can be provided.
    """
    if series and not product:
        return get_collection_cache_path(cache_path_dir, data_access)
    elif product:
        return path.join(cache_path_dir, product + ".json")
    else:
        raise OSError("Cache path can not be retrieved. Either a product name OR the series flag must be set.")
