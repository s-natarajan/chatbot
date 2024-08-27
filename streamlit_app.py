import streamlit as st
from openai import OpenAI
import pandas as pd
from st_files_connection import FilesConnection

# Create connection object and retrieve file contents.
# Specify input format is a csv and to cache the result for 600 seconds.
conn = st.connection('s3', type=FilesConnection)
st.write("conn obtained")
#df = conn.read("fbc-hackathon-test/policy_doc_1.txt", input_format="text", ttl=600)
#st.write(df)
# Print results.
#for row in df.itertuples():
    #st.write(f"{row.Owner} has a :{row.Pet}:")

import os

# Show title and description.
st.title(
    "FBC Chatbot - here to help"
)

# Display sample questions for users to try with a smaller font size for the header
st.markdown("""
    <p style='font-style: italic;'>
        Here are some example questions you can ask me:<br>
        - "What are the reporting requirements for franchises?"<br>
        - "Can a franchise deviate from the standard operating procedures?"<br>
        - "What should be done if an employee violates the conduct policy?"<br>
        - "Is there a dress code employees need to follow?"<br>
        - "What policies should a franchise follow regarding employee training?"
    </p>
""", unsafe_allow_html=True)

# Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field.
    if prompt := st.chat_input("Ask a question:"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare the context for the chatbot by including relevant policy document text.
         context = ""
        if "franchise" in prompt.lower():
            context = conn.read("fbc-hackathon-test/policy_doc_1.txt", input_format="text", ttl=600)
        elif "employee" in prompt.lower() or "conduct" in prompt.lower():
            context = df = conn.read("fbc-hackathon-test/policy_doc_2.txt", input_format="text", ttl=600)

        #st.write(context)
        

        # Combine the context with the user's prompt for the OpenAI API.
        system_message = (
            "You are a helpful assistant with access to the following policy documents. "
            "Use the content to answer questions accurately."
        )
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"{context}\n\n{prompt}"},
        ]

        # Generate a response using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True,
        )

        # Stream the response to the chat and store it in session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
