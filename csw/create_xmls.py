import json
import requests
import xml.etree.ElementTree as ET


def csw_query(identifier):
    """
    Create CSW GetRecordById query for a given identifier.
    """
    
    return f'''
<csw:GetRecordById xmlns:csw="http://www.opengis.net/cat/csw/2.0.2" service="CSW" version="2.0.2" outputSchema="http://www.isotc211.org/2005/gmd">
  <csw:Id>{identifier}</csw:Id>
  <csw:ElementSetName>full</csw:ElementSetName>
</csw:GetRecordById>
'''


def write_xmls(csw_url: str, to_import: str):
    """
    Queries a CSW server for the given identifiers, changes the url and returns it in gmd:MD_Metadata format.
    """
    
    files = json.load(open(to_import))
    for item in files:
        response = requests.post(csw_url, data=csw_query(item['identifier']))
        xml_response = response.text

        tree = ET.fromstring(xml_response)
        gmd = '{http://www.isotc211.org/2005/gmd}'
        md_metadata = tree.find(f'{gmd}MD_Metadata')

        # Replace filepath
        url = md_metadata.find(
            f'{gmd}distributionInfo/{gmd}MD_Distribution/{gmd}transferOptions/{gmd}MD_DigitalTransferOptions/{gmd}onLine/{gmd}CI_OnlineResource/{gmd}linkage/{gmd}URL')
        url.text = item['local_filepath']

        xml = ET.tostring(md_metadata).decode()

        with open(f"xml/{item['identifier']}.xml", "w") as f:
            f.write(xml)


if __name__ == '__main__':
    cur_csw_url = 'https://csw.eodc.eu'
    filename = 'file_list.json'
    write_xmls(cur_csw_url, filename)
