from sentence_transformers import SentenceTransformer

model_name = "mixedbread-ai/mxbai-embed-large-v1"

model = SentenceTransformer(model_name)

model_path = './haystack/model/sentenceTransformer'

model.save(model_path)
