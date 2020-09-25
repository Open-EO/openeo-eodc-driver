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

filepaths_response = {
    "status": "success",
    "code": 200,
    "data": [
        '/s2a_prd_msil1c/2018/06/08/S2A_MSIL1C_20180608T101021_N0206_R022_T32TPS_20180608T135059.zip',
        '/s2a_prd_msil1c/2018/06/11/S2A_MSIL1C_20180611T102021_N0206_R065_T32TPS_20180611T123241.zip',
        '/s2a_prd_msil1c/2018/06/18/S2A_MSIL1C_20180618T101021_N0206_R022_T32TPS_20180618T135619.zip',
        '/s2a_prd_msil1c/2018/06/21/S2A_MSIL1C_20180621T102021_N0206_R065_T32TPS_20180621T140615.zip'
    ]
}

filepaths_response_dc = {
    "status": "success",
    "code": 200,
    "data": [
        '/sig0/SIG0-----_SGRTA01_S1A_IWGRDH1VHD_20170301_050935--_EU010M_E052N015T1.tif',
        '/sig0/SIG0-----_SGRTA01_S1A_IWGRDH1VHD_20170301_051000--_EU010M_E052N015T1.tif',
        '/sig0/SIG0-----_SGRTA01_S1A_IWGRDH1VVD_20170301_050935--_EU010M_E052N015T1.tif',
        '/sig0/SIG0-----_SGRTA01_S1A_IWGRDH1VVD_20170301_051000--_EU010M_E052N015T1.tif',
        '/sig0/SIG0-----_SGRTA01_S1B_IWGRDH1VHD_20170302_050053--_EU010M_E052N015T1.tif',
        '/sig0/SIG0-----_SGRTA01_S1B_IWGRDH1VHD_20170302_050118--_EU010M_E052N015T1.tif',
        '/sig0/SIG0-----_SGRTA01_S1B_IWGRDH1VVD_20170302_050053--_EU010M_E052N015T1.tif',
        '/sig0/SIG0-----_SGRTA01_S1B_IWGRDH1VVD_20170302_050118--_EU010M_E052N015T1.tif',
        '/sig0/SIG0-----_SGRTA01_S1A_IWGRDH1VHD_20170301_050935--_EU010M_E052N016T1.tif',
        '/sig0/SIG0-----_SGRTA01_S1A_IWGRDH1VHD_20170301_051000--_EU010M_E052N016T1.tif',
        '/sig0/SIG0-----_SGRTA01_S1A_IWGRDH1VVD_20170301_050935--_EU010M_E052N016T1.tif',
        '/sig0/SIG0-----_SGRTA01_S1A_IWGRDH1VVD_20170301_051000--_EU010M_E052N016T1.tif',
        '/sig0/SIG0-----_SGRTA01_S1B_IWGRDH1VHD_20170302_050028--_EU010M_E052N016T1.tif',
        '/sig0/SIG0-----_SGRTA01_S1B_IWGRDH1VHD_20170302_050053--_EU010M_E052N016T1.tif',
        '/sig0/SIG0-----_SGRTA01_S1B_IWGRDH1VVD_20170302_050028--_EU010M_E052N016T1.tif',
        '/sig0/SIG0-----_SGRTA01_S1B_IWGRDH1VVD_20170302_050053--_EU010M_E052N016T1.tif'
    ]
}

filepaths_response_wekeo = {
    "status": "success",
    "code": 200,
    "data": [
        'S5P_OFFL_L2__NO2____20200905T001020_20200905T015149_15005_01_010302_20200906T171544',
        'S5P_OFFL_L2__NO2____20200904T222850_20200905T001020_15004_01_010302_20200906T145821',
        'S5P_OFFL_L2__NO2____20200904T204721_20200904T222850_15003_01_010302_20200906T140158',
        'S5P_OFFL_L2__NO2____20200904T190551_20200904T204721_15002_01_010302_20200906T122151',
        'S5P_OFFL_L2__NO2____20200904T172422_20200904T190551_15001_01_010302_20200906T104527',
        'S5P_OFFL_L2__NO2____20200904T154252_20200904T172422_15000_01_010302_20200906T082746',
        'S5P_OFFL_L2__NO2____20200904T140123_20200904T154252_14999_01_010302_20200906T070134',
        'S5P_OFFL_L2__NO2____20200904T121954_20200904T140123_14998_01_010302_20200906T052750',
        'S5P_OFFL_L2__NO2____20200904T103824_20200904T121954_14997_01_010302_20200906T040557',
        'S5P_NRTI_L2__NO2____20200904T094909_20200904T095409_14996_01_010302_20200904T103052',
        'S5P_NRTI_L2__NO2____20200904T094409_20200904T094909_14996_01_010302_20200904T102622',
        'S5P_OFFL_L2__NO2____20200904T071525_20200904T085655_14995_01_010302_20200905T235746',
        'S5P_OFFL_L2__NO2____20200904T053356_20200904T071525_14994_01_010302_20200905T223932',
        'S5P_OFFL_L2__NO2____20200904T035226_20200904T053356_14993_01_010302_20200905T205023',
        'S5P_OFFL_L2__NO2____20200904T021057_20200904T035226_14992_01_010302_20200905T185314',
        'S5P_OFFL_L2__NO2____20200904T002927_20200904T021057_14991_01_010302_20200905T165828'
    ]
}


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


def test_get_filepaths() -> None:
    data_service = worker_factory(DataService)

    data_service.csw_session.get_filepaths.return_value = filepaths_response
    collection_id = "s2a_prd_msil1c"
    spatial_extent = [46.464349400461145, 11.279182434082033, 46.522729291844286, 11.406898498535158]
    temporal_extent = ["2018-06-04", "2018-06-23"]
    result = data_service.get_filepaths(collection_id, spatial_extent, temporal_extent)
    assert result == {
        "status": "success",
        "code": 200,
        "data": filepaths_response,
    }

    data_service.csw_session_dc.get_filepaths.return_value = filepaths_response_dc
    collection_id = "SIG0"
    spatial_extent = [48.06, 16.06, 48.35, 16.65]
    temporal_extent = ["2017-03-01", "2017-03-03"]
    result = data_service.get_filepaths(collection_id, spatial_extent, temporal_extent)
    assert result == {
        "status": "success",
        "code": 200,
        "data": filepaths_response_dc,
    }

    data_service.hda_session.get_filepaths.return_value = filepaths_response_wekeo
    collection_id = "EO:ESA:DAT:SENTINEL-5P:TROPOMI:L2__NO2___"
    spatial_extent = [43.96918075703031, 7.631289019431526, 46.001682783839534, 12.843490774792011]
    temporal_extent = ['2020-09-04T00:00:00.000Z', '2020-09-05T01:00:00.000Z']
    result = data_service.get_filepaths(collection_id, spatial_extent, temporal_extent)
    assert result == {
        "status": "success",
        "code": 200,
        "data": filepaths_response_wekeo,
    }
