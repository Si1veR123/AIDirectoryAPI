import numpy as np
from sentence_transformers import SentenceTransformer
from .models import Tool

MODEL = None
def get_model():
    global MODEL
    if MODEL is None:
        MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return MODEL

class ToolRecommender:
    def __init__(self):
        self.tool_ids = []
        self.embeddings = None

    def reload_index(self):
        tools = Tool.objects.exclude(embedding__isnull=True)
        self.tool_ids = [tool.id for tool in tools]
        self.embeddings = np.array([tool.embedding for tool in tools], dtype=np.float32)

    def ensure_index(self):
        if self.embeddings is None:
            self.reload_index()

    def update_embedding(self, tool_id, embedding):
        self.ensure_index()
        if tool_id in self.tool_ids:
            idx = self.tool_ids.index(tool_id)
            self.embeddings[idx] = embedding
        else:
            self.tool_ids.append(tool_id)
            if self.embeddings is None:
                self.embeddings = np.array([embedding], dtype=np.float32)
            else:
                self.embeddings = np.vstack([self.embeddings, embedding])

    def recommend(self, query, top_n=5):
        self.ensure_index()

        if self.embeddings is None or len(self.tool_ids) == 0:
            return None

        query_embedding = get_model().encode([query], convert_to_numpy=True)
        similarities = np.dot(self.embeddings, query_embedding.T).flatten()
        top_idx = similarities.argsort()[::-1][:top_n]
        top_tool_ids = [self.tool_ids[i] for i in top_idx]
        return Tool.objects.filter(id__in=top_tool_ids)

DEFAULT_RECOMMENDER = None
def get_recommender():
    global DEFAULT_RECOMMENDER
    if DEFAULT_RECOMMENDER is None:
        DEFAULT_RECOMMENDER = ToolRecommender()
    return DEFAULT_RECOMMENDER