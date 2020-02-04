FROM geopython/pycsw

# Hotfix iso return schema
USER root
COPY changed_files/apiso.py /usr/lib/python3.5/site-packages/pycsw/plugins/profiles/apiso/apiso.py

# Add stac outputSchema
COPY changed_files/stac.py /usr/lib/python3.5/site-packages/pycsw/plugins/outputschemas/stac.py
COPY changed_files/outputschema__init__.py /usr/lib/python3.5/site-packages/pycsw/plugins/outputschemas/__init__.py

USER pycsw
