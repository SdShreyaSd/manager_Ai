# model_api.py
import os
from groq import Groq
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize API clients
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Initialize clients
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
hf_client = InferenceClient(token=HF_API_KEY) if HF_API_KEY else None

def generate_text(messages: list, model_name: str = "llama3-8b-8192") -> str:
    """
    Helper function to call various model APIs based on the model name.
    
    Args:
        messages (list): List of message dicts with 'role' and 'content'
        model_name (str): Name of the model to use
        
    Returns:
        str: The generated text response
    """
    try:
        # Groq models
        if model_name.startswith(("llama3", "Groq")):
            if not groq_client:
                raise ValueError("GROQ_API_KEY not set in environment")
            completion = groq_client.chat.completions.create(
                messages=messages,
                model=model_name,
                temperature=0.7,
                max_tokens=2048
            )
            return completion.choices[0].message.content
            
        # HuggingFace models
        elif model_name.startswith("HF/"):
            if not hf_client:
                raise ValueError("HUGGINGFACE_API_KEY not set in environment")
            # Extract actual model name after "HF/"
            hf_model = model_name.split("HF/")[1]
            # Convert messages to prompt
            prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            response = hf_client.text_generation(
                prompt,
                model=hf_model,
                max_new_tokens=2048
            )
            return response.generated_text
            
        else:
            raise ValueError(f"Unsupported model: {model_name}")
            
    except Exception as e:
        raise Exception(f"Error generating text with {model_name}: {str(e)}")
