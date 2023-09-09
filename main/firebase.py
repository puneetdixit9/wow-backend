import os
import time

import firebase_admin
from firebase_admin import credentials, db, messaging

basedir = os.path.abspath(os.path.dirname(__file__))
firebase_credentials = os.path.join(os.path.dirname(basedir), "firebase_credentials.json")

cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred, {"databaseURL": os.environ.get("FIREBASE_DATABASE_URL")})


def new_order_placed_notification(collection: str, message: str):
    try:
        root = db.reference()
        data = {
            "msg": message,
            "timestamp": int(time.time() * 1000),
        }

        root.child(collection).push(data)
    except Exception as e:
        print("Exception : ", e)


def send_push_notification(device_tokens: list, data: dict):
    try:
        messages = messaging.MulticastMessage(data=data, tokens=device_tokens)

        messaging.send_each_for_multicast(messages)
        print("------> published")
    except Exception as e:
        print("Exception : ", e)
