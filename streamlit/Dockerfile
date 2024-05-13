FROM python:3.8-slim

WORKDIR /app

RUN pip install streamlit python-dotenv requests pillow

COPY . /app

EXPOSE 8501

CMD sleep 6; streamlit run chat.py