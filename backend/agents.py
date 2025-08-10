from crewai import Crew, Agent, Task, LLM
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai import APIClient, Credentials
from bs4 import BeautifulSoup
import requests
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -------------------------------------------------------------------
# Extraction & Cleaning
# -------------------------------------------------------------------

def extract_article_text(url):
    try:
        headers = {'User-Agent': 'Chrome/120.0.0.0 Summer-Extension/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Try common article containers
        selectors = ['article', 'main', 'section', 'div[class*="content"]', 'div[class*="article"]']
        for selector in selectors:
            candidate = soup.select_one(selector)
            if candidate:
                text = candidate.get_text(separator=' ', strip=True)
                if len(text.split()) > 100:
                    return text

        # Fallback: all paragraphs
        paragraphs = soup.find_all('p')
        full_text = ' '.join(p.get_text() for p in paragraphs)
        return full_text.strip()
    except Exception as e:
        print(f"❌ Failed to extract content: {e}")
        return ""

def clean_summary_output(text):
    """Remove thinking/meta and tidy whitespace from LLM output."""
    # Strip think tags and similar
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    for pat in [
        r'<thinking>.*?</thinking>',
        r'\*thinking\*.*?\*thinking\*',
        r'\[thinking\].*?\[/thinking\]',
        r'Let me think.*?(?=\n\n|\n[A-Z])',
        r'Okay, let\'s see.*?(?=\n\n|\n[A-Z])',
        r'I need to.*?(?=\n\n|\n[A-Z])',
        r'The user wants.*?(?=\n\n|\n[A-Z])',
    ]:
        text = re.sub(pat, '', text, flags=re.DOTALL | re.IGNORECASE)

    text = re.sub(r'^Summary:\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text).strip()

    for pat in [
        r'^(Here\'s|Here is) (a |the )?(summary|brief summary).*?:?\s*',
        r'^Based on.*?:?\s*',
        r'^The article.*?discusses.*?:?\s*'
    ]:
        text = re.sub(pat, '', text, flags=re.IGNORECASE)

    return text.strip()

def clean_input_text(text: str) -> str:
    """Normalize and de-noise extracted page text before summarization."""
    if not text:
        return ""
    boilerplate_patterns = [
        r'(?i)accept all cookies.*', r'(?i)cookie settings.*', r'(?i)subscribe now.*',
        r'(?i)sign in.*', r'(?i)log in.*', r'(?i)read more.*', r'(?i)advertisement',
        r'(?i)newsletter signup.*', r'(?i)share this.*', r'(?i)related articles.*'
    ]
    for pat in boilerplate_patterns:
        text = re.sub(pat, '', text)

    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)

    lines = [ln.strip() for ln in text.splitlines()]
    deduped, prev = [], None
    for ln in lines:
        if ln and ln != prev:
            deduped.append(ln)
        prev = ln
    text = '\n'.join(deduped).strip()

    max_chars = 8000
    if len(text) > max_chars:
        text = text[:max_chars] + "..."
    return text

# -------------------------------------------------------------------
# Provider: OpenAI & Groq (direct API)
# -------------------------------------------------------------------

def direct_api_summarize(provider, model, apikey, text, instructions=""):
    """Direct API calls for OpenAI and Groq with improved cleaning."""
    print(f"🔧 Starting API call - Provider: {provider}, Model: {model}")
    print(f"🔧 Text length (pre-clean): {len(text)} characters")

    text = clean_input_text(text)
    print(f"🔧 Text length (post-clean): {len(text)} characters")
    print(f"🔧 Has API key: {'Yes' if apikey else 'No'}")

    system_message = (
        "You are a professional content summarizer. Provide ONLY the final summary. "
        "No meta-commentary, no thinking traces, no prefaces."
    )
    user_message = (
        f"{instructions}\n\nText to summarize:\n{text}"
        if instructions
        else f"Provide a concise summary (2–3 short paragraphs) of the following:\n\n{text}"
    )

    api_urls = {
        "openai": "https://api.openai.com/v1/chat/completions",
        "groq": "https://api.groq.com/openai/v1/chat/completions"
    }
    headers = {"Authorization": f"Bearer {apikey}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.1,
        "max_tokens": 800
    }

    try:
        response = requests.post(api_urls[provider], headers=headers, json=payload, timeout=30)
        print(f"📨 API Response Status: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            raise Exception(f"Invalid API response: {str(data)[:300]}")
        raw = choices[0]["message"]["content"]
        summary = clean_summary_output(raw).strip()
        if not summary:
            raise Exception("Generated summary is empty after cleaning")
        return summary
    except Exception as e:
        raise Exception(f"Failed to get summary from {provider}: {str(e)}")

# -------------------------------------------------------------------
# Provider: Ollama (local) — direct fast path
# -------------------------------------------------------------------

def direct_ollama_summarize(model: str, text: str, instructions: str = "") -> str:
    """Fast path: call Ollama's local REST API directly (no CrewAI)."""
    ollama_host = os.getenv("OLLAMA_HOST", "localhost")
    base = f"http://{ollama_host}:11434"

    text = clean_input_text(text)
    system_msg = (
        "You are a professional content summarizer. Output ONLY the final summary. "
        "No meta-commentary, no thinking traces, no prefaces."
    )
    user_prompt = (
        f"{instructions}\n\nText to summarize:\n{text}"
        if instructions
        else f"Summarize the following text in 2–4 short paragraphs:\n\n{text}"
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "options": {"temperature": 0.1}
    }

    try:
        resp = requests.post(f"{base}/api/chat", json=payload, timeout=90)
        resp.raise_for_status()
        data = resp.json()
        content = data["message"]["content"]
        cleaned = clean_summary_output(content)
        if not cleaned:
            raise Exception("Empty summary from Ollama.")
        return cleaned
    except Exception as e:
        raise Exception(f"Ollama direct summarize failed: {e}")

# -------------------------------------------------------------------
# Main entry
# -------------------------------------------------------------------

def summarize_with_provider(request, body):
    provider = body.get("provider")
    model = body.get("model")
    apikey = body.get("apikey", "")
    instructions = body.get("instructions", "")
    text = body.get("text", "")
    url = body.get("url")

    print(f"🔍 Debug - Provider: {provider}")
    print(f"🔍 Debug - Model: {model}")
    print(f"🔍 Debug - Text length: {len(text)} characters")
    print(f"🔍 Debug - Has URL: {'Yes' if url else 'No'}")
    print(f"🔍 Debug - Instructions: {instructions or 'None'}")

    # Handle text extraction
    if url and not text:
        print("🌐 Extracting content from URL...")
        text = extract_article_text(url)

    if not text or len(text.strip()) < 20:
        raise ValueError("No meaningful text content found to summarize")

    cleaned_text = clean_input_text(text)
    print(f"📊 Processing cleaned text: {len(cleaned_text)} characters")
    print(f"📄 Cleaned text preview: {cleaned_text[:200]}...")

    if not provider or not model:
        raise ValueError("Missing required fields: provider or model")

    # API key/env fallbacks
    watsonx_url = None
    project_id = None
    space_id = None

    if provider == "openai" and not apikey:
        apikey = os.getenv("OPENAI_API_KEY", "")
        print("🔑 Using OpenAI API key from .env file")
    elif provider == "groq" and not apikey:
        apikey = os.getenv("GROQ_API_KEY", "")
        print("🔑 Using Groq API key from .env file")
    elif provider == "watsonx":
        if not apikey:
            apikey = os.getenv("WATSONX_API_KEY", "")
            print("🔑 Using Watsonx API key from .env file")
        watsonx_url = body.get("watsonx_url") or os.getenv("WATSONX_URL", "")
        project_id = body.get("project_id") or os.getenv("WATSONX_PROJECT_ID", "")
        space_id = body.get("space_id") or os.getenv("WATSONX_SPACE_ID", "")
        print(f"🔑 Watsonx config - URL: {'✓' if watsonx_url else '✗'}, "
              f"Project: {'✓' if project_id else '✗'}, Space: {'✓' if space_id else '✗'}")

    # ------------------------
    # Provider branching
    # ------------------------

    # OpenAI / Groq → direct API
    if provider in ["openai", "groq"]:
        if not apikey:
            raise ValueError(f"{provider.title()} API key is required. Provide in UI or .env.")
        print(f"🛠 Using direct API for {provider} model: {model}")
        summary_text = direct_api_summarize(provider, model, apikey, cleaned_text, instructions)
        return {"summary": summary_text}

    # Watsonx → direct model call
    if provider == "watsonx":
        if not apikey:
            raise ValueError("Watsonx API key is required.")
        if not watsonx_url:
            raise ValueError("Watsonx URL is required.")
        if not project_id and not space_id:
            raise ValueError("Watsonx requires either project_id OR space_id.")

        print(f"🛠 Setting up Watsonx model: {model}")
        credentials = Credentials(api_key=apikey, url=watsonx_url)
        _ = APIClient(credentials=credentials)  # client kept for completeness

        model_params = {
            "model_id": model,
            "params": {"decoding_method": "greedy", "max_new_tokens": 800, "temperature": 0.1},
            "credentials": credentials
        }
        if project_id:
            model_params["project_id"] = project_id
            print(f"🔑 Using project_id: {project_id}")
        else:
            model_params["space_id"] = space_id
            print(f"🔑 Using space_id: {space_id}")

        llm = Model(**model_params)

        # Build prompt
        if instructions:
            task_prompt = f"{instructions}\n\nPlease summarize the following content:\n\n{cleaned_text}"
        else:
            task_prompt = (
                "Please create a clear, concise summary of the following content. "
                "Focus on the main points and key information:\n\n"
                f"{cleaned_text}"
            )

        try:
            response = llm.generate_text(prompt=task_prompt)
            # Normalize IBM responses
            if hasattr(response, 'generated_text'):
                summary_text = response.generated_text
            elif isinstance(response, dict):
                if 'generated_text' in response:
                    summary_text = response['generated_text']
                elif 'results' in response and response['results']:
                    summary_text = response['results'][0].get('generated_text', str(response['results'][0]))
                else:
                    summary_text = str(response)
            else:
                summary_text = str(response)

            summary_text = clean_summary_output(summary_text).strip()
            if not summary_text or len(summary_text) < 10:
                raise Exception("Generated summary is too short or empty after cleaning")
            return {"summary": summary_text}
        except Exception as e:
            raise Exception(f"Watsonx model generation failed: {str(e)}")

    # Ollama → choose fast vs agentic
    if provider == "ollama":
        mode = os.getenv("OLLAMA_MODE", "fast").lower()
        print(f"🛞 Ollama mode: {mode}")

        # Fast path: direct REST (no CrewAI)
        if mode == "fast":
            print(f"⚡ Using direct Ollama REST path for model: {model}")
            summary_text = direct_ollama_summarize(model, cleaned_text, instructions)
            return {"summary": summary_text}

        # Agentic path: Cleaner Agent → Summarizer Agent via CrewAI
        print(f"🤝 Using CrewAI agentic flow for Ollama model: {model}")
        try:
            ollama_host = os.getenv('OLLAMA_HOST', 'localhost')
            ollama_url = f"http://{ollama_host}:11434"
            llm = LLM(model=f"ollama/{model}", base_url=ollama_url, api_key="not-needed")

            cleaner = Agent(
                role="Content Cleaner",
                goal=("Normalize and de-noise raw webpage text by removing boilerplate (headers, footers, cookie prompts, ads), "
                      "deduplicating lines, and preserving only semantically meaningful paragraphs."),
                backstory=("You specialize in text hygiene for downstream NLP tasks. Output is STRICTLY the cleaned text."),
                verbose=False,
                allow_delegation=False,
                llm=llm
            )

            summarizer = Agent(
                role="Expert Content Analyst & Summarizer",
                goal=("Transform cleaned text into a clear, actionable summary that preserves essential information."),
                backstory=("You write concise, standalone summaries. No meta commentary—only the final summary."),
                verbose=False,
                allow_delegation=False,
                llm=llm
            )

            clean_task = Task(
                description=f"""Clean the following text. 
Return ONLY the cleaned text—no preface, no notes, no headings.

TEXT:
{cleaned_text}
""",
                expected_output="Cleaned text only.",
                agent=cleaner
            )

            if instructions:
                summarization_prompt = f"""{instructions}

Please summarize the following CLEANED content:

<<BEGIN CLEANED TEXT>>
{{cleaned}}
<<END CLEANED TEXT>>"""
            else:
                summarization_prompt = """Please create a clear, concise summary (2–4 short paragraphs) of the CLEANED content below.
Lead with the most important information first. Do not include meta commentary.

<<BEGIN CLEANED TEXT>>
{cleaned}
<<END CLEANED TEXT>>"""

            summarization_task = Task(
                description=summarization_prompt,
                expected_output=("A concise, well-structured summary (150–300 words), "
                                 "capturing main theme, 3–5 key points, and implications."),
                agent=summarizer
            )

            # Step 1: Clean
            crew = Crew(agents=[cleaner, summarizer], tasks=[clean_task], verbose=False)
            clean_result = crew.kickoff()
            if hasattr(clean_result, "raw") and clean_result.raw.strip():
                cleaned_for_summary = clean_result.raw.strip()
            else:
                cleaned_for_summary = cleaned_text  # fallback to deterministic cleaner

            # Step 2: Summarize
            summarization_task.description = summarization_task.description.replace("{cleaned}", cleaned_for_summary)
            crew2 = Crew(agents=[summarizer], tasks=[summarization_task], verbose=False)
            result = crew2.kickoff()

            if hasattr(result, 'raw'):
                summary_text = result.raw
            elif isinstance(result, dict):
                summary_text = result.get('final_output', str(result))
            else:
                summary_text = str(result)

            summary_text = clean_summary_output(summary_text).strip()
            if not summary_text or len(summary_text) < 10:
                raise Exception("Generated summary is too short or empty after cleaning")
            return {"summary": summary_text}

        except Exception as e:
            print(f"⚠️ CrewAI path failed ({e}). Falling back to direct Ollama call...")
            summary_text = direct_ollama_summarize(model, cleaned_text, instructions)
            return {"summary": summary_text}

    # Unsupported
    raise ValueError(f"Unsupported provider: {provider}")
