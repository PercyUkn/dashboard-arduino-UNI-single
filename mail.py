# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from os import environ, path
from dotenv import load_dotenv
import requests
import json

BASE_DIR = path.abspath(path.dirname(__file__))
load_dotenv(path.join(BASE_DIR, ".env"))


def send_mail(category, level, fecha, color, previous_value):
    # to = ("percy.escalante.b@uni.pe", "cerojasr@uni.pe", "jpachasm@uni.pe")

    url = "https://api.sendgrid.com/v3/mail/send"
    api_key = "Bearer " + environ.get("SENDGRID_API_KEY")

    payload = json.dumps({
        "from": {
            "email": "equipo12sensores@gmail.com"
        },
        "personalizations": [
            {
                "to": [
                    {
                        "email": "percy.escalante.b@uni.pe"
                    },
                   # {
                   #     "email": "cerojasr@uni.pe"
                   # },
                   # {
                   #     "email": "jpachasm@uni.pe"
                   # }
                ],
                "dynamic_template_data": {
                    "categoria": f"{category}",
                    "nivel": f"{level}",
                    "fecha": f"{fecha}",
                    "color_variation": f"{color}",
                    "valor_previo": f"{previous_value}"
                }
            }
        ],
        "template_id": "d-d5347b72d40b4dcea5164258adbefb88"
    })
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

    return
