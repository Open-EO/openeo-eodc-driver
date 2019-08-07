def subscription(ws):
    while not ws.closed:
        message = ws.receive()
        print('Received message: ' + message)
        ws.send(message)
