from nameko.testing.services import worker_factory

from capabilities.service import CapabilitiesService

MOCKED_API_SPEC = {
    "openapi": "3.0.1",
    "servers":
        {
            "url": 'https://openeo.eodc.eu/',
            "description": 'The URL to the EODC API',
            "versions": {
                "v1.0": {
                    "url": "https://openeo.eodc.eu/v1.0",
                    "api_version": "1.0.0-rc.2"
                },
                "v0.4": {
                    "url": "https://openeo.eodc.eu/v0.4",
                    "api_version": "0.4.2"
                }
            }
        },
    "info": {
        "title": "EODC API",
        "version": "1.0.0-rc.2",
        "description": 'The EODC API provides access to the EODC services and data, as well as access to the openEO'
                       ' endpoints.',
        "contact": {
            "name": "FirstName SecondName",
            "url": "https://openeo.eodc.eu",
            "email": "firstname.secondname@eodc.eu",
        },
        "license": {
            "name": "Apache 2.0",
            "url": "http://www.apache.org/licenses/LICENSE-2.0.html",
        },
        "backend_version": "1.0.0",
        "stac_version": "0.6.2",
        "id": "eodc-openeo-backend",
        "production": True,
        "file_formats": {
            "input": [
                {
                    "name": "GTiff",
                    "title": "GeoTiff",
                    "gis_data_types": {
                        "raster"
                    },
                }
            ],
            "output": [
                {
                    "name": "GTiff",
                    "title": "GeoTiff",
                    "gis_data_types": [
                        "raster"
                    ]
                }, {
                    "name": "png",
                    "title": "PNG",
                    "gis_data_types": [
                        "raster"
                    ],
                }, {
                    "name": "jpeg",
                    "title": "JPEG",
                    "gis_data_types": [
                        "raster"
                    ]
                }
            ]
        },
        "udf": [
            {
                "name": "Python",
                "default": "3.6",
                "versions": {
                    "3.6": {
                        "libraries": {
                            "numpy": {
                                "version": "1.18.1",
                                "links": {
                                    "href": "https://docs.scipy.org/doc/",
                                    "rel": "about",

                                }
                            }
                        }
                    }
                }
            }
        ]},
    'paths': {
        '/': {
            'get': {
                'summary': 'Information about the back-end',
                'operationId': 'capabilities',
                'description': 'Returns general information about the back-end, including which version and endpoints'
                               ' of the openEO API are supported. May also include billing information.',
                'tags': ['Capabilities'],
                'security': [{}],
                'responses': {
                    '200': {
                        'description': 'Information about the API version and supported endpoints / features.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'title': 'Capabilities Response',
                                    'type': 'object',
                                    'required': ['id', 'title', 'description', 'api_version', 'backend_version',
                                                 'stac_version', 'endpoints', 'links'],
                                    'properties': {
                                        'api_version': {
                                            'type': 'string',
                                            'description': 'Version number of the openEO specification this back-end'
                                                           ' implements.',
                                            'example': '1.0.1'
                                        },
                                        'backend_version': {
                                            'type': 'string',
                                            'description': 'Version number of the back-end implementation.\nEvery'
                                                           ' change on back-end side MUST cause a change of the version'
                                                           ' number.',
                                            'example': '1.1.2'
                                        },
                                        'stac_version': {
                                            'type': 'string',
                                            'description': 'The STAC version implemented.',
                                            'enum': ['0.9.0']
                                        },
                                    }}}}}}}}}}


def test_get_index():
    service = worker_factory(CapabilitiesService)
    result = service.send_index(MOCKED_API_SPEC)
    assert result == {
        'status': 'success',
        'code': 200,
        'data': {
            'api_version': '1.0.0-rc.2',
            'backend_version': '1.0.0',
            'title': 'EODC API',
            'description': 'The EODC API provides access to the EODC services and data, as well as access to the openEO'
                           ' endpoints.',
            'endpoints': [{
                'path': '/',
                'methods': ['GET']
            }],
            'stac_version': '0.6.2',
            'id': 'eodc-openeo-backend',
            'production': True,
            'links': []
        }}


def test_get_versions():
    service = worker_factory(CapabilitiesService)
    result = service.get_versions(MOCKED_API_SPEC)
    assert result == {'status': 'success',
                      'code': 200,
                      'data': {
                          'versions': [
                              {
                                  'api_version': '1.0.0-rc.2',
                                  'production': True,
                                  'url': 'https://openeo.eodc.eu/v1.0'
                              }, {
                                  'api_version': '0.4.2',
                                  'production': True,
                                  'url': 'https://openeo.eodc.eu/v0.4'
                              }]}}


def test_get_file_formats():
    service = worker_factory(CapabilitiesService)
    result = service.get_file_formats(MOCKED_API_SPEC)
    assert result == {
        'status': 'success',
        'code': 200,
        'data': {
            'output': {
                'GTiff': {
                    'title': 'GeoTiff',
                    'gis_data_types': ['raster'],
                    'parameters': {}
                },
                'png': {
                    'title': 'PNG',
                    'gis_data_types': ['raster'],
                    'parameters': {}
                },
                'jpeg': {
                    'title': 'JPEG',
                    'gis_data_types': ['raster'],
                    'parameters': {}
                }
            },
            'input': {
                'GTiff': {
                    'title': 'GeoTiff',
                    'gis_data_types': {'raster'},
                    'parameters': {}}
            }}}


def test_get_udfs():
    service = worker_factory(CapabilitiesService)
    result = service.get_udfs(MOCKED_API_SPEC)
    assert result == {
        'status': 'success',
        'code': 200,
        'data': [{'default': '3.6',
                  'name': 'Python',
                  'versions': {
                      '3.6': {
                          'libraries': {
                              'numpy': {
                                  'links': {
                                      'href': 'https://docs.scipy.org/doc/',
                                      'rel': 'about'},
                                  'version': '1.18.1'}}}}}]}


def test_get_service_types():
    service = worker_factory(CapabilitiesService)
    result = service.get_service_types(MOCKED_API_SPEC)
    assert result == {
        "status": "success",
        "code": 200,
        "data": {'Secondary services': 'None implemented.'}
    }
