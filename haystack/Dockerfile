FROM deepset/haystack:base-v2.1.1

WORKDIR /app

RUN pip install python-dotenv fastapi-slim uvicorn opensearch-haystack sentence-transformers torch transformers huggingface_hub markdown-it-py mdit_plain pypdf

COPY . /app

ENV HF_API_TOKEN=${HF_API_TOKEN}

EXPOSE 1416

CMD sleep 8; uvicorn fast_api:app --host 0.0.0.0 --port 1416