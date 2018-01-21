from node import parse_process_graph

uc1_graph = {
    "process_graph": 
    {
        "process_id": "min_time",
        "args": {
            "collections": [{
                "process_id": "NDVI",
                "args": {
                    "collections": [{
                        "process_id": "filter_daterange",
                        "args": {
                            "collections": [{
                                "process_id": "filter_bbox",
                                "args": {
                                    "collections": [{
                                        "product_id": "S2_L2A_T32TPS_20M"
                                    }],
                                    "left": 652000,
                                    "right":672000,
                                    "top": 5161000,
                                    "bottom": 5181000,
                                    "finish": 54654,
                                    "srs" : "EPSG:32632"
                                }
                            }],
                            "from": "2017-01-01",
                            "to": "2017-01-31"
                        }
                    }],
                    "red": "B04",
                    "nir": "B8A"
                }
            }]
        }
    }
}

if __name__ == "__main__":
    end_node = parse_process_graph(uc1_graph["process_graph"])
