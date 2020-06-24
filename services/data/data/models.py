""" Models """
import logging
from typing import List, NamedTuple, Optional

LOGGER = logging.getLogger("standardlog")


class SpatialExtent(NamedTuple):
    bbox: List[List[float]]


class TemporalExtent(NamedTuple):
    interval: List[List[str]]


class Extent(NamedTuple):
    """ Represents spatial and temporal extent """

    spatial: SpatialExtent
    temporal: TemporalExtent


class Providers:
    """ Represents Providers """

    # Missing items in DB


class Link(NamedTuple):
    """ Represents Links """

    href: str
    rel: str
    type: Optional[str] = None
    title: Optional[str] = None

    def to_dict(self) -> dict:
        ret = {
            "href": self.href,
            "rel": self.rel,
        }
        if self.type:
            ret.update({"type": self.type})
        if self.title:
            ret.update({"title": self.title})
        return ret


class Band:
    """ Represents a single band. """

    band_id: str
    wavelength_nm: float
    res_m: int
    scale: float
    offset: int
    b_type: str
    unit: str
    name: str = ""


class Collection(NamedTuple):
    """ Represents a single collection """

    stac_version: str
    id: str
    description: str
    license: str
    extent: Extent
    links: list
    title: Optional[str] = None
    keywords: Optional[List[str]] = None
    providers: Optional[List[str]] = None
    version: Optional[str] = None

    def __repr__(self) -> str:
        return f"Collection({self.id})"


class Collections(NamedTuple):
    """ Represents multiple collections """

    collections: List[Collection]
    links: List[Link]

    def __repr__(self) -> str:
        return f"Collections({self.collections})"
