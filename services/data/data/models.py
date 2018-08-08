""" Models """


class SpatialExtent:
    """ Represents a spatial extent """

    def __init__(self, top: float, bottom: float, left: float, right: float, crs: str):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
        self.crs = crs


class TemporalExtent:
    """ Represents a temporal extent """

    def __init__(self, t_from: str, to: str):
        setattr(self, "from", t_from)   # Because 'from' is reserved in Python
        self.to = to


class Band:
    """ Represents a single band. """

    def __init__(self, band_id: str, wavelength_nm: float, res_m: int, scale: float,
                 offset: int, b_type: str, unit: str, name: str=""):
        self.band_id = band_id
        self.name = name
        self.wavelength_nm = wavelength_nm
        self.res_m = res_m
        self.scale = scale
        self.offset = offset
        setattr(self, "type", b_type)   # Because 'type' is reserved in Python
        self.unit = unit


class ProductRecord:
    """ Represents a single product record """

    def __init__(self, data_id: str, description: str, source: str,
                 spatial_extent: SpatialExtent=None, temporal_extent: TemporalExtent=None, bands: Band=None):
        self.data_id = data_id
        self.description = description
        self.source = source
        if spatial_extent: self.spatial_extent = spatial_extent
        if temporal_extent: self.temporal_extent = temporal_extent
        if bands: self.bands = bands


class Record:
    """ Represents a single record """

    def __init__(self, name: str, path: str,
                 spatial_extent: SpatialExtent=None, temporal_extent: TemporalExtent=None):
        self.name = name
        self.path = path
        if spatial_extent: self.spatial_extent = spatial_extent
        if temporal_extent: self.temporal_extent = temporal_extent


class FilePath:
    """ Schema for a file path """
    def __init__(self, date:str, name: str, path: str):
        self.date = date
        self.name = name
        self.path = path
