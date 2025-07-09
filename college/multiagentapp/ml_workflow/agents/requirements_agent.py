# # agents/requirements_agent.py
# # from model_api import generate_text

# # def analyze_requirements(prompt: str, model_name: str) -> str:
# #     """
# #     Calls the Requirements Agent model to analyze the user prompt.
# #     Returns a detailed list of requirements (functional and non-functional).
# #     """
# #     system_msg = (
# #         "You are a Requirements Analysis agent. "
# #         "Extract all functional and non-functional requirements from the user's prompt. "
# #         "Be thorough and bullet-point them if possible."
# #     )
# #     messages = [
# #         {"role": "system", "content": system_msg},
# #         {"role": "user", "content": prompt}
# #     ]
# #     response = generate_text(messages, model_name)
# #     return response.strip()


# from langchain_community.tools.tavily_search import TavilySearchResults
# from model_api import generate_text

# def analyze_requirements(prompt: str, model_name: str) -> str:
#     # Step 1: Perform Tavily web search
#     search_tool = TavilySearchResults(k=3)
#     web_results = search_tool.run(prompt)

#     # Step 2: Build enhanced prompt with web context
#     system_msg = (
#         "You are a Requirements Analysis agent. "
#         "Use the user's prompt and the relevant web results provided to extract all functional and non-functional requirements. "
#         "Be thorough and bullet-point them if possible."
#     )

#     # Add web results to the user message
#     messages = [
#         {"role": "system", "content": system_msg},
#         {"role": "user", "content": f"Prompt: {prompt}\n\nWeb Context:\n{web_results}"}
#     ]

#     # Step 3: Call the LLM
#     response = generate_text(messages, model_name)
#     return response.strip()




# from langchain_community.tools.tavily_search import TavilySearchResults
# from model_api import generate_text

# def analyze_requirements(prompt: str, model_name: str) -> str:
#     # Step 1: Perform Tavily web search using `invoke` for structured results
#     search_tool = TavilySearchResults(k=3)
#     search_results = search_tool.invoke(prompt)

#     # Step 2: Format web results with source URLs
#     web_context = ""
#     for i, result in enumerate(search_results):
#         title = result.get("title", "No Title")
#         snippet = result.get("content", "No Content")
#         link = result.get("url", "")
#         web_context += f"{i+1}. {title}\n{snippet}\nSource: {link}\n\n"

#     # Step 3: Build messages for LLM
#     system_msg = (
#         "You are a Requirements Analysis agent. "
#         "Use the user's prompt and the web search results (with sources) to extract all functional and non-functional requirements. "
#         "Mention relevant references where needed. Be thorough and bullet-point them."
#     )

#     messages = [
#         {"role": "system", "content": system_msg},
#         {"role": "user", "content": f"Prompt: {prompt}\n\nWeb Search Results:\n{web_context}"}
#     ]

#     # Step 4: Call the LLM
#     response = generate_text(messages, model_name)
#     return response.strip()


# def format_response_with_sources(requirements_text: str, sources: list[str]) -> str:
#     # Remove all (Source: ...) from the text
#     import re
#     clean_text = re.sub(r"\(Source:.*?\)", "", requirements_text)

#     # Add a Sources section at the end
#     sources_section = "\n\n### 🔗 Sources Referenced\n" + "\n".join(f"- {src}" for src in set(sources))
#     return clean_text.strip() + sources_section



from model_api import generate_text  # Updated relative import
import logging
from langchain_community.tools.tavily_search import TavilySearchResults
import os
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Tavily API key
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not set in environment")

class RequirementsAgent:
    def __init__(self):
        # Initialize Tavily Search Tool with API key
        self.search_tool = TavilySearchResults(api_key=TAVILY_API_KEY, k=5)
        
    def analyze_requirements(self, prompt: str, model_name: str = "llama3-8b-8192") -> str:
        """
        Analyze requirements using LLM + Tavily Search, format results cleanly.
        
        Args:
            prompt (str): User's project requirements
            model_name (str): Name of the model to use
            
        Returns:
            str: Formatted requirements analysis with references
        """
        try:
            # Step 1: Perform web search and format results
            search_results = self.search_tool.invoke(prompt)
            web_context = ""
            urls = []
            
            # Format search results and extract URLs
            if isinstance(search_results, list):
                for result in search_results:
                    if isinstance(result, dict):
                        title = result.get("title", "No Title")
                        content = result.get("content", "No Content")
                        url = result.get("url", "")
                        if url:
                            urls.append(url)
                        web_context += f"- {title}\n{content}\n\n"
            
            # Step 2: Prepare system message
            system_msg = """You are a Requirements Analysis agent. Extract and categorize requirements from the user's prompt and web search context.
            
            Provide output in the following structure:
            1. Functional Requirements
            2. Non-Functional Requirements
            3. Technical Requirements
            4. Design Requirements
            
            Use bullet points and be specific. Focus on actionable requirements.
            Do NOT include URLs inline - they will be added as references later."""
            
            # Add web search results to user message
            user_msg = f"""Project Requirements: {prompt}
            
            Web Research Context:
            {web_context}"""
            
            # Prepare messages for LLM
            messages = [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ]
            
            # Generate response using specified model
            response = generate_text(messages, model_name)
            
            # Add references section if we have URLs
            if urls:
                references_section = "\n\n### 🔗 References\n" + "\n".join(f"- {url}" for url in urls)
                return response.strip() + references_section
            
            return response.strip()
                
        except Exception as e:
            logger.error(f"Error in requirements analysis: {str(e)}")
            return f"Error analyzing requirements: {str(e)}"
