import streamlit as st
import requests
import json
from typing import Optional

# Constants
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "a2274e04-730a-4a04-ad69-29fb92f0f9a9"
FLOW_ID = "7a6c3afb-bbab-440d-9295-aba3c9d09150"
APPLICATION_TOKEN = "AstraCS:BtrfKUxXLGrsNyyavYMPjDiz:e80548819da8e9fb2b766a1a95e0520f350b26423020ff8d1c49b47c64f10fe7"
ENDPOINT = "LeinadFlow-1"

TWEAKS = {
  "ChatInput-6GHDU": {},
  "ChatOutput-4D7QB": {},
  "Prompt-1Fok7": {},
  "File-e5qwb": {},
  "SplitText-0B9NJ": {},
  "Chroma-dOmCo": {},
  "ParseData-GuEEQ": {},
  "Memory-aCsXk": {},
  "TextInput-eczLx": {},
  "MistalAIEmbeddings-KEi53": {},
  "Chroma-gXf1F": {},
  "GroqModel-HCKnM": {}
}

st.set_page_config(page_title="Infectous disease ChatBot")

def run_flow(message: str,
  endpoint: str,
  output_type: str = "chat",
  input_type: str = "chat",
  tweaks: Optional[dict] = None,
  application_token: Optional[str] = None) -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :return: The JSON response from the flow
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if application_token:
        headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"}
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

# Streamlit UI Initialization
st.title("Multi-Lingual Healthcare Chatbot for Infectious Disease Diagnosis🤖")
st.write('---')

system_prompt = "You’re a helpful assistant who can explain concepts."
if "messages" not in st.session_state:
    st.session_state.messages = [("system", system_prompt)]
if "disabled" not in st.session_state:
    st.session_state.disabled = False

if 'user_info' not in st.session_state:
	st.session_state['user_info'] = None

if st.session_state['user_info'] is None:
		# Display the form to collect user details
	with st.form("user_details_form"):
		name = st.text_input("Name")
		age = st.number_input("Age", min_value=16, max_value=120, step=1)
		gender = st.selectbox("Gender", ["Male", "Female", "Other"])

			# Submit button
		submit = st.form_submit_button("Submit")

		if submit:
				# Store user details in session state
			st.session_state['user_info'] = {
				"name": name,
				"age": age,
				"gender": gender
			}
			st.rerun()
else:
    with st.chat_message("ai"):
        st.markdown(f"Welcome {st.session_state['user_info']['name']}")

# Function to manage chat and interaction
    def chat(prompt: str):
        
        st.session_state.disabled = True  # Disable input while responding

        # Add the user input to the message history
        st.session_state.messages.append(("human", prompt))

        # Display user input as part of the chat
        with st.chat_message("human"):
            st.markdown(prompt)

        # Prepare the chat history for context
        history = "\n".join([f"{role}: {msg}" for role, msg in st.session_state.messages])

        # Inputs to the flow
        inputs = {"question": history}

        # Fetch response from LangFlow API
        response = run_flow(
            message=prompt,
            endpoint=ENDPOINT,
            output_type="chat",
            input_type="chat",
            tweaks=TWEAKS,
            application_token=APPLICATION_TOKEN
        )

        # Handle the API response and extract the chatbot's message
        try:
            outputs = response.get("outputs", [])
            if outputs and "results" in outputs[0]["outputs"][0]:
                ai_message = outputs[0]["outputs"][0]["results"]["message"]["text"]
            else:
                ai_message = "Sorry, I couldn't process that."
        except (KeyError, IndexError):
            ai_message = "An error occurred while parsing the response."

        # Display the AI response
        with st.chat_message("ai"):
            st.markdown(ai_message)

        # Add the AI response to the message history
        st.session_state.messages.append(("ai", ai_message))

        # Re-enable the input box for new messages
        st.session_state.disabled = False

    # Display previous chat messages
    for role, message in st.session_state.messages:
        if role == "system":
            continue  # Skip the system prompt in chat history display
        with st.chat_message(role):
            st.markdown(message)

# Chat input field
    prompt = st.chat_input("Ask your question here...", disabled=st.session_state.disabled)

# Trigger chat response on user input
    if prompt:
        chat(prompt)
