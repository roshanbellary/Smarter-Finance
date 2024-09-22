import requests
import os
NESSIE_API_KEY = os.getenv('CAPITAL_ONE_API_KEY')
url = "http://api.nessieisreal.com/"
headers = {
    "Content-Type": "application/json",
    "Accept": "*/*"
    # "Authorization": f"Bearer {NESSIE_API_KEY}"
}


def create_user(name):
    payload = {
        "first_name": name.split(" ")[0],
        "last_name": name.split(" ")[1],
        "address": {
            "street_number": "string",
            "street_name": "string",
            "city": "string",
            "state": "TX",
            "zip": "76006"
        }
    }

    try:
        resp = requests.post(f"{url}customers?key={NESSIE_API_KEY}", headers=headers, json=payload)
        print(resp.json())
    except requests.exceptions.RequestException as e:
        print(e)


create_user("Eshan Singhal")
