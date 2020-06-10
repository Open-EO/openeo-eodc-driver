import json
import os

from nameko.testing.services import worker_factory

from data.models import Collection, Collections, Extent, Link
from data.service import DataService

collection_dict = {
    "stac_version": "0.9.0",
    "id": "s2a",
    "title": "Sentinet-2A",
    "description": "Sentinel-2A description",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "license": "Some license",
    # provider?
    "extent": {
        "spatial": [12.3, 34.5, 14.5, 36.7],
        "temporal": ["2015-06-23T00:00:00Z", "2019-01-01T00:00:00Z"],
    },
    "links": [{
        "rel": "alternate",
        "href": "https://openeo.org/csw",
        "title": "openEO catalog (OGC Catalogue Services 3.0)",
    }]
}


collection_model = Collection(
    stac_version="0.9.0",
    b_id="s2a",
    title="Sentinet-2A",
    description="Sentinel-2A description",
    keywords=["keyword1", "keyword2", "keyword3"],
    b_license="Some license",
    # provider?
    extent=Extent(
        spatial=[12.3, 34.5, 14.5, 36.7],
        temporal=["2015-06-23T00:00:00Z", "2019-01-01T00:00:00Z"],
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
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "dependencies", "jsons",
                             collection_id + ".json")
    with open(json_path) as f:
        json_data = json.load(f)
    json_data.update(collection_dict)

    data_service = worker_factory(DataService)
    data_service.arg_parser.parse_product.return_value = collection_id
    data_service.csw_session.get_product.return_value = collection_model
    result = data_service.get_product_detail()
    assert result == {
        "status": "success",
        "code": 200,
        "data": json_data,
    }
