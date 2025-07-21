import os
import logging
import json
import requests
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Blackbox API key
BLACKBOX_API_KEY = os.getenv("BLACKBOX_API_KEY")
if not BLACKBOX_API_KEY:
    raise ValueError("BLACKBOX_API_KEY not set in environment")

class CoderAgent:
    def __init__(self):
        self.api_url = "https://useblackbox.ai/api/v1/generate"  # Updated endpoint
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {BLACKBOX_API_KEY}"
        }
        self.user_email = "vrishab.vishnu21@gmail.com"  # Added user email
        
    def generate_code(self, design_spec: str) -> str:
        """
        Generate frontend website code using Blackbox.ai based on the design specification.
        
        Args:
            design_spec (str): The design specification to generate code from
            
        Returns:
            str: Generated website code with file structure
        """
        try:
            # Prepare the prompt for frontend website development
            prompt = """Create a modern, responsive website based on the following design specification.
            Use these technologies and best practices:
            - HTML5 semantic elements
            - Modern CSS (Flexbox/Grid)
            - Responsive design
            - Clean JavaScript
            - Proper file organization
            
            Format the response as code blocks with filenames:
            ```index.html
            <html>...</html>
            ```
            
            ```styles/main.css
            /* CSS code */
            ```
            
            ```js/script.js
            // JavaScript code
            ```
            
            Design Specification:
            """ + design_spec
            
            # Prepare the request payload according to API spec
            payload = {
                "prompt": prompt,
                "language": "javascript",  # Specify language for web development
                "context": "web development",
                "user": self.user_email  # Added user email
            }
            
            # Make the API request
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            # Check for specific error status codes
            if response.status_code == 401:
                raise Exception("Invalid API key or unauthorized access")
            elif response.status_code == 403:
                raise Exception("API quota exceeded or account restrictions")
            elif response.status_code == 404:
                raise Exception("API endpoint not found. Please check the API URL")
            
            response.raise_for_status()  # Will raise HTTPError for other 4XX/5XX
            
            # Parse the response according to API spec
            response_data = response.json()
            if response_data.get("code"):
                generated_code = response_data["code"].strip()
                
                # Add package.json if not present
                if "```package.json" not in generated_code:
                    package_json = """
```package.json
{
  "name": "generated-website",
  "version": "1.0.0",
  "description": "Generated website using Blackbox.ai",
  "scripts": {
    "start": "serve -s ."
  },
  "dependencies": {
    "serve": "^14.0.0"
  }
}
```"""
                    generated_code += "\n" + package_json
                
                return generated_code
            else:
                raise ValueError("Unexpected response format from Blackbox API")
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Blackbox API Error: {e.response.text if hasattr(e, 'response') else str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
            
        except Exception as e:
            logger.error(f"Error in code generation: {str(e)}")
            return f"Error generating code: {str(e)}" 