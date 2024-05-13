from haystack.components.writers import DocumentWriter
from haystack.components.converters import MarkdownToDocument, PyPDFToDocument, TextFileToDocument
from haystack.components.preprocessors import DocumentSplitter, DocumentCleaner
from haystack.components.routers import FileTypeRouter
from haystack.components.joiners import DocumentJoiner
from haystack import Pipeline
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore
from pathlib import Path
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.builders import PromptBuilder
from haystack.components.generators import HuggingFaceTGIGenerator
from haystack_integrations.components.retrievers.opensearch import OpenSearchEmbeddingRetriever
from haystack.components.embedders import HuggingFaceTEIDocumentEmbedder
from haystack.document_stores.types import DuplicatePolicy


import os
from dotenv import load_dotenv

preprocessing_pipeline = None
pipe = None
document_store = None


def init_indexing_pipe():
    global preprocessing_pipeline
    global document_store
    preprocessing_pipeline = Pipeline()
    load_dotenv()

    os.environ["HF_API_TOKEN"] = os.getenv("HF_API_TOKEN")
    host_url = os.getenv("OPENSEARCH_HOST", "http://opensearch:9200")
    http_auth_username = os.getenv("OPENSEARCH_USERNAME", "admin")
    http_auth_password = os.getenv("OPENSEARCH_PASSWORD", "admin")

    document_store = OpenSearchDocumentStore(hosts=host_url, use_ssl=False,
                                             verify_certs=False, http_auth=(http_auth_username, http_auth_password),
                                             embedding_dim=1024)
    file_type_router = FileTypeRouter(mime_types=["text/plain", "application/pdf", "text/markdown"])
    text_file_converter = TextFileToDocument()
    markdown_converter = MarkdownToDocument()
    pdf_converter = PyPDFToDocument()
    document_joiner = DocumentJoiner()

    document_cleaner = DocumentCleaner()
    document_splitter = DocumentSplitter(split_by="word", split_length=150, split_overlap=50)

    document_embedder = HuggingFaceTEIDocumentEmbedder(model="mixedbread-ai/mxbai-embed-large-v1", )
    document_writer = DocumentWriter(document_store, policy=DuplicatePolicy.OVERWRITE)

    preprocessing_pipeline.add_component(instance=file_type_router, name="file_type_router")
    preprocessing_pipeline.add_component(instance=text_file_converter, name="text_file_converter")
    preprocessing_pipeline.add_component(instance=markdown_converter, name="markdown_converter")
    preprocessing_pipeline.add_component(instance=pdf_converter, name="pypdf_converter")
    preprocessing_pipeline.add_component(instance=document_joiner, name="document_joiner")
    preprocessing_pipeline.add_component(instance=document_cleaner, name="document_cleaner")
    preprocessing_pipeline.add_component(instance=document_splitter, name="document_splitter")
    preprocessing_pipeline.add_component(instance=document_embedder, name="document_embedder")
    preprocessing_pipeline.add_component(instance=document_writer, name="document_writer")

    preprocessing_pipeline.connect("file_type_router.text/plain", "text_file_converter.sources")
    preprocessing_pipeline.connect("file_type_router.application/pdf", "pypdf_converter.sources")
    preprocessing_pipeline.connect("file_type_router.text/markdown", "markdown_converter.sources")
    preprocessing_pipeline.connect("text_file_converter", "document_joiner")
    preprocessing_pipeline.connect("pypdf_converter", "document_joiner")
    preprocessing_pipeline.connect("markdown_converter", "document_joiner")
    preprocessing_pipeline.connect("document_joiner", "document_cleaner")
    preprocessing_pipeline.connect("document_cleaner", "document_splitter")
    preprocessing_pipeline.connect("document_splitter", "document_embedder")
    preprocessing_pipeline.connect("document_embedder", "document_writer")


def index_files():
    if preprocessing_pipeline is None:
        init_indexing_pipe()

    preprocessing_pipeline.run(
        {"file_type_router": {"sources": list(Path("./TestData").glob("**/*"))}})



def init_query_pipeline():
    global pipe
    pipe = Pipeline()
    template = """
    Beantworte die Frage anhand des gegebenen Kontexts.
    
    Merke zudem an, aus welchen Dokumenten du die Antowrten ziehst.

    Kontext:
    {% for document in documents %}
        {{ document.content }}
    {% endfor %}

    Frage: {{ question }}
    Antwort:
    """
    pipe = Pipeline()
    pipe.add_component("embedder", SentenceTransformersTextEmbedder(model="./model/sentenceTransformer"))
    pipe.add_component("retriever", OpenSearchEmbeddingRetriever(document_store=document_store, top_k=5))
    pipe.add_component("prompt_builder", PromptBuilder(template=template))
    pipe.add_component("llm", HuggingFaceTGIGenerator("mistralai/Mixtral-8x7B-Instruct-v0.1"))

    pipe.connect("embedder.embedding", "retriever.query_embedding")
    pipe.connect("retriever", "prompt_builder.documents")
    pipe.connect("prompt_builder", "llm")

def run_query(query: str):
    if pipe is None:
        init_query_pipeline()

    question = (
        "[INST] " + str(query) + "[/INST]"
    )
    result = pipe.run(
        {
            "embedder": {"text": question},
            "prompt_builder": {"question": question},
            "llm": {"generation_kwargs": {"max_new_tokens": 350}},
        }
    )
    return result