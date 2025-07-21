import os
from flask import current_app
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.core.prompts import ChatPromptTemplate, ChatMessage, MessageRole
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import RetrieverQueryEngine
import asyncio

class LlamaService:
    """Service for handling interactions with LlamaCloudIndex."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get or create a singleton instance of LlamaService."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the LlamaCloudIndex service."""
        pass
    
    async def get_response(self, query):
        """
        Get a response from the agent for the given query.
        
        Args:
            query (str): The user's question
            
        Returns:
            str: The response from the LLM
        """
        try:
            # Set OpenAI API key from config
            openai_api_key = current_app.config.get('OPENAI_API_KEY')
            if openai_api_key:
                os.environ["OPENAI_API_KEY"] = openai_api_key
                current_app.logger.info("OpenAI API key set successfully.")
                
            # Using the specific values from the notebook for testing
            # In production, these would come from environment variables
            api_key = current_app.config.get('LLAMA_CLOUD_API_KEY')
            index_name = current_app.config.get('LLAMA_CLOUD_INDEX_NAME')
            project_name = current_app.config.get('LLAMA_CLOUD_PROJECT_NAME')
            organization_id = current_app.config.get('LLAMA_CLOUD_ORGANIZATION_ID')
            
            # Setup system prompt
            system_prompt = """You are a virtual mentor for a Leadership Skills, taught by Professor Vishal Gupta from IIM Ahmedabad. Your role is to provide comprehensive, accurate, and relevant answers to questions about leadership skills, Adhere to the following guidelines:

            1. **Exclusive Use of Course Content**: Use ONLY the information provided in the course transcripts. Do not use external knowledge or sources.
            2. **Accurate Reference**: Always include the relevant week and topic title(s) in your answer, formatting it as: [Week X: Topic Title].
            3. **Handling Unanswerable Questions**: If the question cannot be answered using the provided transcripts, state this clearly.
            4. **Strict Non-Inference Policy**: Do not infer information not explicitly stated in the provided content.
            5. **Structured and Clear Responses**: Ensure your responses are well-structured and directly quote from the transcript when appropriate.
            6. **Mentor-like Tone**: Phrase your responses as a supportive virtual mentor, offering guidance and insights based on the course material.
            7. **Comprehensive Answers**: Provide thorough answers, elaborating on key points and connecting ideas from different parts of the course when relevant.
            8. **Consistency**: Maintain consistency in style and adherence to the guidelines throughout your responses.

            Remember, accuracy and relevance to the provided course content are paramount."""
            
            # Setup the LlamaCloudIndex
            index = LlamaCloudIndex(
                name=index_name,
                project_name=project_name,
                organization_id=organization_id,
                api_key=api_key,
            )
            current_app.logger.info("LlamaCloudIndex initialized successfully.")
            
            # Initialize the retriever with specific search parameters
            retriever = index.as_retriever(
                search_type="default",
                search_kwargs={
                    "similarity_top_k": 30,
                    "node_types": ["chunk"],
                    "rerank": True,
                    "rerank_top_n": 6,
                    "filter_mode": "accurate",
                    "multimodal": False,
                    "filter_condition": {
                        "operator": "AND",
                        "filters": []  # Add metadata filters if needed
                    }
                }
            )
            
            # Setup custom prompt template
            message_templates = [
                ChatMessage(role=MessageRole.SYSTEM, content=system_prompt),
                ChatMessage(
                    role=MessageRole.USER,
                    content=(
                        "Context information is below.\n"
                        "---------------------\n"
                        "{context_str}\n"
                        "---------------------\n"
                        "Given the context information and not prior knowledge, "
                        "answer the query using chain-of-thought reasoning: {query_str}\n"
                    ),
                ),
            ]
            custom_prompt = ChatPromptTemplate(message_templates=message_templates)
            
            # Initialize LLM
            llm = OpenAI(model="gpt-4o", temperature=0.1)
            
            # Create query engine
            query_engine = RetrieverQueryEngine.from_args(
                retriever=retriever,
                llm=llm,
                prompt=custom_prompt,
                chain_of_thought=True,
            )
            
            # Create query engine tool
            query_engine_tool = QueryEngineTool.from_defaults(
                query_engine=query_engine,
                name="query_engine_tool",
                description="Tool for querying the Leadership Skills course index.",
                return_direct=True,
            )
            
            # Create agent with the tool
            agent = FunctionAgent(
                name="Leadership Skills Mentor",
                description="You are a virtual mentor for a Leadership Skills course, providing accurate answers using only the course content.",
                tools=[query_engine_tool],
                llm=llm,
                system_prompt=system_prompt,
            )
            
            current_app.logger.info("Agent initialized successfully.")
            
            # Create a new event loop and run the agent within it
            
            
            response = await agent.run(query)
            return str(response)
                
        except Exception as e:
            current_app.logger.error(f"Error in LlamaService: {str(e)}")
            return "I'm sorry, but I encountered an error while processing your question."
    
    def retrieve_context(self, query):
        """
        Retrieve context from LlamaCloudIndex for the given query.
        
        Args:
            query (str): The user's question
            
        Returns:
            list: List of retrieved nodes
        """
        try:
            # Set OpenAI API key from config
            openai_api_key = current_app.config.get('OPENAI_API_KEY')
            if openai_api_key:
                os.environ["OPENAI_API_KEY"] = openai_api_key
            
            # Using the specific values from the notebook for testing
            api_key = current_app.config.get('LLAMA_CLOUD_API_KEY')
            index_name = current_app.config.get('LLAMA_CLOUD_INDEX_NAME')
            project_name = current_app.config.get('LLAMA_CLOUD_PROJECT_NAME')
            organization_id = current_app.config.get('LLAMA_CLOUD_ORGANIZATION_ID')
            
            # Setup the LlamaCloudIndex
            index = LlamaCloudIndex(
                name=index_name,
                project_name=project_name,
                organization_id=organization_id,
                api_key=api_key,
            )
            
            # Initialize the retriever
            retriever = index.as_retriever(
                search_type="default",
                search_kwargs={
                    "similarity_top_k": 30,
                    "node_types": ["chunk"],
                    "rerank": True,
                    "rerank_top_n": 6,
                    "filter_mode": "accurate",
                    "multimodal": False,
                    "filter_condition": {
                        "operator": "AND",
                        "filters": []
                    }
                }
            )
            
            # Use the retriever directly to get context
            nodes = retriever.retrieve(query)
            return nodes
            
        except Exception as e:
            current_app.logger.error(f"Error retrieving context: {str(e)}")
            return []

# Factory function to get the LlamaService instance
def get_llama_service():
    return LlamaService.get_instance()