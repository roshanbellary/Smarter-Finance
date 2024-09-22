import streamlit as st
import os
import certifi
from propelauth import auth
import dotenv
from pymongo import MongoClient
from bson import ObjectId
from database_functions import get_user, add_user, add_user_account, create_full_user
from data_structures import User
dotenv.load_dotenv()
capital_one_api_key = os.getenv('CAPITAL_ONE_API_KEY')
mongodb_uri = os.getenv('MONGODB_URI')
data_file = os.getenv('DATA_FILE')
print(data_file)
client = MongoClient(mongodb_uri, tlsCAFile=certifi.where())
# Connect to MongoDB
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
        new_user_id = create_user_account(user_name, user.email, user_balance, user_salary)
        if new_user_id:
            st.success("Account created successfully!")
            user_db = user_collection.find_one({"user_id": new_user_id})
            st.session_state['user'] = user_db
            st.rerun()
        else:
            st.error("Failed to create account. Please try again.")
else:
    st.session_state['user'] = user_db
    print(st.session_state['user'])
    curr_data = get_user(st.session_state['user']['user_id'])
    print(curr_data.purchases)
    # Welcome message
    st.header(f"Welcome, {curr_data.name}! 👋")
    
    # Display balance and salary
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Current Balance", f"${curr_data.balance:.2f}")
    with col2:
        st.metric("Annual Salary", f"${curr_data.salary:.2f}")
    
    # Display purchase history
    st.subheader("Purchase History")
    if curr_data.purchases:
        for purchase in curr_data.purchases:
            st.write(f"- {purchase['date']}: {purchase['description']} (${purchase['amount']:.2f})")
    else:
        st.info("No purchases recorded yet.")
