"""

"""


import json
import os
from typing import Any, Dict, List


def add_non_csw_info(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for record in records:
        record.update(get_non_csw_info_single_record(record["id"]))
    return records


def get_non_csw_info_single_record(collection_id: str) -> Dict[str, Any]:
    # Add cube:dimensions and summaries
    json_file = os.path.join(
        os.path.dirname(__file__),
        "jsons",
        collection_id + ".json",
    )
    response = {}
    if os.path.isfile(json_file):
        with open(json_file) as file_json:
            json_data = json.load(file_json)
            for key in json_data.keys():
                response[key] = json_data[key]
    return response
