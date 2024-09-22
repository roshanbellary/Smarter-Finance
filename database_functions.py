import requests
from data_structures import User, Purchase
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

NESSIE_API_KEY = os.getenv('CAPITAL_ONE_API_KEY')
MERCHANT_ID = os.getenv('MERCHANT_ID')
DATAFILE = os.getenv('DATAFILE')
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
      "merchant_id": MERCHANT_ID,
      "medium": "balance",
      "purchase_date": date.strftime("%Y-%m-%d"),
      "amount": int(float(price)),
      "status": "pending",
      "description": description
    }

    try:
        print(payload)
        print(f"{url}accounts/{user.account_id}/purchases?key={NESSIE_API_KEY}")
        resp = requests.post(f"{url}accounts/{user.account_id}/purchases?key={NESSIE_API_KEY}", headers=headers, json=payload)
        print(resp.json())
    except requests.exceptions.RequestException as e:
        print(e)


def get_user(user_id):
    try:
        user_resp = requests.get(f"{url}customers/{user_id}?key={NESSIE_API_KEY}", headers=headers).json()
        # acc_resp = requests.get(f"{url}customers/{user_id}/accounts?key={NESSIE_API_KEY}", headers=headers).json()
        # if len(acc_resp) == 0:
        #     add_user_account(user_id)
        acc_resp = requests.get(f"{url}customers/{user_id}/accounts?key={NESSIE_API_KEY}", headers=headers).json()
        user = User(user_id, acc_resp[0]['_id'], f"{user_resp['first_name']} {user_resp['last_name']}",
                    acc_resp[0]['rewards'], acc_resp[0]['balance'], [])

        purchase_resp = requests.get(f"{url}accounts/{user.account_id}/purchases?key={NESSIE_API_KEY}", headers=headers)
        for i in purchase_resp.json():
            user.purchases.append(Purchase(i["description"], i["amount"],
                                           datetime.strptime(i["purchase_date"], "%Y-%m-%d"), None))

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


def make_merchant():
    payload = {
      "name": "merchant",
      "category": "string",
      "address": {
        "street_number": "string",
        "street_name": "string",
        "city": "string",
        "state": "TX",
        "zip": "76006"
      },
      "geocode": {
        "lat": 0,
        "lng": 0
      }
    }
    resp = requests.post(f"{url}merchants?key={NESSIE_API_KEY}", headers=headers, json=payload).json()
    print(resp)


def clear_db():
    accounts = requests.get(f"{url}accounts?key={NESSIE_API_KEY}", headers=headers).json()
    print(accounts)
    for i in accounts:
        requests.delete(f"{url}accounts/{i['_id']}?key={NESSIE_API_KEY}", headers=headers)


# create_full_user("Eshan Singhal", 30000, 5000, DATAFILE)
user_id = "66efc0e89683f20dd518a9ca"
user = get_user(user_id)
print(user.purchases)
# clear_db()
# make_merchant()
