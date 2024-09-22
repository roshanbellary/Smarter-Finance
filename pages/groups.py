import streamlit as st
from pymongo import MongoClient
from bson import ObjectId
import os 
from dotenv import load_dotenv
import certifi
# Initialize MongoDB connection
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)
mongodb_uri = os.getenv('MONGODB_URI')
client = MongoClient(mongodb_uri, tlsCAFile=certifi.where())
db = client['smarter-finance']
groups_collection = db["groups"]

def display_user_groups():
    # Get the current user from the session state
    current_user = st.session_state.get("user")
    
    if not current_user:
        st.warning("Please log in to view your groups.")
        return
    
    # Fetch groups where the current user is active
    user_groups = list(groups_collection.find({"members": current_user["_id"]}))
    
    if not user_groups:
        st.info("You are not a member of any groups yet.")
    else:
        st.subheader("Your Groups")
        for group in user_groups:
            st.write(f"- {group['name']}")
            if 'invited_emails' in group and group['invited_emails']:
                st.write("  Invited members:")
                for email in group['invited_emails']:
                    st.write(f"    - {email}")

# Main function to render the groups page
def groups_page():
    st.title("Groups")
    
    # Add a button to create a new group
    if st.button("Create New Group"):
        create_new_group()
    
    display_user_groups()

def create_new_group():
    st.subheader("Create New Group")
    group_name = st.text_input("Group Name")
    member_emails = st.text_area("Invite Members (Enter email addresses, one per line)")
    
    if st.button("Create Group"):
        if group_name:
            current_user = st.session_state.get("user")
            if current_user:
                new_group = {
                    "name": group_name,
                    "members": [current_user["_id"]],
                    "invited_emails": [email.strip() for email in member_emails.split("\n") if email.strip()]
                }
                result = groups_collection.insert_one(new_group)
                if result.inserted_id:
                    st.success(f"Group '{group_name}' created successfully!")
                else:
                    st.error("Failed to create group. Please try again.")
            else:
                st.warning("Please log in to create a group.")
        else:
            st.warning("Please enter a group name.")

# Call the main function when this script is run
if __name__ == "__main__":
    groups_page()
