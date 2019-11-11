FROM geopython/pycsw

# Hotfix iso return schema
USER root
RUN sed -i -e "s/if caps is None and xml_blob is not None and xml_blob.startswith(b'<gmd:MD_Metadata')/if caps is None and xml_blob is not None and xml_blob.startswith('<gmd:MD_Metadata')/g" /usr/lib/python3.5/site-packages/pycsw/plugins/profiles/apiso/apiso.py
USER pycsw
