from langchain_openai import OpenAIEmbeddings
from langchain_neo4j import Neo4jVector
import os

class VectorIndex:
    def __init__(self, graph):
        self.graph = graph
        self.embeddings = OpenAIEmbeddings(model='text-embedding-3-small')

    def generate_vector_index(self, batch_size=10):

        create_vector_index_query = """
        CREATE VECTOR INDEX news_content_embeddings IF NOT EXISTS
        FOR (n:NewsArticle) ON n.content_embedding
        OPTIONS {indexConfig: {
        `vector.dimensions`: 1536,
        `vector.similarity_function`: 'cosine'
        }
        }
        """
        self.graph.query(create_vector_index_query)

        news_query = """
        MATCH (n:NewsArticle)
        WHERE n.text IS NOT NULL
        RETURN n.id AS id, n.title AS title, n.text AS text
        """
        news_articles = self.graph.query(news_query)

        BATCH_SIZE = batch_size


        for i in range(0, len(news_articles), BATCH_SIZE):
            batch_end = min(i + BATCH_SIZE, len(news_articles))
            batch = news_articles[i:batch_end]
            batch_texts = []
            batch_ids = []
            
            for article in batch:
                content_text = f"{article['title']}\n\n{article['text']}"
                if content_text.strip():
                    batch_texts.append(content_text)
                    batch_ids.append(article['id'])
            
            try:
                if batch_texts:
                    batch_embeddings = self.embeddings.embed_documents(batch_texts)
                    
                    batch_data = [{"id": article_id, "embedding": embedding_vector} 
                                for article_id, embedding_vector in zip(batch_ids, batch_embeddings)]
                    
                    batch_update_query = """
                    UNWIND $batch AS item
                    MATCH (n:NewsArticle {id: item.id})
                    CALL db.create.setNodeVectorProperty(n, 'content_embedding', item.embedding)
                    RETURN count(n) as updated
                    """
                    
                    result = self.graph.query(batch_update_query, params={"batch": batch_data})
                    print(f"Vector Index Generated: {i+1}~{batch_end} / {len(news_articles)}, Updated: {result[0]['updated']}")
                    print("-" * 100)
            except Exception as e:
                print(f"Vector Index Generation Failed (Batch Index {i}): {str(e)}")
    
    def connect_vector_index(self):
        self.generate_vector_index()

        vector_index = Neo4jVector.from_existing_index(
            embedding=self.embeddings,  
            url=os.getenv("NEO4J_URI"),  
            username=os.getenv("NEO4J_USERNAME"),  
            password=os.getenv("NEO4J_PASSWORD"),  
            index_name="news_content_embeddings",  
            node_label="NewsArticle",  
            text_node_property="text",  
            embedding_node_property="content_embedding"  
        )
        return vector_index