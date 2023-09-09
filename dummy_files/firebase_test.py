# # import time
#
# import firebase_admin
# from firebase_admin import credentials, db, messaging
#
# # Use a raw string to specify the file path
# cred = credentials.Certificate(
#     r"C:\Users\PuneetDixit\Desktop\wow-backend\wow-pizza-21db7-firebase-adminsdk-hejvy-83470f5a1e.json"
# )
# firebase_admin.initialize_app(
#     cred, {"databaseURL": "https://wow-pizza-21db7-default-rtdb.asia-southeast1.firebasedatabase.app"}
# )
#
# # root = db.reference()
# #
# # data = {
# #     "timestamp": int(time.time() * 1000),
# #     "msg": "2x Large Pizza, 1x Small Coke"
# # }
# # root.child("Orders/").push(data)
# # print("msg sent")
#
#
# # Create a message
# messages = messaging.MulticastMessage(
#     data={
#         "title": "Order Picked Up",
#         "body": "Your order no 101 is picked up and will be deliver soon.",
#     },
#     tokens=[
#         "eEI1gQP2QIiVYBA_6rXPpG:APA91bHy3bUEpFNq_FckpmWVnRhF9ftEmHzfq_4-uH_eOPh20CzhP_WkbWrMZ4wwf4sE8WopH6LkuovWbOkmILgj05kDAUMeczuZKp1ekcesvb7heCJpPC-4OFOtyM9Ujllj2UMnnZL_",
#         "fe2HAbkF9R7S0Jmu6XbyD0P:APA91bEpWv9IJ-zoeN9ZqYsrqNP2GBWGcaCJyZnDdIWglYNkF-uu-yicpA5TyLs8jWxZnL9zH4NVZDXlT7QrIOaulbQvcXqO-WQ8dOZSk_CITx_d7WJswKHv5AVZaWjX9I4qWoLWnAV-",
#     ],
# )
#
# # Send the message
# response = messaging.send_each_for_multicast(messages)
#
# # Print the message ID
# print("Successfully sent message:", response)
#
#
# # import requests
# # import json
# #
# # serverToken = 'AAAA_qAF8fQ:APA91bFkPOzEaKFUZxT1bZOzeT_0VY4EvaGfG5Oy4iO7_0YkjtLj_SGEHZ6QXnrH48_T4v6wQPGJa8zr9NgA7p7_CqUy0fHL30wMU8OnfvolNpItaZGMYogBByVAQmITayrkRODoDGj9'
# # deviceToken = 'fxqwsS3DS7G6h1s-GBBRqR:APA91bEiV9qhO2jG37PVmcwnuWMvvjhhwDwrmL98or8v-RQbIIMZdVtr8NPf3zzQ5WQbdw5oBEOy-krhg9gu1WWOflDHFvnj2zgsnFVJKBk1FaEAED06LVEGVlmMPTKrKpLRdSnVrKJ6'
# #
# # headers = {
# #     'Content-Type': 'application/json',
# #     'Authorization': 'key=' + serverToken,
# # }
# #
# # body = {
# #     'notification': {
# #         'title': 'Order Picked Up',
# #         'body': 'Your order is picked up and will be deliver soon.'
# #         },
# #     'to': deviceToken,
# #     'priority': 'high',
# # }
# # response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
# # print(response.status_code)
# #
# # print(response.json())
