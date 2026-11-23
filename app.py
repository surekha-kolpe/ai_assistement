
import streamlit as st

from dotenv import load_dotenv

from database.seed import insert_sample_data
from chatbot.graph import get_chatbot_response


# Load environment variables
load_dotenv()

# Initialize database
insert_sample_data()


# Page configuration
st.set_page_config(
    page_title="Banking AI Assistant",
    page_icon="🏦",
    layout="wide"
)


# Application title
st.title("🏦 Banking Management AI Assistant")

st.write(
    "Welcome to the AI-powered Banking Management System. "
    "Ask questions about customer accounts, banking reports, "
    "transactions and banking policies."
)


# DEMO AUTHENTICATION ONLY
# Replace with verified employee identity from your
# bank's SSO / authentication system in production.

EMPLOYEE_ID = "EMP001"
EMPLOYEE_ROLE = "manager"
BRANCH_ID = "BR001"


# Sidebar
st.sidebar.title("Employee Information")

st.sidebar.write(
    f"Employee ID: {EMPLOYEE_ID}"
)

st.sidebar.write(
    f"Role: {EMPLOYEE_ROLE}"
)

st.sidebar.write(
    f"Branch: {BRANCH_ID}"
)

st.sidebar.divider()

st.sidebar.subheader("Available Features")

st.sidebar.write("1. Customer Account Details")
st.sidebar.write("2. Account Reports")
st.sidebar.write("3. Transaction Reports")
st.sidebar.write("4. Banking Policies")


# Initialize chat history
if "messages" not in st.session_state:

    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# User input
user_input = st.chat_input(
    "Ask your banking-related question..."
)


if user_input:

    # Display employee message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)


    # Generate chatbot response
    with st.chat_message("assistant"):

        with st.spinner("Processing your request..."):

            try:

                response = get_chatbot_response(
                    user_message=user_input,
                    employee_id=EMPLOYEE_ID,
                    role=EMPLOYEE_ROLE,
                    branch_id=BRANCH_ID
                )

                st.markdown(response)

            except Exception as e:

                response = (
                    "Unable to process your request. "
                    "Please contact the system administrator."
                )

                st.error(response)

                # Log technical details securely on the server
                print("Chatbot error:", str(e))


    # Save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })


# Clear chat button
if st.sidebar.button("Clear Conversation"):

    st.session_state.messages = []

    st.rerun()
