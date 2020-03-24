from nameko.testing.services import worker_factory
from capabilities.service import CapabilitiesService, ServiceException

def test_get_versions():
    service = worker_factory(CapabilitiesService)
    result = service.get_versions()
    assert result == \
        {
            "status": "success",
            "code": 200,
            "data": {
                "versions": [
                    {
                        "url": "https://openeo.eodc.eu",
                        "api_version": "0.4.0",
                    }
                ]
            }
        }

def test_get_output_formats():
    service = worker_factory(CapabilitiesService)
    result = service.get_output_formats()
    assert result == \
        {
            "status": "success",
            "code": 200,
            "data": {
                "GTiff": {
                    "gis_data_types": [
                        "raster"
                    ],
                    "parameters": {}
                },
                "png": {
                    "gis_data_types": [
                        "raster"
                    ],
                    "parameters": {}
                },
                "jpeg": {
                    "gis_data_types": [
                        "raster"
                    ],
                    "parameters": {}
                }
            },
        }

def test_get_udfs():
    service = worker_factory(CapabilitiesService)
    result = service.get_udfs()
    assert result == \
        {
            "status": "success",
            "code": 200,
            "data": {}
        }

def test_get_service_types():
    service = worker_factory(CapabilitiesService)
    result = service.get_service_types()
    assert result == \
        {
            "status": "success",
            "code": 200,
            "data": {}
        }
