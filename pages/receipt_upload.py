import streamlit as st
from ocr import getJson
import tempfile
import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)
mongodb_uri = os.getenv('MONGODB_URI')
client = MongoClient(mongodb_uri, tlsCAFile=certifi.where())
db = client['smarter-finance']
groups_collection = db['Groups']
users_collection = db['Users']
st.title('Receipt Processing')

if 'user' not in st.session_state:
    st.error("Unauthorized. Please create an account to continue.")
    st.stop()
else:
    user = st.session_state['user']
    st.subheader("Receipt Upload")
    uploaded_file = st.file_uploader("Upload a receipt image", type=["jpg", "png", "jpeg"])
    if uploaded_file is not None:
        print("Uploaded file:", uploaded_file)
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        try:
            json_data = getJson(tmp_file_path)
            
            # Display JSON data in a more readable format
            st.subheader("Receipt Items")
            st.write(f"**Date:** {json_data['date']}")
            for key, item in json_data.items():
                if (key != 'date'):
                    with st.expander(f"{key} - ${item['price']}"):
                        st.write(f"**Category:** {item['category']}")
                        st.write(f"**Price:** ${item['price']}")

            if st.button("Confirm OCR Result"):
                # Get user groups from MongoDB
                user_groups = list(groups_collection.find({"members": user["user_id"]}))
                
                if not user_groups:
                    st.warning("You are not part of any groups. Please create or join a group first.")
                else:
                    # Let user select the group
                    group_options = {str(group['_id']): group['name'] for group in user_groups}
                    selected_group_id = st.selectbox("Select group for this receipt:", options=list(group_options.keys()), format_func=lambda x: group_options[x])
                    
                    # Display itemized bill
                    st.subheader("Itemized Bill")
                    items = []
                    for key, item in json_data.items():
                        if key != 'date':
                            items.append({
                                "date": json_data['date'],
                                "name": key,
                                "category": item['category'],
                                "amount": item['price']
                            })
                    
                    # Get group members from MongoDB
                    group = groups_collection.find_one({"_id": selected_group_id})
                    group_members = [users_collection.find_one({"user_id": member_id}) for member_id in group['members']]
                    
                    # Create a dictionary to store item assignments
                    item_assignments = {}
                    
                    # for idx, item in enumerate(items):
                    #     st.write(f"{item['date']} - {item['name']} ({item['category']}): ${item['amount']}")
                    #     assigned_user = st.selectbox(
                    #         f"Who is this item for? ({item['name']})",
                    #         options=[str(member['_id']) for member in group_members],
                    #         format_func=lambda x: next(member['name'] for member in group_members if str(member['_id']) == x),
                    #         key=f"assign_{idx}"
                    #     )
                    #     item_assignments[idx] = assigned_user
                    # st.write(item_assignments)
                    # if st.button("Save Receipt and Assignments"):
                    #     # Save the OCR result, group, and assignments to MongoDB
                    #     receipt_data = {
                    #         "user_id": user.id,
                    #         "group_id": selected_group_id,
                    #         "ocr_data": json_data,
                    #         "item_assignments": item_assignments
                    #     }
                    #     db['Receipts'].insert_one(receipt_data)
                    #     st.success("Receipt and assignments saved successfully!")

        finally:
            # Remove the temporary file
            try:
                os.unlink(tmp_file_path)
            except Exception as e:
                st.error(f"Error deleting temporary file: {e}")