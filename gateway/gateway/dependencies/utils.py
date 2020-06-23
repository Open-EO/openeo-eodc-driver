from flask import request


class GatewayUtils:

    def fix_transfer_encoding(self):
        """
        Sets the "wsgi.input_terminated" environment flag, thus enabling
        Werkzeug to pass chunked requests as streams.  The gunicorn server
        should set this, but it's not yet been implemented.
        """

        transfer_encoding = request.headers.get("Transfer-Encoding", None)
        if transfer_encoding == u"chunked":
            request.environ["wsgi.input_terminated"] = True
