import requests
from data_structures import *

from APIKeys import *

url = "http://api.nessieisreal.com/"
headers = {
    "Content-Type": "application/json",
    "Accept": "*/*"
    # "Authorization": f"Bearer {NESSIE_API_KEY}"
}


def add_user(name):
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
        return resp.json()['objectCreated']['_idx']
    except requests.exceptions.RequestException as e:
        print(e)


def add_user_account(user):
    payload = {
      "type": "Credit Card",
      "nickname": "string",
      "rewards": 0,
      "balance": user.balance,
      "account_number": "1",
      "customer_id": user.id
    }

    try:
        resp = requests.post(f"{url}customers/{user.id}/accounts?key={NESSIE_API_KEY}", headers=headers, json=payload)
        print(resp.json())
        # return resp.json()['objectCreated']['_idx']
    except requests.exceptions.RequestException as e:
        print(e)


def get_user_info(id):
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


def create_full_user(name, balance, salary):
    user_id = add_user(name)
    user = User(user_id, name, balance, salary)
