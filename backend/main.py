from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from agents import summarize_with_provider
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with extension ID or allowed origins in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/providers")
async def get_available_providers():
    """Check which providers have API keys available in .env"""
    available_providers = {}
    
    # Check OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    available_providers["openai"] = {
        "has_apikey": bool(openai_key and openai_key.strip())
    }
    
    # Check Groq
    groq_key = os.getenv("GROQ_API_KEY")
    available_providers["groq"] = {
        "has_apikey": bool(groq_key and groq_key.strip())
    }
    
    # Check Watsonx - all fields required
    watsonx_key = os.getenv("WATSONX_API_KEY")
    watsonx_url = os.getenv("WATSONX_URL")
    watsonx_project_id = os.getenv("WATSONX_PROJECT_ID")
    watsonx_space_id = os.getenv("WATSONX_SPACE_ID")
    
    available_providers["watsonx"] = {
        "has_apikey": bool(watsonx_key and watsonx_key.strip()),
        "has_url": bool(watsonx_url and watsonx_url.strip()),
        "has_project_id": bool(watsonx_project_id and watsonx_project_id.strip()),
        "has_space_id": bool(watsonx_space_id and watsonx_space_id.strip()),
        "all_configured": all([
            watsonx_key and watsonx_key.strip(),
            watsonx_url and watsonx_url.strip(),
            # Require EITHER project_id OR space_id, not both
            (watsonx_project_id and watsonx_project_id.strip()) or (watsonx_space_id and watsonx_space_id.strip())
        ])
    }
    
    # Ollama doesn't need API key
    available_providers["ollama"] = {
        "has_apikey": True  # Always available locally
    }
    
    print(f"🔍 Available providers: {available_providers}")
    return available_providers

@app.post("/summarize")
async def summarize(request: Request):
    try:
        body = await request.json()
        print("🚀 Incoming request body:", body)

        summary = summarize_with_provider(request, body)
        print("✅ Returning summary:", summary)
        return summary
    except Exception as e:
        print(f"❌ Backend error: {e}")
        return {"error": str(e)}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5050)
