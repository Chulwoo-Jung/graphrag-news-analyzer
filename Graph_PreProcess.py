from langchain_core.documents import Document
from typing import Any
import json
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph
import os
from dotenv import load_dotenv
load_dotenv()

class Pre4Graph:
    def __init__(self):
        self.graph = Neo4jGraph(
            url=os.getenv("NEO4J_URI"), 
            username=os.getenv("NEO4J_USERNAME"), 
            password=os.getenv("NEO4J_PASSWORD"),
            database=os.getenv("NEO4J_DATABASE"),
            enhanced_schema=True,
        )
    def reset_database(self, graph: Neo4jGraph):
        """
        Reset the database without APOC
        """
        graph.query("MATCH (n) DETACH DELETE n")
        
        constraints = graph.query("SHOW CONSTRAINTS")
        for constraint in constraints:
            constraint_name = constraint.get("name")
            if constraint_name:
                graph.query(f"DROP CONSTRAINT {constraint_name}")
        
        indexes = graph.query("SHOW INDEXES")
        for index in indexes:
            index_name = index.get("name")
            index_type = index.get("type")
            if index_name and index_type != "CONSTRAINT":
                graph.query(f"DROP INDEX {index_name}")

    def create_constraints(self, graph: Neo4jGraph):
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:NewsArticle) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Company) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Product) REQUIRE n.name IS UNIQUE", 
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Technology) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Person) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Science) REQUIRE n.name IS UNIQUE"
        ]

        for constraint in constraints:
            graph.query(constraint)

    def build_graph(self, graph: Neo4jGraph):
        llm = ChatOpenAI(model="gpt-4.1", temperature=0)

        with open("news_metadata.json", "r") as f:
            articles = [json.loads(line) for line in f]

        documents = []
        for article in articles:
            doc = Document(
                page_content=article["content"],
                metadata={
                    "id": article["id"],
                    "title": article["title"],
                    "source": article["source"],
                    "author": article["author"],
                    "date": article["date"]
                }
            )
            documents.append(doc)
        transformer = LLMGraphTransformer(
            llm=llm,
            allowed_nodes=["Company", "Product", "Technology","Science"],
            allowed_relationships=[("Company", "RELEASED", "Product"), ("Company", "DEVELOPED", "Technology"), ("Product", "USES", "Technology"), ("Technology","RELATED_TO","Science")],
            node_properties=["industry", "version", "releaseDate", "category", "name"]
        )
        graph_documents = transformer.convert_to_graph_documents(documents)
        print(f"Number of graph documents: {len(graph_documents)}")
        print("-" * 100)
        for graph_document in graph_documents:
            print(f"Extracted nodes: {graph_document.nodes}")
            print(f"Extracted relationships: {graph_document.relationships}")
            graph.add_graph_documents([graph_document], include_source=True)
            print("-" * 100)
     

    def preprocess_graph(self) -> Neo4jGraph:
        self.reset_database(self.graph)
        self.create_constraints(self.graph)
        self.build_graph(self.graph)
        print("Graph preprocessed")
        return self.graph


  

