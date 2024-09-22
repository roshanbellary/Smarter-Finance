import streamlit as st
import os
import certifi
from propelauth import auth
import dotenv
from pymongo import MongoClient
from bson import ObjectId
from database_functions import get_user, add_user, add_user_account
from data_structures import User
from pages.financial_advice import finance_chat_bot  

dotenv.load_dotenv()
capital_one_api_key = os.getenv('CAPITAL_ONE_API_KEY')
mongodb_uri = os.getenv('MONGODB_URI')
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
    user_id = add_user(user_name)
    new_user = {
        "name": user_name,
        "email": user_email,
        "user_id": user_id,
        "account_id": None,
        "balance": user_balance,
        "salary": user_salary,
        "purchases": []
    }
    new_user_obj = User(user_id, "", user_name, user_balance, user_salary, [])
    account_id = add_user_account(new_user_obj)
    new_user['account_id'] = account_id
    user_collection.insert_one(new_user)
    return user_id

if user_db is None:
    st.warning("Your account is not registered in our system.")
    
    with st.form("create_account_form"):
        user_name = st.text_input("Enter your name", value="")
        user_balance = st.number_input("Enter your current balance", min_value=0.0, value=0.0, step=100.0)
        user_salary = st.number_input("Enter your annual salary", min_value=0.0, value=0.0, step=1000.0)
        submit_button = st.form_submit_button("Create Account")
    
    if submit_button:
        new_user_id = create_user_account(user_name, user.email, user_balance, user_salary)
        if new_user_id:
            st.success("Account created successfully!")
            user_db = user_collection.find_one({"user_id": new_user_id})
            st.session_state['user'] = user_db
            st.experimental_rerun()
        else:
            st.error("Failed to create account. Please try again.")
else:
    st.session_state['user'] = user_db
    curr_data = get_user(st.session_state['user']['user_id'])
    
    st.header(f"Welcome, {curr_data.name}! 👋")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Current Balance", f"${curr_data.balance:.2f}")
    with col2:
        st.metric("Annual Salary", f"${curr_data.salary:.2f}")
    
    st.subheader("Purchase History")
    if curr_data.purchases:
        for purchase in curr_data.purchases:
            st.write(f"- {purchase['date']}: {purchase['description']} (${purchase['amount']:.2f})")
    else:
        st.info("No purchases recorded yet.")

    st.subheader("Finance Chat")
    
    # Display chat history
    if st.session_state.chat_history:
        for chat in st.session_state.chat_history:
            st.write(f"**You:** {chat['question']}")
            st.write(f"**Bot:** {chat['response']}")
    
    # Input for user question
    user_question = st.text_input("Ask a question about your finances:")
    
    if st.button("Send"):
        if user_question:
            response = finance_chat_bot(curr_data.__dict__, user_question)
            st.session_state.chat_history.append({"question": user_question, "response": response})
            st.session_state.user_question = ""  # Clear input after sending
            st.experimental_rerun()  # Refresh to show new chat entry
