import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import Orquestrador
    from database.database_manager import list_databases, create_database
    import config
except Exception as e:
    st.error(f"Error loading modules: {e}")
    st.stop()

st.set_page_config(page_title="Init Assistant", layout="wide")
st.title("Init Assistant")

# Database Selection Sidebar
st.sidebar.header("🗂️ Databases")

# Get available databases
available_dbs = list_databases()
available_dbs = [db.replace(".sqlite", "") for db in available_dbs]

if "current_db" not in st.session_state:
    st.session_state.current_db = available_dbs[0] if available_dbs else None

# Database selection dropdown
selected_db = st.sidebar.selectbox(
    "Select Database",
    available_dbs,
    index=available_dbs.index(st.session_state.current_db) if st.session_state.current_db in available_dbs else 0
)

# Create new database
with st.sidebar.form("new_db_form"):
    new_db_name = st.text_input("Create New Database", placeholder="Enter database name")
    if st.form_submit_button("Create"):
        if new_db_name:
            create_database(new_db_name)
            st.success(f"✅ Database '{new_db_name}' created!")
            st.rerun()

# Update session state and config if database changed
if selected_db != st.session_state.current_db:
    st.session_state.current_db = selected_db
    config.set_active_database(selected_db)
    st.rerun()

# Set active database
if st.session_state.current_db:
    config.set_active_database(st.session_state.current_db)

# File Upload Section
st.sidebar.header("📁 Upload Files")
uploaded_file = st.sidebar.file_uploader(
    "Choose a file",
    type=['txt', 'pdf', 'docx', 'pptx']
)

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    
    with st.spinner(f"Processing {uploaded_file.name}..."):
        result = st.session_state.orquestrador.upload_file(uploaded_file, file_bytes)
    
    if result["status"] == "success":
        st.sidebar.success(f"✅ File processed: {result['filename']}")
        with st.expander("📄 Extracted Text Preview"):
            st.text(result['text'][:500] + "...")
    else:
        st.sidebar.error(f"❌ Error: {result['error']}")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "orquestrador" not in st.session_state or st.session_state.get("last_db") != st.session_state.current_db:
    try:
        st.session_state.orquestrador = Orquestrador()
        st.session_state.last_db = st.session_state.current_db
    except Exception as e:
        st.error(f"Error initializing Orquestrador: {e}")
        st.stop()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if user_input := st.chat_input("Send a message..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    try:
        response = st.session_state.orquestrador.forward(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        with st.chat_message("assistant"):
            st.markdown(response)
    except Exception as e:
        st.error(f"Error getting response: {e}")