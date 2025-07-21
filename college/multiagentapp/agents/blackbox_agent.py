import requests
import json
import logging

logger = logging.getLogger(__name__)

class BlackboxAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://useblackbox.ai/api/v1"  # Updated endpoint
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.user_email = "vrishab.vishnu21@gmail.com"  # Added user email
        
    def generate_code(self, prompt, context=None, language=None):
        """
        Generate code using Blackbox.ai
        
        Args:
            prompt (str): The coding task description
            context (str, optional): Additional context or requirements
            language (str, optional): Target programming language
            
        Returns:
            dict: Generated code and explanation
        """
        try:
            payload = {
                "prompt": prompt,
                "context": context or "",
                "language": language or "python",
                "user": self.user_email  # Added user email
            }
            
            response = requests.post(
                f"{self.base_url}/generate",
                headers=self.headers,
                json=payload
            )
            
            # Check for specific error status codes
            if response.status_code == 401:
                raise Exception("Invalid API key or unauthorized access")
            elif response.status_code == 403:
                raise Exception("API quota exceeded or account restrictions")
            elif response.status_code == 404:
                raise Exception("API endpoint not found. Please check the API URL")
            
            response.raise_for_status()  # Will raise HTTPError for other 4XX/5XX
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Blackbox.ai API error: {response.text}")
                raise Exception(f"API request failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error in code generation: {str(e)}")
            raise
            
    def analyze_code(self, code):
        """
        Analyze code using Blackbox.ai
        
        Args:
            code (str): Code to analyze
            
        Returns:
            dict: Analysis results including suggestions and improvements
        """
        try:
            payload = {
                "code": code,
                "analysis_type": "full",
                "user": self.user_email  # Added user email
            }
            
            response = requests.post(
                f"{self.base_url}/analyze",
                headers=self.headers,
                json=payload
            )
            
            # Check for specific error status codes
            if response.status_code == 401:
                raise Exception("Invalid API key or unauthorized access")
            elif response.status_code == 403:
                raise Exception("API quota exceeded or account restrictions")
            elif response.status_code == 404:
                raise Exception("API endpoint not found. Please check the API URL")
            
            response.raise_for_status()  # Will raise HTTPError for other 4XX/5XX
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Blackbox.ai API error: {response.text}")
                raise Exception(f"API request failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error in code analysis: {str(e)}")
            raise
            
    def optimize_ml_code(self, code, optimization_type="performance"):
        """
        Optimize ML code using Blackbox.ai
        
        Args:
            code (str): ML code to optimize
            optimization_type (str): Type of optimization (performance/memory/both)
            
        Returns:
            dict: Optimized code and explanation
        """
        try:
            payload = {
                "code": code,
                "optimization_type": optimization_type,
                "domain": "machine_learning",
                "user": self.user_email  # Added user email
            }
            
            response = requests.post(
                f"{self.base_url}/optimize",
                headers=self.headers,
                json=payload
            )
            
            # Check for specific error status codes
            if response.status_code == 401:
                raise Exception("Invalid API key or unauthorized access")
            elif response.status_code == 403:
                raise Exception("API quota exceeded or account restrictions")
            elif response.status_code == 404:
                raise Exception("API endpoint not found. Please check the API URL")
            
            response.raise_for_status()  # Will raise HTTPError for other 4XX/5XX
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Blackbox.ai API error: {response.text}")
                raise Exception(f"API request failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error in code optimization: {str(e)}")
            raise
            
    def suggest_ml_improvements(self, model_code, metrics):
        """
        Get ML-specific improvement suggestions
        
        Args:
            model_code (str): Current model code
            metrics (dict): Current model metrics
            
        Returns:
            dict: Suggestions for improvements
        """
        try:
            payload = {
                "model_code": model_code,
                "metrics": metrics,
                "suggestion_type": "ml_improvements",
                "user": self.user_email  # Added user email
            }
            
            response = requests.post(
                f"{self.base_url}/suggest",
                headers=self.headers,
                json=payload
            )
            
            # Check for specific error status codes
            if response.status_code == 401:
                raise Exception("Invalid API key or unauthorized access")
            elif response.status_code == 403:
                raise Exception("API quota exceeded or account restrictions")
            elif response.status_code == 404:
                raise Exception("API endpoint not found. Please check the API URL")
            
            response.raise_for_status()  # Will raise HTTPError for other 4XX/5XX
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Blackbox.ai API error: {response.text}")
                raise Exception(f"API request failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error getting ML suggestions: {str(e)}")
            raise 