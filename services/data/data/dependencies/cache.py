''' Module that contains caching functions '''

from datetime import datetime, timedelta
from json import dumps, loads
from os import path

def _cache_json(records: list, path_to_cache: str):
    """Stores the output to a json file with the id if single record or
    to a full collection json file

    Arguments:
        records {list} -- List of fetched records
        path_to_cache {str} -- The path to the cached file
    """

    if not records:
        return

    json_dump = dumps(records)
    with open(path_to_cache, 'w') as f:
        f.write(json_dump)

def _check_cache(path_to_cache: str) -> bool:
    """Checks whether the cache exists and if it is older than a day from
    running this function

    Arguments:
        path_to_cache {str} -- The path to the cached file

    Returns:
        bool -- False if cache doesn't exist or hasn't refreshed for
        longer than a day, True otherwise
    """

    if path.isfile(path_to_cache):
        now = datetime.now()
        file_time = datetime.utcfromtimestamp(int(path.getmtime(path_to_cache)))
        difference = now - file_time
        if difference < timedelta(1):
            return True

    return False

def _get_json_cache(path_to_cache: str) -> list:
    """Fetches the item(s) from the json cache

    Arguments:
        path_to_cache {str} -- The path to the cached file

    Returns:
        list -- List of dictionaries containing cached data
    """
    with open(path_to_cache, 'r') as f:
        data = loads(f.read())

    return data

def _get_cache_path(cache_path_dir: str, product: str, series: bool) -> str:
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
        path_to_cache = path.join(cache_path_dir, 'collections.json')
    else:
        path_to_cache = path.join(cache_path_dir, product + '.json')

    return path_to_cache
