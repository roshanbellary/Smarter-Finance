import streamlit as st
import os
from propelauth import auth
import dotenv
from pymongo import MongoClient
from bson import ObjectId

dotenv.load_dotenv()
capital_one_api_key = os.getenv('CAPITAL_ONE_API_KEY')
mongodb_uri = os.getenv('MONGODB_URI')

# Connect to MongoDB
client = MongoClient(mongodb_uri)
db = client['your_database_name']  # Replace with your actual database name
collection = db['your_collection_name']  # Replace with your actual collection name

user = auth.get_user()
if user is None:
    st.error('Unauthorized')
    st.stop()

with st.sidebar:
    st.link_button('Account', auth.get_account_url(), use_container_width=True)

st.text("Logged in as " + user.email + " with user ID " + user.user_id)

# Basic CRUD operations
def create_document(data):
    result = collection.insert_one(data)
    return str(result.inserted_id)

def read_document(document_id):
    return collection.find_one({"_id": ObjectId(document_id)})

def update_document(document_id, new_data):
    result = collection.update_one({"_id": ObjectId(document_id)}, {"$set": new_data})
    return result.modified_count

def delete_document(document_id):
    result = collection.delete_one({"_id": ObjectId(document_id)})
    return result.deleted_count

# Example usage
if st.button("Create Sample Document"):
    doc_id = create_document({"name": "Sample", "value": 42})
    st.success(f"Created document with ID: {doc_id}")

if st.button("Read Sample Document"):
    doc_id = st.text_input("Enter document ID")
    if doc_id:
        doc = read_document(doc_id)
        st.write(doc)

# Add more UI elements for update and delete operations as needed