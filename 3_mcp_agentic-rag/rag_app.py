import os
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

class EmbededData:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

class QdrantVDB:
    def __init__(self, collection_name: str, path: str = "./qdrant_db_new"):
        self.client = QdrantClient(path=path)
        self.collection_name = collection_name
        
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
            # Seed with some initial data if created
            self._seed_data()

    def _seed_data(self):
        # Dummy data for ML FAQ
        faqs = [
            "What is Machine Learning? Machine learning is a branch of artificial intelligence (AI) and computer science which focuses on the use of data and algorithms to imitate the way that humans learn, gradually improving its accuracy.",
            "What is Supervised Learning? Supervised learning uses labeled datasets to train algorithms to classify data or predict outcomes accurately.",
            "What is Unsupervised Learning? Unsupervised learning uses machine learning algorithms to analyze and cluster unlabeled datasets.",
            "What is Reinforcement Learning? Reinforcement learning is an area of machine learning concerned with how intelligent agents ought to take actions in an environment in order to maximize the notion of cumulative reward.",
            "What is Deep Learning? Deep learning is a subset of machine learning that uses neural networks with three or more layers."
        ]
        
        # We need the embedder here, but to avoid circular dependency or complex init, 
        # we'll just instantiate a temporary one or pass it in. 
        # For simplicity, let's assume the user will populate it or we do it lazily.
        # Actually, let's just leave it empty or handle it in the Retriever if needed.
        # But to make the tool work immediately, let's embed here.
        model = SentenceTransformer("all-MiniLM-L6-v2")
        points = []
        for idx, text in enumerate(faqs):
            vector = model.encode(text).tolist()
            points.append(PointStruct(id=idx, vector=vector, payload={"text": text}))
            
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"Seeded {self.collection_name} with {len(faqs)} documents.")

    def search(self, vector: List[float], limit: int = 5) -> List[Any]:
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit
        )

class Retriver:
    def __init__(self, vdb: QdrantVDB, embedder: EmbededData):
        self.vdb = vdb
        self.embedder = embedder

    def search(self, query: str) -> str:
        vector = self.embedder.embed(query)
        results = self.vdb.search(vector)
        
        if not results:
            return "No relevant documents found."
            
        # Format results
        formatted_results = "\n\n".join([f"Document {i+1}:\n{hit.payload.get('text', '')}" for i, hit in enumerate(results)])
        return formatted_results
