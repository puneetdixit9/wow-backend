import stomp


class StompConnection:
    def __init__(self):
        self.host = "52.54.183.1"
        self.port = 61613
        self.username = "admin"
        self.password = "1m2p3k4n"
        self.conn = None
        self.connect()

    def connect(self):
        self.conn = stomp.Connection(host_and_ports=[(self.host, self.port)])
        self.conn.connect(self.username, self.password, wait=True)

    def send_message(self, body, destination):
        if not self.conn:
            raise RuntimeError("Not connected to STOMP server.")

        self.conn.send(body=body, destination=destination)
        print("Message sent")

    def disconnect(self):
        if self.conn:
            self.conn.disconnect()
