import json
import requests


def csw_query(identifier):
    """
    
    """
    
    return f'''
<csw:GetRecordById xmlns:csw="http://www.opengis.net/cat/csw/2.0.2" service="CSW" version="2.0.2" outputSchema="http://www.isotc211.org/2005/gmd">
  <csw:Id>{identifier}</csw:Id>
  <csw:ElementSetName>full</csw:ElementSetName>
</csw:GetRecordById>
'''


def write_xmls(csw_url, to_import):
    """
    
    """
    
    files = json.load(open(to_import))
    for item in files:
        response = requests.post(csw_url, data=csw_query(item['identifier']))
        xml = response.text
        # Replace filepath
        start = xml.find("<gmd:URL>") + len("<gmd:URL>")
        end = xml.find("</gmd:URL>")
        xml = xml.replace(xml[start:end], item['local_filepath'])
        
        with open(f"xml/{item['identifier']}.xml", "w") as f:
            f.write(xml)  


csw_url = 'https://csw.eodc.eu'
to_import = 'file_list.json'
write_xmls(csw_url, to_import)
