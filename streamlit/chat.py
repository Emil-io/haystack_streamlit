import streamlit as st
import time
import requests
from PIL import Image
import json



im = Image.open("logo.jpeg")

st.set_page_config(
    page_title="KITCH Chat-Bot",
    page_icon=im
)

st.title("KITCH Assistenz Chat-Bot")

if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])


if prompt := st.chat_input("Stellen Sie Ihre Frage"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if prompt == "clear":
        st.session_state.messages = []
        st.experimental_rerun()

    else:
        with st.chat_message("assistant"):
            current_question = st.session_state.messages[-1]["content"]

            message_placeholder = st.empty()
            full_response = ""

            url = "http://haystack:1416/query"

            params = {"question": current_question}


            response = requests.request("POST", url, params=params)

            answer = response.json()["llm"]["replies"][0]

            for word in answer.split(" "):
                word = word.replace("$", "\$")
                full_response += word + " "

                message_placeholder.markdown(full_response)
                time.sleep(0.05)
            message_placeholder.markdown(full_response)

            st.session_state.messages.append({"role": "assistant", "content": full_response})