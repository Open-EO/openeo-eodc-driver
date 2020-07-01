# -*- coding: utf-8 -*-
# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2015 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import datetime

from pycsw.core import util
from pycsw.core.etree import etree

NAMESPACE = "https://github.com/radiantearth/stac-spec"
STAC_VERSION = "0.9.0"


def write_record(result, esn, context, url=None):
    """ Return csw:SearchResults child as lxml.etree.Element """

    node = etree.Element("collection")

    etree.SubElement(node, "stac_version").text = STAC_VERSION

    val = util.getqattr(result, "identifier")
    if val:
        etree.SubElement(node, "id").text = val

    val = util.getqattr(result, "abstract")
    if val:
        etree.SubElement(node, "description").text = val

    val = util.getqattr(result, "conditionapplyingtoaccessanduse")
    if val:
        etree.SubElement(node, "license").text = val

    val = util.getqattr(result, "title")
    if val:
        etree.SubElement(node, "title").text = val

    val = util.getqattr(result, "keywords")
    for keyword in val.split(","):
        etree.SubElement(node, "keywords").text = keyword

    extent = etree.SubElement(node, "extent")
    
    ext_temporal = etree.SubElement(extent, "temporal")
    interval_str = '[[' + format_time(util.getqattr(result, "time_begin")) + ',' + format_time(util.getqattr(result, "time_end")) + ']]'
    etree.SubElement(ext_temporal, "interval").text = interval_str

    ext_spatial = etree.SubElement(extent, "spatial")
    val = util.getqattr(result, context.md_core_model["mappings"]["pycsw:BoundingBox"])
    if val:
        bbox = util.wkt2geom(val)
        etree.SubElement(ext_spatial, "bbox").text = '[' + str(list(bbox)) + ']'

    return node


def format_time(timestr):
    # Always return a string so it can be concatenated
    if not timestr:
        return "None"

    # Get time obj. based on two expected time formats
    # (with time for single dataset / only date for complete data product)
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d"):
        try:
            timeobj = datetime.datetime.strptime(timestr, fmt)
        except ValueError:
            return "None"
    date_time = timeobj.strftime("%Y-%m-%dT%H:%M:%SZ")
    return date_time
