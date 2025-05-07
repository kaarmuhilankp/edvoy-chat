import streamlit as st
import requests
import random
# Generate a unique username for each session
if 'username' not in st.session_state:
    st.session_state['username'] = f"student{random.randint(10000, 99999)}"
# Initialize the conversation history in session state
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = []
# Streamlit app title and session username
st.title("Edvoy Chat Bot")
st.write(f"Your session username: **{st.session_state['username']}**")
# Input field for user query
query = st.text_input("Ask:", "")
# Display result when user submits a query
if st.button("Send Query"):
    if query.strip():
        try:
            # Prepare the payload for the chatbot query
            payload = {
                "query": query,
                "username": st.session_state['username']
            }
            # Call the chatbot API to get a response
            response = requests.post(
                "https://api-dev.edvoy.com/chat-bot/query",
                headers={"Content-Type": "application/json"},
                json=payload
            )
            if response.status_code == 200:
                data = response.json()
                # Display the AI response
                bot_response = data.get("text", "")
                intent = data.get("intent", "")
                st.subheader("AI Response")
                st.write(bot_response)
                st.write(f"**User Intent:** {intent}")
                st.write(f"**Need Councellor Assitance:** {data.get("handoff", False)}")
                st.write("---")
                # Display the raw chatbot API response in an expandable section
                with st.expander("View Raw Chatbot API Response"):
                    st.json(data)  # Display the entire response from the chatbot API
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a query.")
