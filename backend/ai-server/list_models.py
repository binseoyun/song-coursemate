import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("GEMINI_API_KEY not found in .env file.")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    print("Listing available models:")
    for model in genai.list_models():
        if "generateContent" in model.supported_generation_methods:
            print(f"- {model.name} (Supported: {model.supported_generation_methods})")

# backend/ai-server/list_models.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# 1) 여러 키(GEMINI_API_KEYS)가 있으면 그 중 첫 번째 사용
# 2) 없으면 예전 방식인 GEMINI_API_KEY 하나만 사용하는 것도 허용
raw_keys = os.getenv("GEMINI_API_KEYS")
if raw_keys:
    keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
else:
    single = os.getenv("GEMINI_API_KEY", "")
    keys = [single] if single.strip() else []

if not keys:
    print("❌ Gemini API 키를 찾을 수 없습니다. .env의 GEMINI_API_KEYS 또는 GEMINI_API_KEY를 확인하세요.")
else:
    api_key = keys[0]
    genai.configure(api_key=api_key)
    print(f"✅ Using Gemini API key (prefix): {api_key[:8]}...")
    print("Listing available models:")
    for model in genai.list_models():
        if "generateContent" in getattr(model, "supported_generation_methods", []):
            print(f"- {model.name} (Supported: {model.supported_generation_methods})")
