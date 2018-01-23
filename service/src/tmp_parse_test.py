from node import parse_process_graph

uc1_graph = {
    "process_graph": {
        "process_id": "filter_daterange",
        "args": {
            "collections": [{
                "process_id": "filter_bbox",
                "args": {
                    "collections": [{
                        "product_id": "Sentinel-2A"
                    }],
                    "left" : "0 48",
                    "right" :"12 48",
                    "top" : "9 47",
                    "bottom" : "14 46",
                    "finish" : "0 48",
                    "srs" : "EPSG:32632"
                }
            }],
            "from": "2017-01-01T00:00:00",
            "to": "2017-01-05T23:59:59"
        }
    }
}

end_node = parse_process_graph(uc1_graph["process_graph"])
