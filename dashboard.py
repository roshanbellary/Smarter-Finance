from datetime import timedelta

import pandas as pd
import streamlit as st
import os
import certifi
from propelauth import auth
import dotenv
from pymongo import MongoClient
from bson import ObjectId
from database_functions import get_user, add_user, add_user_account, create_full_user
from data_structures import User
from financial_advice import finance_chat_bot
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from financial_advice import *

dotenv.load_dotenv()
capital_one_api_key = os.getenv('CAPITAL_ONE_API_KEY')
mongodb_uri = os.getenv('MONGODB_URI')
data_file = os.getenv('DATAFILE')
print(data_file)
client = MongoClient(mongodb_uri, tlsCAFile=certifi.where())
db = client['smarter-finance']
group_collection = db['Groups']
user_collection = db['Users']
user = auth.get_user()
if user is None:
    st.error('Unauthorized')
    st.stop()

with st.sidebar:
    st.link_button('Account', auth.get_account_url(), use_container_width=True)

user_db = user_collection.find_one({"email": user.email})

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []


def create_user_account(user_name, user_email, user_balance, user_salary):
    user_obj = create_full_user(user_name, user_balance, user_salary, data_file)
    new_user = {
        "name": user_name,
        "email": user_email,
        "user_id": user_obj.id,
        "account_id": user_obj.account_id,
        "balance": user_balance,
        "salary": user_salary,
        "purchases": []
    }
    user_collection.insert_one(new_user)
    return user_obj.id


if user_db is None:
    st.warning("Your account is not registered in our system.")

    with st.form("create_account_form"):
        user_name = st.text_input("Enter your name", value="")
        user_balance = st.number_input("Enter your current balance", min_value=0.0, value=0.0, step=100.0)
        user_salary = st.number_input("Enter your annual salary", min_value=0.0, value=0.0, step=1000.0)
        submit_button = st.form_submit_button("Create Account")

    if submit_button:
        new_user_id = add_user_account(create_full_user(user_name, user_balance, user_salary, data_file))
        user_collection.insert_one({"name": user_name, "email": user.email, "user_id": new_user_id, "account_id": new_user_id, "balance": user_balance, "salary": user_salary, "purchases": []})
        if new_user_id:
            st.success("Account created successfully!")
            user_db = user_collection.find_one({"user_id": new_user_id})
            st.session_state['user'] = user_db
        else:
            st.error("Failed to create account. Please try again.")
else:
    st.session_state['user'] = user_db
    curr_data = get_user(st.session_state['user']['user_id'])
    while True:
        try:
            curr_data = categorize_user_expenses(curr_data)
            break
        except Exception as e:
            print(e)

    print(curr_data.purchases)
    # Welcome message
    st.header(f"Welcome, {curr_data.name}! 👋")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Current Balance", f"${curr_data.balance:.2f}")
    with col2:
        st.metric("Annual Salary", f"${curr_data.salary:.2f}")

    st.subheader("Purchase History")

    categories = ['Housing', 'Transportation', 'Food', 'Entertainment & Leisure', 'Healthcare',
                                   'Savings & Investments']
    df = pd.DataFrame([], columns=['Date'] + categories)

    for i in curr_data.purchases:
        # Convert purchase date to the start of the week (Monday)
        start_of_week = pd.to_datetime(i.date) - timedelta(days=pd.to_datetime(i.date).weekday())

        # Check if the week exists in the DataFrame
        if start_of_week not in df['Date'].values:
            # Add a new row for this week with zeros for each category
            new_row = pd.DataFrame({'Date': [start_of_week], **{cat: [0] for cat in categories}})
            df = pd.concat([df, new_row], ignore_index=True)

        # Find the index of the week
        row_index = df.index[df['Date'] == start_of_week].tolist()[0]

        # Check if the category exists, if not, add to 'Other'
        if i.category in categories:
            df.at[row_index, i.category] += i.price
        else:
            print(f"Warning: Unknown category '{i.category}' for purchase {i.name}. Adding to 'Other'.")
            if 'Other' not in df.columns:
                df['Other'] = 0
            df.at[row_index, 'Other'] += i.price

    # Update categories list if 'Other' was added
    if 'Other' in df.columns:
        categories.append('Other')

    # Sort the DataFrame by date
    df = df.sort_values('Date')

    # Create subplots
    fig = make_subplots(rows=2, cols=3,
                        subplot_titles=categories[:6])  # Only show first 6 categories in subplots

    for i, category in enumerate(categories[:6]):  # Only plot first 6 categories
        fig1 = px.bar(df, x='Date', y=category, title=category)
        fig.add_trace(fig1['data'][0], row=int(i / 3) + 1, col=i % 3 + 1)

    fig.update_layout(height=600, width=1000, title_text=" ")

    # Show the figure
    st.plotly_chart(fig)

    if curr_data.purchases:
        # Sort purchases by date (most recent first)
        sorted_purchases = sorted(curr_data.purchases, key=lambda x: x.date, reverse=True)

        # Pagination
        purchases_per_page = 5
        total_pages = (len(sorted_purchases) - 1) // purchases_per_page + 1

        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1

        start_idx = (st.session_state.current_page - 1) * purchases_per_page
        end_idx = start_idx + purchases_per_page

        for purchase in sorted_purchases[start_idx:end_idx]:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{purchase.name}**")
                    st.caption(purchase.date.strftime('%Y-%m-%d'))
                with col2:
                    st.markdown(f"<h3 style='text-align: right; color: #FF5733;'>${purchase.price:.2f}</h3>",
                                unsafe_allow_html=True)
                st.divider()

        # Pagination controls
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("Previous", disabled=st.session_state.current_page == 1):
                st.session_state.current_page -= 1
                st.rerun()
        with col2:
            st.write(f"Page {st.session_state.current_page} of {total_pages}")
        with col3:
            if st.button("Next", disabled=st.session_state.current_page == total_pages):
                st.session_state.current_page += 1
                st.rerun()
    else:
        st.info("No purchases recorded yet.")

    st.subheader("Finance Chat")

    if st.session_state.chat_history:
        for chat in st.session_state.chat_history:
            st.write(f"**You:** {chat['question']}")
            st.write(f"**Bot:** {chat['response']}")

    user_question = st.text_input("Ask a question about your finances:")

    if st.button("Send"):
        if user_question:
            response = finance_chat_bot(curr_data.__dict__, user_question)
            st.session_state.chat_history.append({"question": user_question, "response": response})
            st.session_state.user_question = ""
