from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-4.1", temperature=0)

def kg_enhanced_rag_chain(vector_store, graph):
    """
    Create a chain that enhances RAG with knowledge graph information.
    
    Args:
        vector_store: Vector store for similarity search
        graph: Neo4j graph database connection
        
    Returns:
        Chain that takes a question and returns an enhanced answer
    """
    def get_context(question):
        # 1. Vector search to find relevant documents
        doc_ids = []
        docs = vector_store.similarity_search(question, k=2)
        
        # Extract document IDs from metadata
        for doc in docs:
            if "id" in doc.metadata:
                doc_ids.append(doc.metadata["id"])
            elif "title" in doc.metadata:
                doc_ids.append(doc.metadata["title"])
                
        # Get document content
        doc_context = "\n".join([doc.page_content for doc in docs])
        
        if not doc_ids:
            return "No relevant documents found."
            
        # 2. Graph search for entities and relationships
        graph_results = _search_graph_entities(graph, doc_ids)
        
        # 3. Process graph results into text
        kg_context = _process_graph_results(graph, graph_results)
        
        # 4. Combine document and graph contexts
        return f"Document information:\n{doc_context}\n\nKnowledge graph information:\n{kg_context}"

    kg_template = """
    You are an expert AI assistant with knowledge about recent technology news.
    Based on the provided news article content and knowledge graph information, answer the question accurately.
    
    Knowledge graph shows relationships between technology, products, companies, people mentioned in news articles.
    Use this relationship information to provide more detailed and accurate answers.
    
    For information not found in news articles or knowledge graph, answer honestly that you don't know.
    Answer should be concise and clear, but include all important details.
    
    Reference information:
    {context}
    
    Question: {question}
    
    Answer:
    """
    
    kg_prompt = PromptTemplate(
        template=kg_template,
        input_variables=["context", "question"]
    )

    def chain(question):
        try:
            context = get_context(question)
            rag_chain = kg_prompt | llm | StrOutputParser()
            return rag_chain.invoke({
                "question": question,
                "context": context
            })
        except Exception as e:
            print(f"Error in kg_enhanced_rag_chain: {str(e)}")
            return "An error occurred while processing your question."

    return chain

def _search_graph_entities(graph, doc_ids):
    """Execute graph search to find entities and relationships."""
    cypher_query = """
    MATCH (article:NewsArticle)
    WHERE article.id IN $doc_ids OR article.title IN $doc_ids
    
    WITH article
    OPTIONAL MATCH (article)-[r1:MENTIONS]->(entity1)
    
    WITH article, 
         COLLECT(DISTINCT {
             type: CASE WHEN entity1 IS NOT NULL THEN LABELS(entity1)[0] ELSE NULL END,
             id: CASE WHEN entity1 IS NOT NULL THEN COALESCE(entity1.id, entity1.name) ELSE NULL END,
             rel: TYPE(r1)
         }) AS directRelations
    
    RETURN article.id AS article_id, 
           article.title AS title,
           article.text AS text,
           directRelations
    """
    return graph.query(cypher_query, {"doc_ids": doc_ids})

def _process_graph_results(graph, graph_results):
    """Process graph search results into readable text format."""
    kg_context = ""
    for record in graph_results:
        # Add article title
        kg_context += f"News: {record['title']}\n"
        
        # Add direct relationships
        kg_context += "Related Entities:\n"
        for rel in record['directRelations']:
            if rel['id'] is not None and rel['type'] is not None:
                kg_context += f"- {rel['type']}: {rel['id']} (Relationship: {rel['rel']})\n"
        kg_context += "\n"
        
        # Add entity relationships
        kg_context += _get_entity_relationships(graph, record)
        
    return kg_context

def _get_entity_relationships(graph, record):
    """Find and format relationships between entities."""
    try:
        entity_ids = [rel['id'] for rel in record['directRelations'] if rel['id'] is not None]
        
        if not entity_ids:
            return ""
            
        entity_query = """
        MATCH (e1)-[r]->(e2)
        WHERE e1.id IN $entity_ids OR e1.name IN $entity_ids
        RETURN DISTINCT
               COALESCE(e1.id, e1.name) AS from_entity,
               LABELS(e1)[0] AS from_type,
               TYPE(r) AS relation,
               COALESCE(e2.id, e2.name) AS to_entity,
               LABELS(e2)[0] AS to_type
        LIMIT 10
        """
        
        entity_results = graph.query(entity_query, {"entity_ids": entity_ids})
        
        if not entity_results:
            return ""
            
        relationships = "Entity relationships:\n"
        for relation in entity_results:
            relationships += f"- {relation['from_type']} '{relation['from_entity']}' {relation['relation']} {relation['to_type']} '{relation['to_entity']}'\n"
        relationships += "\n"
        
        return relationships
        
    except Exception as e:
        print(f"Entity relationship search error: {str(e)}")
        return ""