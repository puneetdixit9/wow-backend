# import time
# import stomp
#
#
# class MyListener(stomp.ConnectionListener):
#     def on_error(self, frame):
#         print('Received an error:', frame)
#
#     def on_message(self, headers, body):
#         print('Received a message:', body)
#
#
# conn = stomp.Connection(host_and_ports=[('52.54.183.1', 61613)])
# conn.set_listener('', MyListener())
#
# try:
#     conn.connect("admin", '1m2p3k4n', wait=True)
#
#     conn.send(body='Testing STOMP connection', destination='/queue/test')
#     print('Message sent')
#
#     time.sleep(2)  # Allow time for message to be received
#
#     conn.disconnect()
# except KeyboardInterrupt:
#     conn.disconnect()


import time

import stomp

conn = stomp.Connection(host_and_ports=[("52.54.183.1", 61613)])

try:
    conn.connect("admin", "1m2p3k4n", wait=True)

    conn.send(body="Testing STOMP connection 5 ", destination="/queue/test")
    print("Message sent")

    time.sleep(2)  # Allow time for message to be received

    conn.disconnect()
except KeyboardInterrupt:
    conn.disconnect()


# import time
# import stomp
#
#
# class MyListener(stomp.ConnectionListener):
#     def on_error(self, frame):
#         print('Received an error:', frame)
#
#     def on_message(self, headers, body):
#         print('Received a message:', body)
#
#
# conn = stomp.Connection(host_and_ports=[('52.54.183.1', 61613)])
# conn.set_listener('', MyListener())
#
# try:
#     conn.connect("admin", '1m2p3k4n', wait=True)
#
#     conn.send(body='Testing STOMP connection', destination='/queue/test')
#     print('Message sent')
#
#     time.sleep(2)  # Allow time for message to be received
#
#     conn.disconnect()
# except KeyboardInterrupt:
#     conn.disconnect()
