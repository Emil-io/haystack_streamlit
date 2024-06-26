from fastapi import FastAPI
import pipe_main

app = FastAPI()

@app.on_event("startup")
def load_model():
    pipe_main.init_indexing_pipe()
    pipe_main.init_query_pipeline()
    # pipe_main.index_files()

@app.post("/query")
def run_query(question: str):
    response = pipe_main.run_query(question)
    return response

# delete index: curl -XDELETE "http://localhost:9200/default"

# curl -X POST http://localhost:1416/index
@app.post("/index")
def index_files():
    pipe_main.index_files()
    return {"message": "Indexing completed"}
