from copy import deepcopy

from nameko.testing.services import worker_factory

from data.models import Collection, Collections, Extent, Link, SpatialExtent, TemporalExtent
from data.service import DataService

collection_dict = {
    "stac_version": "0.9.0",
    "id": "s2a_prd_msil1c",
    "title": "Sentinel-2A",
    "description": "Sentinel-2A description",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "license": "Some license",
    # provider?
    "extent": {
        "spatial": {
            "bbox": [[12.3, 34.5, 14.5, 36.7]]
        },
        "temporal": {
            "interval": [["2015-06-23T00:00:00Z", "2019-01-01T00:00:00Z"]],
        },
    },
    "cube:dimensions": {
        "bands": {
            "type": "bands",
            "values": [
                "B01",
                "B02",
            ]
        },
        "t": {
            "extent": [
                "2015-06-27T00:00:00Z",
                None,
            ],
            "type": "temporal"
        },
        "x": {
            "axis": "x",
            "extent": [
                -180,
                180
            ],
            "type": "spatial"
        },
        "y": {
            "axis": "y",
            "extent": [
                -90,
                90
            ],
            "type": "spatial"
        }
    },
    "summaries": {
        "eo:bands": [
            {
                "center_wavelength": 0.4427,
                "common_name": "coastal",
                "full_width_half_max": 0.021,
                "name": "B01"
            },
            {
                "center_wavelength": 0.4924,
                "common_name": "blue",
                "full_width_half_max": 0.066,
                "name": "B02"
            },
        ]
    },
    "deprecated": False,
    "links": [{
        "rel": "alternate",
        "href": "https://openeo.org/csw",
        "title": "openEO catalog (OGC Catalogue Services 3.0)",
    }]
}


collection_model = Collection(
    stac_version="0.9.0",
    id="s2a_prd_msil1c",
    title="Sentinel-2A",
    description="Sentinel-2A description",
    keywords=["keyword1", "keyword2", "keyword3"],
    license="Some license",
    # provider?
    cube_dimensions={
        "bands": {
            "type": "bands",
            "values": [
                "B01",
                "B02",
            ]
        },
        "t": {
            "extent": [
                "2015-06-27T00:00:00Z",
                None,
            ],
            "type": "temporal"
        },
        "x": {
            "axis": "x",
            "extent": [
                -180,
                180
            ],
            "type": "spatial"
        },
        "y": {
            "axis": "y",
            "extent": [
                -90,
                90
            ],
            "type": "spatial"
        }},
    summaries={
        "eo:bands": [
            {
                "center_wavelength": 0.4427,
                "common_name": "coastal",
                "full_width_half_max": 0.021,
                "name": "B01"
            },
            {
                "center_wavelength": 0.4924,
                "common_name": "blue",
                "full_width_half_max": 0.066,
                "name": "B02"
            },
        ]
    },
    extent=Extent(
        spatial=SpatialExtent(bbox=[[12.3, 34.5, 14.5, 36.7]]),
        temporal=TemporalExtent(interval=[["2015-06-23T00:00:00Z", "2019-01-01T00:00:00Z"]])
    ),
    links=[Link(
        rel="alternate",
        href="https://openeo.org/csw",
        title="openEO catalog (OGC Catalogue Services 3.0)",
    )],
)


def test_get_all_products() -> None:
    data_service = worker_factory(DataService)
    data_service.csw_session.get_all_products.return_value = Collections([collection_model], [])
    result = data_service.get_all_products()
    assert result == {
        "status": "success",
        "code": 200,
        "data": {
            "collections": [collection_dict],
            "links": [],
        }
    }


def test_get_product_detail() -> None:
    collection_id = "s2a_prd_msil1c"
    data_service = worker_factory(DataService)
    collect_ret = deepcopy(collection_dict)
    collect_ret["cube_dimensions"] = collect_ret["cube:dimensions"]
    data_service.csw_session.get_product.return_value = collect_ret
    result = data_service.get_product_detail(collection_id=collection_id)
    assert result == {
        "status": "success",
        "code": 200,
        "data": collection_dict,
    }
