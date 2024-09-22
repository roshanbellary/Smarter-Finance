import os
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

load_dotenv()
CEREBRAS_API_KEY = os.getenv('CEREBRAS_API_KEY')
client = Cerebras(
    api_key=os.environ.get(CEREBRAS_API_KEY)
)

def categorize_expenses(expenses):
    categories = ['Housing', 'Transportation', 'Food', 'Entertainment & Leisure', 'Healthcare', 'Savings & Investments']
    prompt = "Categorize the following expenses from this receipt into " + str(categories) + " outputted in a JSON format (not a list of JSONs) with the item bought as the key and the category and price as corresponding values: " + str(
        expenses) + ". Also include the date of the purchase a field. Output nothing else outside of the JSON, no additional text, just the json, as your output will be parsed by an algorithm. Make sure all the items you include are actually real items, exclude things that don't seem like real items. Here is an example json schema: " + '''
        {
            "date": date, 
            item_name1: {"category": category, "price": price},
            item_name2: {"category": category, "price": price},
            item_name3: {"category": category, "price": price},
            ...
        }
        '''


    print(prompt)
    response = client.chat.completions.create(
        model="llama3.1-8b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response


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
