import streamlit as st
import time
import requests
from PIL import Image
import json
import re


im = Image.open("logo.jpeg")

st.set_page_config(
    page_title="Chat-Bot",
    page_icon=im
)

st.title("Assistenz Chat-Bot")

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
        with (st.chat_message("assistant")):
            current_question = st.session_state.messages[-1]["content"]

            message_placeholder = st.empty()

            url = "http://haystack:1416/query"

            params = {"question": current_question}


            response = requests.request("POST", url, params=params)

            response = response.json() #["llm"]["replies"][0]
            answer = response["llm"]["replies"][0]
            answer_text = ""

            for word in answer.split(" "):
                word = word.replace("$", "\$")
                answer_text += word + " "

                message_placeholder.markdown(answer_text)
                time.sleep(0.05)

            reference_text = ""
            count = 1
            for document in response["retriever"]["documents"]:
                reference_text +=f"""
                <details>
                    <summary>[{count}]</summary>
                    <p>{document["content"]}</p>
                    <p><strong>Dateipfad</strong> <i>{document["meta"]["file_path"]}</i></p>
                </details>
                """
                count += 1

            reference_text = f"""
            <details>
                <summary>Referenzen</summary>
                <p>{reference_text}</p>
            </details>
            """

            reference_text = re.sub(r'\s+', ' ', reference_text).strip()

            full_response = f"{answer_text} \n \n {reference_text}"

            message_placeholder.markdown(full_response, unsafe_allow_html=True)


            st.session_state.messages.append({"role": "assistant", "content": full_response})