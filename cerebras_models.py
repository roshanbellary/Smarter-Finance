import os
from cerebras.cloud.sdk import Cerebras

CEREBRAS_API_KEY = ""
client = Cerebras(
    api_key=os.environ.get(CEREBRAS_API_KEY)
)


def categorize_expenses(expenses):
    categories = ['Housing', 'Transportation', 'Food', 'Entertainment & Leisure', 'Healthcare', 'Savings & Investments']
    prompt = "Categorize the following expenses into " + str(categories) + " outputted in a JSON format: " + str(
        expenses)
    print(prompt)
    response = client.chat.completions.create(
        model="llama3.1-8b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )


def finance_chat_bot(user_info, question):
    prompt = "You are a financial advising expert for the following user who's monthly financial information is in JSON format:\n" + \
             str(user_info) + "\nAnswer the following question relating to their finances and give advice on how they " \
                              "can improve their financial state: " + str(question)
    print(prompt)
    response = client.chat.completions.create(
        model="llama3.1-8b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )


categorize_expenses([])

user = {
    "name": "",
    "monthly salary": "",
    "expenses": {
        "housing": "",
        "transportation": "",
        "food": "",
        "entertainment/leisure": "",
        "healthcare": "",
        "savings/investments": ""
    }
}
finance_chat_bot(user, "how can i lower my expenses?")
