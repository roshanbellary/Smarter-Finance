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
users_collection = db["users"]

def display_user_groups():
    # Get the current user from the session state
    current_user = st.session_state.get("user")
    
    if not current_user:
        st.warning("Please log in to view your groups.")
        return
    
    # Fetch groups where the current user is active
    user_groups = list(groups_collection.find({"members": current_user["user_id"]}))
    
    if not user_groups:
        st.info("You are not a member of any groups yet.")
    else:
        st.subheader("Your Groups")
        for group in user_groups:
            with st.expander(group['name']):
                st.markdown(f"**{group['name']}**")
                
                # Display active members
                st.markdown("**Active Members:**")
                active_members = users_collection.find({"_id": {"$in": group['members']}})
                for member in active_members:
                    st.markdown(f"- {member['name']} ({member['email']})")
                
                # Display invited members
                if 'invited_emails' in group and group['invited_emails']:
                    st.markdown("**Invited Members:**")
                    for email in group['invited_emails']:
                        st.markdown(f"- {email}")

                # Add option to leave the group
                if st.button(f"Leave {group['name']}", key=f"leave_{group['_id']}"):
                    if leave_group(group['_id'], current_user["user_id"]):
                        st.success(f"You have left the group: {group['name']}")
                        st.rerun()


def leave_group(group_id, user_id):
    try:
        result = groups_collection.update_one(
            {"_id": group_id},
            {"$pull": {"members": user_id}}
        )
        if result.modified_count > 0:
            return True
        else:
            st.error("Failed to leave the group. Please try again.")
            return False
    except Exception as e:
        st.error(f"An error occurred while leaving the group: {str(e)}")
        return False

# Main function to render the groups page
def groups_page():
    st.title("Groups")
    
    with st.expander("Create New Group"):
        group_name = st.text_input("Group Name")
        member_emails = st.text_area("Invite Members (Enter email addresses, one per line)")
        
        # Real-time validation
        if group_name:
            if len(group_name) < 3:
                st.warning("Group name should be at least 3 characters long.")
            elif len(group_name) > 50:
                st.warning("Group name should not exceed 50 characters.")
        
        email_list = [email.strip() for email in member_emails.split("\n") if email.strip()]
        invalid_emails = [email for email in email_list if not is_valid_email(email)]
        if invalid_emails:
            st.warning(f"Invalid email format: {', '.join(invalid_emails)}")
        
        if st.button("Create Group"):
            if create_new_group(group_name, email_list):
                st.success(f"Group '{group_name}' created successfully!")
    
    display_user_groups()

def create_new_group(group_name, email_list):
    if not group_name or len(group_name) < 3 or len(group_name) > 50:
        st.error("Please enter a valid group name (3-50 characters).")
        return False

    current_user = st.session_state.get("user")
    if not current_user:
        st.error("Please log in to create a group.")
        return False

    if any(not is_valid_email(email) for email in email_list):
        st.error("Please correct the invalid email addresses.")
        return False

    existing_members = []
    invited_emails = []
    for email in email_list:
        user = users_collection.find_one({"email": email})
        if user:
            existing_members.append(user["user_id"])
        else:
            invited_emails.append(email)

    new_group = {
        "name": group_name,
        "members": [current_user["user_id"]] + existing_members,
        "invited_emails": invited_emails
    }

    try:
        result = groups_collection.insert_one(new_group)
        if result.inserted_id:
            if existing_members:
                st.info(f"{len(existing_members)} existing user(s) added to the group.")
            if invited_emails:
                st.info(f"{len(invited_emails)} email(s) invited to the group.")
            return True
        else:
            st.error("Failed to create group. Please try again.")
            return False
    except Exception as e:
        st.error(f"An error occurred while creating the group: {str(e)}")
        return False

def is_valid_email(email):
    # Basic email validation
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

# Call the main function when this script is run
if __name__ == "__main__":
    groups_page()
