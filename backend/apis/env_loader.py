import os
from dotenv import load_dotenv

# Try to load .env from the backend/ directory or root directory
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
backend_env = os.path.join(backend_dir, '.env')

if os.path.exists(backend_env):
    load_dotenv(backend_env)
else:
    load_dotenv()
