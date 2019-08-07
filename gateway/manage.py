from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

from gateway import gateway


app = gateway.get_service()


if __name__ == "__main__":

    server = pywsgi.WSGIServer(('', 3000), app, handler_class=WebSocketHandler)
    server.serve_forever()
