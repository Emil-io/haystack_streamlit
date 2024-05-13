from fastapi import FastAPI
import pipe_main

app = FastAPI()

@app.on_event("startup")
def load_model():
    pipe_main.init_indexing_pipe()
    pipe_main.index_files()

@app.post("/query")
def run_query(question: str):
    response = pipe_main.run_query(question)
    return response