"""This domain module provides required data classes.

This is not a database model! The data service does not have a dedicated database associated.
The classes defined here are rather classic simple classes - mainly NamedTuples - used to ensure fixed data structures.
"""
import logging
from typing import Dict, List, NamedTuple, Optional

LOGGER = logging.getLogger("standardlog")


class SpatialExtent(NamedTuple):
    """Stores a list of bounding boxes."""

    bbox: List[List[float]]
    """A list of bounding boxes.

    Each bounding box consists of four or six elements.
    """


class TemporalExtent(NamedTuple):
    """Stores a list of time intervals."""

    interval: List[List[str]]
    """A list of time intervals.

    A time interval is given as a start and end time.
    """


class Extent(NamedTuple):
    """Combines spatial and temporal extent."""

    spatial: SpatialExtent
    temporal: TemporalExtent


class Providers:
    """Represents Providers.

    Currently not implemented - content is not available.
    """

    # Missing items in DB


class Link(NamedTuple):
    """Represents a single Link."""

    href: str
    """A valid URI."""
    rel: str
    """Describes the relation between the current and the linked document."""
    type_: Optional[str] = None
    """Hints at the format used to represent data at the provided URI.

    Preferably a media (MIME) type.
    """
    title: Optional[str] = None
    """Human readable label for the link."""

    def to_dict(self) -> Dict[str, str]:
        """Serialise link object to a dictionary."""
        ret = {
            "href": self.href,
            "rel": self.rel,
        }
        if self.type_:
            ret.update({"type": self.type_})
        if self.title:
            ret.update({"title": self.title})
        return ret


class Band(NamedTuple):
    """Represents a single band."""

    band_id: str
    wavelength_nm: float
    """Center wavelength in nanometers"""
    res_m: int
    """Spatial resolution in meters."""
    scale: float
    offset: int
    b_type: str
    unit: str
    name: str = ""


class Collection(NamedTuple):
    """Represents a single collection.

    For more details see `OpenEO API EO Data Discovery`_.
    """

    stac_version: str
    """The applying `version of the STAC specification`_"""
    id_: str
    """Unique identifier of the collection."""
    description: str
    """Detailed multi-line description to explain the collection."""
    license_: str
    """License of the data."""
    extent: Extent
    """Spatial and temporal extent of the collection."""
    links: list
    """Links related to this collection."""
    title: Optional[str] = None
    """A short descriptive one-line title of the collection."""
    keywords: Optional[List[str]] = None
    """List of keywords describing the collection."""
    providers: Optional[List[str]] = None
    """List of providers."""
    version: Optional[str] = None
    """Version of the collection."""

    def __repr__(self) -> str:
        """Return human readable version of the collection."""
        return f"Collection({self.id_})"


class Collections(NamedTuple):
    """Represents a list of collections with associated links."""

    collections: List[Collection]
    """A List of collections."""
    links: List[dict]
    """A list of links related to the collection."""

    def __repr__(self) -> str:
        """Return human readable version of the collections."""
        return f"Collections({self.collections})"
