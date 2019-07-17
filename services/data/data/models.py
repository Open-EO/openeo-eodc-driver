""" Models """


class Extent:
    """ Represents spatial and temporal extent """

    def __init__(self, spatial: list, temporal: list):
        self.spatial = spatial
        self.temporal = temporal

class Providers:
    """ Represents Providers """
    # Missing items in DB

class Properties:
    """ Represents Properties """
    # Missing items in DB, should somehow relate to BandSchema
    pass

class Link:
    """ Represents Links """
    def __init__(self, href: str, rel: str, b_type: str=None, title: str=None):
        self.href = href
        self.rel = rel
        if b_type: setattr(self, 'type', b_type) # Because 'type' is reserved in Python
        if title: self.title = title

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

    def __init__(self, stac_version: str, b_id: str, description: str, b_license: str,
                 extent: Extent, links: Link, title: str=None, keywords: list=None,
                 providers: Providers=None, version: str=None, properties: Properties=None):
        self.stac_version = stac_version
        setattr(self, "id", b_id) # Because 'id' is reserved in Python
        self.description = description
        setattr(self, "license", b_license) # Because 'license' is reserved in Python
        self.extent = extent
        self.links = links
        if title: self.title = title
        if keywords: self.keywords = keywords
        if providers: self.providers = providers
        if version: self.version = version
        if properties: self.properties = properties
