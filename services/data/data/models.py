""" Models """
import logging

LOGGER = logging.getLogger("standardlog")


class Extent:  # noqa
    """ Represents spatial and temporal extent """

    def __init__(self, spatial: list, temporal: list) -> None:
        self.spatial = spatial
        self.temporal = temporal


class Providers:
    """ Represents Providers """

    # Missing items in DB


class Link:
    """ Represents Links """

    def __init__(self, href: str, rel: str, b_type: str = None, title: str = None) -> None:
        self.href = href
        self.rel = rel
        self.type = b_type
        if title:
            self.title = title


class Band:
    """ Represents a single band. """

    def __init__(
        self,
        band_id: str,
        wavelength_nm: float,
        res_m: int,
        scale: float,
        offset: int,
        b_type: str,
        unit: str,
        name: str = None,
    ) -> None:
        self.band_id = band_id
        self.name = name if name else ""
        self.wavelength_nm = wavelength_nm
        self.res_m = res_m
        self.scale = scale
        self.offset = offset
        self.type = b_type
        self.unit = unit


class Collection:
    """ Represents a single collection """

    def __init__(
        self,
        stac_version: str,
        b_id: str,
        description: str,
        b_license: str,
        extent: Extent,
        links: list,
        title: str = None,
        keywords: list = None,
        providers: list = None,
        version: str = None,
    ) -> None:
        self.stac_version = stac_version
        self.id = b_id
        self.description = description
        self.license = b_license
        self.extent = extent
        self.links = links
        if title:
            self.title = title
        if keywords:
            self.keywords = keywords
        if providers:
            self.providers = providers
        if version:
            self.version = version

        LOGGER.debug(f"Initialized {self} from CSW")

    def __repr__(self) -> str:
        return f"Collection({self.id})"


class Collections:
    """ Represents multiple collections """

    def __init__(self, collections: list, links: list) -> None:
        self.collections = collections
        self.links = links
        LOGGER.debug("Initialized %s", self)

    def __repr__(self) -> str:
        return f"Collections({self.collections})"
