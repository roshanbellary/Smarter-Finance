import requests
from data_structures import *
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

NESSIE_API_KEY = os.getenv('CAPITAL_ONE_API_KEY')
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
        return resp.json()['objectCreated']['_id']
    except requests.exceptions.RequestException as e:
        print(e)


def add_user_account(user):
    payload = {
      "type": "Credit Card",
      "nickname": "string",
      "rewards": user.salary,
      "balance": user.balance,
    }

    try:
        resp = requests.post(f"{url}customers/{user.id}/accounts?key={NESSIE_API_KEY}", headers=headers, json=payload)
        print(resp.json())
        return resp.json()['objectCreated']['_id']
    except requests.exceptions.RequestException as e:
        print(e)


def add_user_purchase(user, date, price, description):
    payload = {
      "merchant_id": user.account_id,
      "medium": "balance",
      "purchase_date": date.strftime("%Y-%m-%d"),
      "amount": price,
      "status": "pending",
      "description": description
    }

    try:
        resp = requests.post(f"{url}accounts/{user.account_id}/purchases?key={NESSIE_API_KEY}", headers=headers, json=payload)
        print(resp.json())
    except requests.exceptions.RequestException as e:
        print(e)


def get_user(user_id):
    try:
        user_resp = requests.get(f"{url}customers/{user_id}?key={NESSIE_API_KEY}", headers=headers)
        acc_resp = requests.get(f"{url}customers/{user_id}/accounts?key={NESSIE_API_KEY}", headers=headers)
        print(user_resp.json())
        print(acc_resp.json())
        user = User(user_id, acc_resp.json()["account_number"], f"{user_resp.json()['first_name']} {user_resp.json()['last_name']}",
                    acc_resp.json()['rewards'], acc_resp.json()['balance'], [])

        purchase_resp = requests.get(f"{url}accounts/{user.account_id}/purchases?key={NESSIE_API_KEY}", headers=headers)
        for i in purchase_resp.json():
            user.purchases.append(Purchase(i["description"], i["amount"],
                                           datetime.strftime(i["purchase_date"], "%Y-%m-%d"), None))

        print(purchase_resp.json())
        return user
    except requests.exceptions.RequestException as e:
        print(e)


def create_full_user(name, balance, salary, purchase_file):
    user_id = add_user(name)
    user = User(user_id, "", name, balance, salary, [])
    account_id = add_user_account(user)
    user.account_id = account_id

    with open(purchase_file, 'r') as file:
        for line in file:
            name, price, date = line.split('; ')
            print(date)
            date = datetime.strptime(date, "%Y-%m-%d\n")
            add_user_purchase(user, date, price, name)
            user.purchases.append(Purchase(name, price, date, None))

    return user


# create_full_user("Eshan Singhal", 30000, 5000, "C:\\Users\\eshan\\Desktop\\Coding Projects\\Receipt-To-Split\\Eshan Singhal Purchases.txt")
user_id = "66ef77b99683f20dd518a6db"
user = get_user(user_id)
print(user)