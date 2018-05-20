# EODC Process: Extract-S2
Extracts, filters and stitches Sentinel-2 data from EODC storage.

Further description at: [openEO Process Documentation](https://open-eo.github.io/openeo-api/v0.0.2/processgraphs/index.html#core-processes)

- Description:
  ```json
    {
        "process_id": "filter-s2",
        "description": "Extracts and filters Sentinel-2 data from EODC storage to a mounted volume.",
        "git_uri": "git@git.eodc.eu:eodc-processes/filter-s2.git",
        "git_ref": "master",
        "type": "operation",
        "args": {
            "file_paths": {
                "description": "File-Paths per day (as array) to Sentinel-2 data on EODC storage",
                "type": "array",
                "required": true
            },
            "left":{
                "description":"left boundary (longitude / easting) in EPSG:32632",
                "type": "number",
                "required": true
            },
            "right":{
                "description":"right boundary (longitude / easting)",
                "type": "number",
                "required": true
            },
            "top":{
                "description":"top boundary (latitude / northing)",
                "type": "number",
                "required": true
            },
            "bottom":{
                "description":"bottom boundary (latitude / northing)",
                "type": "number",
                "required": true
            },
            "srs":{
                "description":"Spatial reference system of boundaries as proj4 or EPSG:12345 like string",
                "type": "string",
                "regex": "^EPSG:\\d+$",
                "required": true
            },
            "bands": {
                "description":"String or array of strings containing band ids.",
                "type": "number",
                "required": false
            }
        }
    }
```
