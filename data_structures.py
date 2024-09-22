class User:
    def __init__(self, user_id, account_id, name, salary, balance, purchases):
        self.id = user_id
        self.account_id = account_id
        self.name = name
        self.salary = salary
        self.balance = balance
        self.purchases = purchases


class Purchase:
    def __init__(self, name, price, date, category):
        self.name = name
        self.price = price
        self.date = date
        self.category = category
