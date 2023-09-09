import stomp


class MyListener(stomp.ConnectionListener):
    def on_error(self, frame):
        print("Received an error:", frame.body)

    def on_message(self, frame):
        print("Received a message:", frame.body)


conn = stomp.Connection(host_and_ports=[("52.54.183.1", 61613)])
conn.set_listener("", MyListener())

try:
    conn.connect("admin", "1m2p3k4n", wait=True)

    conn.subscribe(destination="/queue/test", id=1, ack="auto")  # Subscribe to the queue

    print("Waiting for messages. To exit press Ctrl+C")

    while True:
        pass  # Keep the script running to continue receiving messages

except KeyboardInterrupt:
    conn.disconnect()
