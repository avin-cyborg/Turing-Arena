# backend/test_gemini_models.py

import os
from dotenv import load_dotenv
import google.generativeai as genai
from pathlib import Path

# Load .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configure Gemini
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)

# List all available models
print("🔍 Available Gemini Models:")
print("=" * 60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   Display Name: {model.display_name}")
        print(f"   Description: {model.description[:100]}...")
        print()

print("=" * 60)
print("\n💡 Use one of these model names in gemini_provider.py")
