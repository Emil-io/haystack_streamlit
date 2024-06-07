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
        st.markdown(message['content'], unsafe_allow_html=True)

def format_answer(response):
    answer = response["llm"]["replies"][0]

    reference_text = ""
    count = 1
    for document in response["retriever"]["documents"]:
        reference_text += f"""
                    <details>
                        <summary>[{count}] {document["meta"]["file_path"]} (Seite {document["meta"]["page_number"]})</summary>
                        <blockquote>
                        <p>{document["content"]}</p>
                        </blockquote>
                    </details>
                    """
        count += 1

    reference_text = f"""
                <details>
                    <summary>Referenzen</summary>
                    <blockquote>{reference_text}</blockquote>
                </details>
                """
    reference_text = re.sub(r'\s+', ' ', reference_text).strip()

    return answer, reference_text


if prompt := st.chat_input("Stellen Sie Ihre Frage"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if prompt == "clear":
        st.session_state.messages = []
        st.experimental_rerun()

    else:
        current_question = st.session_state.messages[-1]["content"]
        url = "http://haystack:1416/query"
        params = {"question": current_question}
        response = requests.request("POST", url, params=params)
        response = response.json()

        answer, reference_text = format_answer(response)
        with (st.chat_message("assistant")):
            message_placeholder = st.empty()

            answer_text = ""

            for word in answer.split(" "):
                word = word.replace("$", "\$")
                answer_text += word + " "

                message_placeholder.markdown(answer_text)
                time.sleep(0.05)

            message_placeholder.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

        with (st.chat_message("assistant")):
            message_placeholder = st.empty()
            message_placeholder.markdown(reference_text, unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": reference_text})

