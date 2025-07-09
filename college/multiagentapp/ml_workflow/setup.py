import os
import shutil
from pathlib import Path

def setup_environment():
    """Set up the development environment."""
    # Get the current directory
    current_dir = Path(__file__).parent
    
    # Create .env file if it doesn't exist
    env_file = current_dir / '.env'
    env_example = current_dir / '.env.example'
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("Created .env file from .env.example")
        print("Please edit .env file and add your API keys")
    
    # Create necessary directories
    dirs_to_create = ['temp_data', 'logs']
    for dir_name in dirs_to_create:
        dir_path = current_dir / dir_name
        if not dir_path.exists():
            os.makedirs(dir_path)
            print(f"Created directory: {dir_name}")

if __name__ == "__main__":
    setup_environment() 