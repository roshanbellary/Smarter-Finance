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
