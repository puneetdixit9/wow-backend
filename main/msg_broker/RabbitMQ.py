import pika
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
        print("Stomp connection established")

    def broadcast_to_exchange(self, exchange_name: str, body: str):
        """
        To broadcast a msg to an exchange, all subscribers will get the notification.
        :param exchange_name:
        :type exchange_name:
        :param body:
        :type body:
        :return:
        :rtype:
        """
        if not self.conn:
            raise RuntimeError("Not connected to STOMP server.")

        self.conn.send(body=body, destination=f"/exchange/{exchange_name}")
        print(f"Message broadcast done to exchange: {exchange_name}")

    def send_to_queue(self, queue_name: str, body: str):
        """
        To send a msg to the queue, any one from the subscribers will get the msg notification.
        :param queue_name:
        :type queue_name:
        :param body:
        :type body:
        :return:
        :rtype:
        """
        if not self.conn:
            raise RuntimeError("Not connected to STOMP server.")

        self.conn.send(body=body, destination=f"/queue/{queue_name}")
        print(f"Message sent to queue: {queue_name}")

    def disconnect(self):
        if self.conn:
            self.conn.disconnect()


class PikaConnection:
    def __init__(self):
        self.host = "52.54.183.1"
        self.port = 5672
        self.username = "admin"
        self.password = "1m2p3k4n"
        self.conn = None
        self.connect()

    def connect(self):
        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(self.host, self.port, "/", credentials)
        self.conn = pika.BlockingConnection(parameters)
        print("Pika connection established")

    def broadcast_to_exchange(self, exchange_name: str, body: str):
        """
        To broadcast a msg to an exchange, all subscribers will get the notification.
        :param exchange_name:
        :type exchange_name:
        :param body:
        :type body:
        :return:
        :rtype:
        """
        channel = self.conn.channel()
        channel.exchange_declare(exchange=exchange_name, exchange_type="fanout")
        channel.basic_publish(exchange=exchange_name, routing_key="", body=body)
        print(f"Message broadcast done to exchange: {exchange_name}")

    def send_to_queue(self, queue_name: str, body: str):
        """
        To send a msg to the queue, any one from the subscribers will get the msg notification.
        :param queue_name:
        :type queue_name:
        :param body:
        :type body:
        :return:
        :rtype:
        """
        channel = self.conn.channel()
        try:
            channel.queue_declare(queue=queue_name, durable=True)
        except pika.exceptions.ChannelClosedByBroker as e:  # noqa
            print(f"Queue {queue_name} already exists. ==>> ", e)
            channel = self.conn.channel()

        channel.basic_publish(exchange="", routing_key=queue_name, body=body)
        print(f"Message sent to queue: {queue_name}")

    def disconnect(self):
        if self.conn:
            self.conn.close()
