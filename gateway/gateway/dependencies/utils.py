"""Utility functions needed in the Gateway."""
from flask import request


class GatewayUtils:
    """Provide a set of utility functions useful in the gateway."""

    def fix_transfer_encoding(self) -> None:
        """Sets the "wsgi.input_terminated" environment flag.

        Thus enabling Werkzeug to pass chunked requests as streams. The gunicorn server should set this, but it is not
        yet been implemented.
        """
        transfer_encoding = request.headers.get("Transfer-Encoding", None)
        if transfer_encoding == u"chunked":
            request.environ["wsgi.input_terminated"] = True
