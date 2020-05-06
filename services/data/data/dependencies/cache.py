""" Module that contains caching functions """

from json import dumps, loads
from os import path
import logging

LOGGER = logging.getLogger("standardlog")


def cache_json(records: list, path_to_cache: str):
    """Stores the output to a json file with the id if single record or
    to a full collection json file

    Arguments:
        records {list} -- List of fetched records
        path_to_cache {str} -- The path to the cached file
    """

    if not records:
        return

    json_dump = dumps(records)
    with open(path_to_cache, "w") as f:
        f.write(json_dump)


def get_json_cache(path_to_cache: str) -> list:
    """Fetches the item(s) from the json cache

    Arguments:
        path_to_cache {str} -- The path to the cached file

    Returns:
        list -- List of dictionaries containing cached data
    """
    try:
        LOGGER.debug("Getting json cache %s", path_to_cache)
        with open(path_to_cache, "r") as f:
            data = loads(f.read())
    except FileNotFoundError:
        data = []
    return data


def get_cache_path(
    cache_path_dir: str, product: str = None, series: bool = False
) -> str:
    """Get the path of the cache depending on whether series or
    product were passed

    Arguments:
        cache_path_dir {str} -- Path to the cache dir
        product {str} -- The identifier of the product (default: {None})
        series {bool} -- Specifier if series (products) or records are queried (default: {False})


    Returns:
        str -- The path to the cached file
    """

    if series and not product:
        path_to_cache = path.join(cache_path_dir, "collections.json")
    else:
        path_to_cache = path.join(cache_path_dir, product + ".json")

    return path_to_cache
