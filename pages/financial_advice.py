import os
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv
import json

load_dotenv()
CEREBRAS_API_KEY = os.getenv('CEREBRAS_API_KEY')
client = Cerebras(
    api_key=os.environ.get(CEREBRAS_API_KEY)
)


def categorize_user_expenses(user_obj):
    expenses = []
    for i in user_obj.purchases:
        expenses.append([i.name])

    categories = ['Housing', 'Transportation', 'Food', 'Entertainment & Leisure', 'Healthcare', 'Savings & Investments']
    prompt = "Categorize the following expenses into " + str(categories) + " outputted in a JSON format with the item bought as the key and the category as a corresponding value: " + str(
        expenses) + ". Output nothing else outside of the JSON list, no additional text or ``` characters at all, just the json, as your output will be parsed by an algorithm. Make sure all the items you include are actually real items, exclude things that don't seem like real items. Here is an example json schema: " + '''
        [
            {name: item_name1, cat: category_name1},
            {name: item_name2, cat: category_name2},
            {name: item_name3, cat: category_name3},
            ...
        ]
        '''

    print(prompt)
    response = client.chat.completions.create(
        model="llama3.1-8b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    print(response.choices[0].message.content)
    res = json.loads(response.choices[0].message.content)
    print(res)
    category_map = {}
    for i in range(len(res)):
        if not res[i]['name'] in category_map:
            print(res[i])
            category_map[res[i]['name']] = res[i]['cat']

    for i in user_obj.purchases:
        if i.name in category_map:
            i.category = category_map[i.name]

    return user_obj


def categorize_expenses(expenses):
    prompt = "Place the following expenses from this receipt into the following JSON format (not a list of JSONs) with the item bought as the key and the price as a corresponding value: " + str(
        expenses) + ". Also include the date of the purchase as a field. Output nothing else outside of the JSON, no additional text and no comments and no ``` characters as your output will be parsed by an algorithm. Make sure all the items you include are actually real items, exclude things that don't seem like real items. Here is an example json schema: " + '''
        {
            "date": date, 
            item_name1: {"price": price},
            item_name2: {"price": price},
            item_name3: {"price": price},
            ...
        }
        '''


    # print(prompt)
    response = client.chat.completions.create(
        model="llama3.1-8b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


def finance_chat_bot(user_info, question):
    prompt = (
        "You are an expert financial advisor with extensive knowledge in personal finance, investment strategies, and economic principles. "
        "The following user has provided their monthly financial information in JSON format:\n"
        f"{str(user_info)}\n"
        "Your task is to conduct a comprehensive analysis of their financial situation and respond to the following inquiry:\n"
        f"{str(question)}\n"
        "In your response, consider key financial metrics such as cash flow, debt-to-income ratio, and savings rate. "
        "Evaluate their current asset allocation and suggest optimal diversification strategies. "
        "Identify potential areas for cost reduction, including discretionary spending and fixed expenses, and provide detailed budgeting techniques. "
        "Discuss the implications of their financial decisions on long-term wealth accumulation and risk management. "
        "Incorporate relevant financial theories and concepts, such as the time value of money and compound interest, to substantiate your recommendations. "
        "Ensure your advice is actionable, precise, and tailored to their unique financial circumstances."
    )
    print(prompt)
    response = client.chat.completions.create(
        model="llama3.1-8b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content 


# dummy_expenses = [
#     {"item": "Rent", "price": 1500},
#     {"item": "Bus Ticket", "price": 2.5},
#     {"item": "Groceries", "price": 200},
#     {"item": "Movie Ticket", "price": 15},
#     {"item": "Doctor Visit", "price": 100}
# ]
#
# print(categorize_expenses(dummy_expenses))
#
# categorize_expenses(["item1", "item2", "item3"])
#
# user = {
#     "name": "John Doe",
#     "monthly salary": 5000,
#     "expenses": {
#         "housing": 1500,
#         "transportation": 500,
#         "food": 800,
#         "entertainment/leisure": 200,
#         "healthcare": 300,
#         "savings/investments": 1000
#     }
# }
# print(finance_chat_bot(user, "how can i lower my expenses?"))
