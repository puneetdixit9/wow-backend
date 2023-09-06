import json
import os

import requests

url = "https://www.fast2sms.com/dev/bulkV2"
API_KEY = os.getenv("SMS_API_KEY", "")


def send_otp_sms_to_number(otp: str, number: str):
    """
    To send otp to a number
    :param otp:
    :type otp:
    :param number:
    :type number:
    :return:
    :rtype:
    """
    payload = json.dumps({"route": "otp", "variables_values": str(otp), "numbers": str(number)})

    headers = {"Content-Type": "application/json", "authorization": API_KEY}

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()
