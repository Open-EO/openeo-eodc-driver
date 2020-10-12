"""WSGI entrypoint to gateway.

Used in run.sh to run the gateway service.
"""
from gateway import gateway

app = gateway.get_service()
