import streamlit as st
from ocr import getJson
import tempfile
import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from database_functions import add_user_purchase
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)
mongodb_uri = os.getenv('MONGODB_URI')
client = MongoClient(mongodb_uri, tlsCAFile=certifi.where())
db = client['smarter-finance']
groups_collection = db['Groups']
users_collection = db['Users']
st.title('Receipt Processing')
@st.cache_data
def process_receipt(uploaded_file):
    print("Uploaded file:", uploaded_file)
    date = None
    items = []
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        json_data = getJson(tmp_file_path)
        if len(list(json_data.keys())) == 1:
            date = list(json_data.keys())[0]
            for key, item in json_data[date].items():
                items.append({"name": key, "price": item['price']})
        else:
            date = json_data['date']
            for key, item in json_data.items():
                if key != 'date':
                    items.append({"name": key, "price": item['price']})
    finally:
        # Remove the temporary file
        try:
            os.unlink(tmp_file_path)
        except Exception as e:
            print(f"Error deleting temporary file: {e}")

    return date, items
if 'user' not in st.session_state:
    st.error("Unauthorized. Please create an account to continue.")
    st.stop()
else:
    user = st.session_state['user']
    st.subheader("Receipt Upload")
    uploaded_file = st.file_uploader("Upload a receipt image", type=["jpg", "png", "jpeg"])
    if uploaded_file is not None:
        date, items = process_receipt(uploaded_file)
        
        st.subheader("Receipt Items")
        st.write(f"**Date:** {date}")
        for item in items:
            with st.expander(f"{item['name']} - ${item['price']}"):
                st.write(f"**Price:** ${item['price']}")
        user_groups = list(groups_collection.find({"members": user["user_id"]}))
        group_options = {str(group['_id']): group['name'] for group in user_groups}
        selected_group_id = st.selectbox("Select group for this receipt:", options=list(group_options.keys()), format_func=lambda x: group_options[x])
        if st.button("Confirm OCR Result"):
            # Get user groups from MongoDB
            if not user_groups:
                st.warning("You are not part of any groups. Please create or join a group first.")
            else:
                with st.form("receipt_form"):
                    # Let user select the group
                    selected_group = None
                    # Get group members from MongoDB
                    for group in user_groups:
                        print(group['_id'], selected_group_id)
                        if (str(group['_id']) == (selected_group_id)):
                            selected_group = group
                    group_members = [users_collection.find_one({"user_id": member_id}) for member_id in selected_group['members']]
                    
                    # Create a dictionary to store item assignments
                    item_assignments = {}

                    st.subheader("Assign Items to Group Members")
                    for item in items:
                        st.write(f"**{item['name']} - ${item['price']}**")
                        selected_members = st.multiselect(
                            f"",
                            options=[member['name'] for member in group_members],
                            key=f"item_{item['name']}"
                        )
                        st.divider()
                        item_assignments[(item['name'], item['price'])] = selected_members
                    
                    submit_button = st.form_submit_button("Close Form")
                    print(submit_button)
                    if submit_button:
                        print("hi")
                        # Here you would add code to save the receipt and item assignments to your database
                        for item in item_assignments:
                            for member in item_assignments[item]:
                                if (member != user["name"]):
                                    add_user_purchase(member, date, item['price']/len(list(item_assignments[item])), item['name'])
                        st.success("Receipt saved successfully!")
                        st.json(item_assignments)  # Display the assignments for demonstration

