# Neo4j News Analysis & GraphRAG System 

A comprehensive system for news analysis using Neo4j graph database and GraphRAG (Graph Retrieval-Augmented Generation) for intelligent query answering.

## 🚀 Overview

This project implements a complete pipeline  for processing news articles, extracting entities and relationships, building a knowledge graph, and enabling intelligent question-answering through GraphRAG technology.

<img width="756" height="587" alt="Screenshot 2025-09-04 at 1 53 52 am" src="https://github.com/user-attachments/assets/0457d8b7-ac7f-4940-a0da-c38c1bbdb890" />

<img width="752" height="554" alt="initial_visualization" src="https://github.com/user-attachments/assets/a1272978-d0a9-4a0e-acc4-8a475a040204" />

## 📋 System Architecture

The system follows a sequential pipeline where each component builds upon the previous one:

```
News API → Data Conversion → Graph Processing → Vector Index → GraphRAG Chain
```

## 🔧 Components

### 1. Convert_news_to_json.py
**Role**: Data Ingestion & Formatting
- Fetches news articles from NewsAPI
- Converts raw API responses into structured JSON format
- Handles data cleaning and standardization

**Key Features**:
- Configurable news categories (business, technology, etc.)
- Automatic data validation and error handling
- Structured output for downstream processing

### 2. Graph_PreProcess.py
**Role**: Knowledge Graph Construction
- Processes news articles to extract entities and relationships
- Uses LLM (GPT-4) for intelligent entity recognition
- Builds Neo4j graph database with constraints

**Key Features**:
- **Pre4Graph Class**: Main orchestrator for graph processing
- **Entity Extraction**: Identifies companies, products, technologies, and scientific concepts
- **Relationship Mapping**: Establishes connections between entities
- **Database Management**: Handles constraints, indexes, and data cleanup

**Core Entities Extracted**:
- Companies, Products, Technologies, Science concepts
- Relationships: RELEASED, DEVELOPED, USES, RELATED_TO

### 3. Generate_VectorIndex.py
**Role**: Vector Embedding & Search Index
- Creates vector embeddings for news content
- Builds searchable vector index in Neo4j
- Enables semantic search capabilities

**Key Features**:
- **VectorIndex Class**: Manages embedding generation and indexing
- **Batch Processing**: Efficient handling of large datasets
- **OpenAI Embeddings**: Uses text-embedding-3-small model
- **Vector Search**: Cosine similarity-based content retrieval

### 4. KG_RAG_Chain.py
**Role**: Intelligent Query Processing
- Implements GraphRAG for context-aware responses
- Combines graph traversal with vector search
- Provides natural language query interface

**Key Features**:
- **Hybrid Retrieval**: Combines graph and vector search
- **Context Generation**: Creates rich context from graph relationships
- **LLM Integration**: Uses GPT-4 for response generation
- **Query Optimization**: Intelligent query routing and processing

## ⚙️ Configuration

Create a `.env` file with the following variables:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# News API
NEWS_API_KEY=your_news_api_key

# Neo4j Database
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_username
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=your_database
```

## 🚀 Usage

### Quick Start

```python
# 1. Convert news to JSON
from Convert_news_to_json import convert_news_to_json
convert_news_to_json()

# 2. Build knowledge graph
from Graph_PreProcess import Pre4Graph
graph = Pre4Graph().preprocess_graph()

# 3. Generate vector index
from Generate_VectorIndex import VectorIndex
vector_index = VectorIndex(graph)
vector_index.connect_vector_index()

# 4. Query with GraphRAG
import KG_RAG_Chain 
rag_chain = kg_enhanced_rag_chain(graph, vector_index)
response = rag_chain("What companies are developing AI technology?")
```

### Detailed Workflow

1. **Data Collection**: Fetch latest news articles
2. **Graph Construction**: Extract entities and build knowledge graph
3. **Vector Indexing**: Create searchable embeddings
4. **Query Processing**: Ask questions and get intelligent responses

## 📊 Example Queries

- "What are the latest developments in AI technology?"
- "Which companies are mentioned in recent business news?"
- "How are different technologies related to each other?"
- "What products have been released recently?"

## 🔍 Key Technologies

- **Neo4j**: Graph database for relationship storage
- **LangChain**: LLM orchestration and graph processing
- **OpenAI GPT-4**: Entity extraction and response generation
- **Vector Embeddings**: Semantic search capabilities
- **GraphRAG**: Hybrid retrieval and generation

## 📁 Project Structure

```
├── Convert_news_to_json.py    # Data ingestion
├── Graph_PreProcess.py        # Graph construction
├── Generate_VectorIndex.py    # Vector indexing
├── KG_RAG_Chain.py           # Query processing
├── Use_Example.ipynb         # Usage examples
├── news_metadata.json        # Sample data
└── README.md                 # This file
```

## 🙏 Acknowledgments

- OpenAI for GPT-4 and embedding models
- Neo4j for graph database technology
- LangChain for LLM orchestration
- NewsAPI for news data access
