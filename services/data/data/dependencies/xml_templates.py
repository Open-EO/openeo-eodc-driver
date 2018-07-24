xml_base = (
    "<?xml version='1.0' encoding='ISO-8859-1' standalone='no'?>"
    "<csw:GetRecords "
    "xmlns:csw='http://www.opengis.net/cat/csw/2.0.2' "
    "xmlns:ogc='http://www.opengis.net/ogc' "
    "service='CSW' "
    "version='2.0.2' "
    "resultType='results' "
    "startPosition='{start_position}' "
    "maxRecords='1000' "
    "outputFormat='application/json' "
    "outputSchema='{output_schema}' "
    "xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' "
    "xsi:schemaLocation='http://www.opengis.net/cat/csw/2.0.2 http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd' "
    "xmlns:gml='http://www.opengis.net/gml' "
    "xmlns:gmd='http://www.isotc211.org/2005/gmd' "
    "xmlns:apiso='http://www.opengis.net/cat/csw/apiso/1.0'>"
    "<csw:Query typeNames='csw:Record'>"
    "<csw:ElementSetName>full</csw:ElementSetName>"
    "<csw:Constraint version='1.1.0'>"
    "<ogc:Filter>"
    "{children}"
    "</ogc:Filter>"
    "</csw:Constraint>"
    "<ogc:SortBy>"
    "<ogc:SortProperty>"
    "<ogc:PropertyName>dc:date</ogc:PropertyName>"
    "<ogc:SortOrder>ASC</ogc:SortOrder>"
    "</ogc:SortProperty>"
    "</ogc:SortBy>"
    "</csw:Query>"
    "</csw:GetRecords>")

xml_and = (
    "<ogc:And>"
    "{children}"
    "</ogc:And>")

xml_series = (
    "<ogc:PropertyIsEqualTo>"
    "<ogc:PropertyName>apiso:Type</ogc:PropertyName>"
    "<ogc:Literal>series</ogc:Literal>"
    "</ogc:PropertyIsEqualTo>")

xml_product = (
    "<ogc:PropertyIsEqualTo>"
    "<ogc:PropertyName>{property}</ogc:PropertyName>"
    "<ogc:Literal>{product}</ogc:Literal>"
    "</ogc:PropertyIsEqualTo>")

xml_begin = (
    "<ogc:PropertyIsGreaterThanOrEqualTo>"
    "<ogc:PropertyName>apiso:TempExtent_begin</ogc:PropertyName>"
    "<ogc:Literal>{start}</ogc:Literal>"
    "</ogc:PropertyIsGreaterThanOrEqualTo>")

xml_end = (
    "<ogc:PropertyIsLessThanOrEqualTo>"
    "<ogc:PropertyName>apiso:TempExtent_end</ogc:PropertyName>"
    "<ogc:Literal>{end}</ogc:Literal>"
    "</ogc:PropertyIsLessThanOrEqualTo>")

xml_bbox = (
    "<ogc:BBOX>"
    "<ogc:PropertyName>ows:BoundingBox</ogc:PropertyName>"
    "<gml:Envelope>"
    "<gml:lowerCorner>{bbox.x1} {bbox.y1}</gml:lowerCorner>"
    "<gml:upperCorner>{bbox.x2} {bbox.y2}</gml:upperCorner>"
    "</gml:Envelope>"
    "</ogc:BBOX>")
