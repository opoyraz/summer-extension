from crewai import Crew, Agent, Task, LLM
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai import APIClient, Credentials
from bs4 import BeautifulSoup
import requests
import os
import json
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    """Clean up LLM output by removing thinking processes, meta-commentary, and unwanted formatting"""
    
    # Remove <think> tags and their content (including multiline)
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove other thinking patterns
    thinking_patterns = [
        r'<thinking>.*?</thinking>',
        r'\*thinking\*.*?\*thinking\*',
        r'\[thinking\].*?\[/thinking\]',
        r'Let me think.*?(?=\n\n|\n[A-Z])',
        r'Okay, let\'s see.*?(?=\n\n|\n[A-Z])',
        r'I need to.*?(?=\n\n|\n[A-Z])',
        r'The user wants.*?(?=\n\n|\n[A-Z])',
    ]
    
    for pattern in thinking_patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove "Summary:" prefix if it exists
    text = re.sub(r'^Summary:\s*', '', text, flags=re.IGNORECASE)
    
    # Remove excessive newlines and clean up whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Max 2 newlines
    text = text.strip()  # Trim start/end whitespace
    
    # Remove any remaining meta-commentary patterns
    meta_patterns = [
        r'^(Here\'s|Here is) (a |the )?(summary|brief summary).*?:?\s*',
        r'^Based on.*?:?\s*',
        r'^The article.*?discusses.*?:?\s*'
    ]
    
    for pattern in meta_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text.strip()

def direct_api_summarize(provider, model, apikey, text, instructions=""):
    """Direct API calls for OpenAI and Groq with improved cleaning"""
    
    print(f"🔧 Starting API call - Provider: {provider}, Model: {model}")
    print(f"🔧 Text length: {len(text)} characters")
    print(f"🔧 Has API key: {'Yes' if apikey else 'No'}")
    
    # Prepare the system message - be very explicit about output format
    system_message = """You are a professional content summarizer. Provide ONLY the final summary without any thinking process, reasoning, meta-commentary, or explanations. 

Do NOT include:
- <think> tags or thinking processes
- "Here's a summary" or similar introductions  
- Your reasoning or analysis process
- Meta-commentary about the task

Provide ONLY the direct, clean summary content."""
    
    # Prepare the user message
    if instructions:
        user_message = f"{instructions}\n\nText to summarize:\n{text}"
    else:
        user_message = f"Provide a brief, concise summary of the following text (2-3 paragraphs max):\n\n{text}"
    
    # API endpoints
    api_urls = {
        "openai": "https://api.openai.com/v1/chat/completions",
        "groq": "https://api.groq.com/openai/v1/chat/completions"
    }
    
    # Make the API call
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.1,
        "max_tokens": 800
    }
    
    print(f"🌐 Making API request to: {api_urls[provider]}")
    print(f"🌐 Payload model: {payload['model']}")
    
    try:
        response = requests.post(
            api_urls[provider],
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📨 API Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ API Error Response: {response.text}")
            raise Exception(f"API error: {response.status_code} - {response.text}")
        
        data = response.json()
        print(f"📊 API Response Keys: {list(data.keys())}")
        
        if 'choices' not in data or not data['choices']:
            print(f"❌ No choices in response: {data}")
            raise Exception(f"Invalid API response format: {data}")
        
        raw_summary = data['choices'][0]['message']['content']
        print(f"✅ Raw summary received: {len(raw_summary)} characters")
        print(f"📄 Raw summary preview: {raw_summary[:200]}...")
        
        # Clean the summary using our new function
        summary = clean_summary_output(raw_summary)
        
        if not summary:
            print("❌ Summary is empty after cleaning")
            raise Exception("Generated summary is empty after cleaning")
        
        print(f"✅ Cleaned summary: {len(summary)} characters")
        print(f"📄 Clean summary preview: {summary[:200]}...")
        return summary
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        raise Exception(f"Network error calling {provider}: {str(e)}")
    except Exception as e:
        print(f"❌ API call failed: {e}")
        raise Exception(f"Failed to get summary from {provider}: {str(e)}")

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

    # Limit text length to avoid token limits
    max_chars = 6000
    if len(text) > max_chars:
        text = text[:max_chars] + "..."
        print(f"📄 Text truncated to {max_chars} characters")

    print(f"📊 Processing text: {len(text)} characters")
    print(f"📄 Text preview: {text[:200]}...")

    if not provider or not model:
        raise ValueError("Missing required fields: provider or model")

    # Use .env fallback for API keys and other config if not provided
    if provider == "openai" and not apikey:
        apikey = os.getenv("OPENAI_API_KEY", "")
        print("🔑 Using OpenAI API key from .env file")
    
    elif provider == "groq" and not apikey:
        apikey = os.getenv("GROQ_API_KEY", "")
        print("🔑 Using Groq API key from .env file")
    
    elif provider == "watsonx":
        # Use .env fallback for all Watsonx fields
        if not apikey:
            apikey = os.getenv("WATSONX_API_KEY", "")
            print("🔑 Using Watsonx API key from .env file")
        
        watsonx_url = body.get("watsonx_url") or os.getenv("WATSONX_URL", "")
        project_id = body.get("project_id") or os.getenv("WATSONX_PROJECT_ID", "")
        space_id = body.get("space_id") or os.getenv("WATSONX_SPACE_ID", "")
        
        print(f"🔑 Using Watsonx config - URL: {'✓' if watsonx_url else '✗'}, Project: {'✓' if project_id else '✗'}, Space: {'✓' if space_id else '✗'}")

    # Setup LLM based on provider
    try:
        if provider == "watsonx":
            # Handle Watsonx setup
            if not apikey:
                raise ValueError("Watsonx API key is required. Please configure in .env file or provide in UI.")
            
            if not watsonx_url:
                raise ValueError("Watsonx URL is required. Please configure in .env file or provide in UI.")
            
            # Require EITHER project_id OR space_id, not both
            if not project_id and not space_id:
                raise ValueError("Watsonx requires either project_id OR space_id. Please configure in .env file or provide in UI.")

            print(f"🛠 Setting up Watsonx model: {model}")
            
            # Create credentials object properly
            credentials = Credentials(
                api_key=apikey,
                url=watsonx_url
            )
            client = APIClient(credentials=credentials)
            
            # Use project_id if available, otherwise use space_id
            model_params = {
                "model_id": model,
                "params": {
                    "decoding_method": "greedy",
                    "max_new_tokens": 800,
                    "temperature": 0.1
                },
                "credentials": credentials
            }
            
            if project_id:
                model_params["project_id"] = project_id
                print(f"🔑 Using project_id: {project_id}")
            else:
                model_params["space_id"] = space_id
                print(f"🔑 Using space_id: {space_id}")
            
            llm = Model(**model_params)

        elif provider == "ollama":
            print(f"🛠 Setting up Ollama model: {model}")
            ollama_host = os.getenv('OLLAMA_HOST', 'localhost')
            ollama_url = f"http://{ollama_host}:11434"
            # For Ollama - use LiteLLM with proper base URL
            llm = LLM(
                model=f"ollama/{model}",
                base_url=ollama_url,
                api_key="not-needed"
            )

        elif provider in ["openai", "groq"]:
            if not apikey:
                raise ValueError(f"{provider.title()} API key is required. Please configure in .env file or provide in UI.")
            
            # Use direct API calls for better control
            print(f"🛠 Using direct API for {provider} model: {model}")
            
            try:
                summary_text = direct_api_summarize(provider, model, apikey, text, instructions)
                
                if not summary_text or len(summary_text.strip()) < 10:
                    raise Exception("Generated summary is too short or empty")
                
                print(f"✅ Summary generated successfully!")
                print(f"📄 Summary length: {len(summary_text)} characters")
                print(f"📄 Summary preview: {summary_text[:100]}...")
                
                return {"summary": summary_text}
                
            except Exception as e:
                print(f"❌ Direct API summarization failed: {e}")
                raise e

        else:
            raise ValueError(f"Unsupported provider: {provider}")

        print("✅ LLM setup completed successfully")

    except Exception as e:
        print(f"❌ LLM setup failed: {e}")
        raise Exception(f"Failed to initialize {provider} model '{model}': {str(e)}")

    # Create a single summarization task (simplified approach)
    try:
        print("📝 Creating summarization agent...")
        
        # Prepare the prompt based on instructions
        if instructions:
            task_prompt = f"""
{instructions}

Please summarize the following content:

{text}
"""
        else:
            task_prompt = f"""
Please create a clear, concise summary of the following content. Focus on the main points and key information:

{text}
"""

        # For Watsonx, use direct model generation
        if provider == "watsonx":
            print("🚀 Using Watsonx direct generation...")
            print(f"📋 Task prompt length: {len(task_prompt)} characters")
            
            try:
                response = llm.generate_text(prompt=task_prompt)
                print(f"📨 Watsonx response type: {type(response)}")
                print(f"📨 Watsonx response: {response}")
                
                # Handle different response formats
                if hasattr(response, 'generated_text'):
                    summary_text = response.generated_text
                    print(f"✅ Found generated_text attribute: {len(summary_text)} chars")
                elif isinstance(response, dict):
                    if 'generated_text' in response:
                        summary_text = response['generated_text']
                        print(f"✅ Found generated_text in dict: {len(summary_text)} chars")
                    elif 'results' in response and response['results']:
                        # Sometimes IBM returns results array
                        result = response['results'][0]
                        summary_text = result.get('generated_text', str(result))
                        print(f"✅ Found generated_text in results: {len(summary_text)} chars")
                    else:
                        print(f"❌ Dict keys: {list(response.keys())}")
                        summary_text = str(response)
                else:
                    print(f"❌ Unknown response format, converting to string")
                    summary_text = str(response)
                
                summary_text = clean_summary_output(summary_text)
                
                print(f"📄 Cleaned Watsonx summary: {summary_text[:200]}...")
                
            except Exception as e:
                print(f"❌ Watsonx generation failed: {e}")
                raise Exception(f"Watsonx model generation failed: {str(e)}")

        else:
            # For other providers (Ollama), use CrewAI
            print("🚀 Using CrewAI for summarization...")
            
            summarizer = Agent(
                role="Expert Content Analyst & Summarizer",
                goal="Transform complex text into clear, actionable summaries that preserve essential information while eliminating noise. Create summaries that enable readers to quickly understand key insights, main arguments, important facts, and any actionable items without reading the full content.",
                backstory="""You are a seasoned content analyst with 15+ years of experience in information synthesis and knowledge distillation. You've worked as a research analyst for top consulting firms, helping executives quickly grasp complex reports, market analyses, and technical documents. 

Your expertise spans multiple domains including business, technology, science, and current events. You have a unique ability to identify the most critical information within any text and present it in a way that respects the reader's time while ensuring no crucial details are lost.

Your methodology focuses on three pillars:
1. **Accuracy**: Never distort or misrepresent the original meaning
2. **Clarity**: Use simple, direct language that anyone can understand  
3. **Actionability**: Highlight insights that readers can actually use

You understand that different content types require different summarization approaches - news articles need context and implications, technical documents need key findings and methodologies, business content needs insights and recommendations.

IMPORTANT: You provide ONLY the final summary content. Never include thinking processes, reasoning, meta-commentary, or explanations about your approach.""",
                verbose=False,
                allow_delegation=False,
                llm=llm
            )

            summarization_task = Task(
                description=task_prompt,
                expected_output="""A comprehensive yet concise summary that includes:

**Structure Requirements:**
- 2-4 well-organized paragraphs (aim for 150-300 words total)
- Lead with the most important information first
- Use clear, professional language accessible to a general audience

**Content Requirements:**
- **Main Theme**: What is this content fundamentally about?
- **Key Points**: 3-5 most important facts, findings, or arguments
- **Context**: Any necessary background information for understanding
- **Implications**: Why this matters or what it means for readers
- **Specifics**: Include relevant numbers, dates, names, or statistics when important

**Quality Standards:**
- Maintain factual accuracy - never add information not in the source
- Preserve the original tone and perspective while being objective
- Use active voice and clear, direct sentences
- Ensure the summary can stand alone without requiring the original text
- If technical content: explain complex concepts in simpler terms
- If news content: include who, what, when, where, why context
- If opinion content: clearly distinguish facts from opinions

CRITICAL: Provide ONLY the summary content. Do NOT include thinking processes, reasoning explanations, introductory phrases like "Here's a summary", or any meta-commentary about the task.

The summary should enable a busy reader to understand the essential information and decide whether they need to read the full content.""",
                agent=summarizer
            )

            crew = Crew(
                agents=[summarizer],
                tasks=[summarization_task],
                verbose=False
            )

            result = crew.kickoff()

            # Extract summary from CrewAI result
            if hasattr(result, 'raw'):
                summary_text = result.raw
            elif isinstance(result, dict):
                summary_text = result.get('final_output', str(result))
            else:
                summary_text = str(result)

            # Clean the CrewAI summary as well
            summary_text = clean_summary_output(summary_text)

        # Final validation and cleaning
        summary_text = summary_text.strip()
        
        if not summary_text or len(summary_text) < 10:
            raise Exception("Generated summary is too short or empty after cleaning")

        print(f"✅ Summary generated successfully!")
        print(f"📄 Summary length: {len(summary_text)} characters")
        print(f"📄 Summary preview: {summary_text[:100]}...")

        return {"summary": summary_text}

    except Exception as e:
        print(f"❌ Summarization failed: {e}")
        raise Exception(f"Summarization failed: {str(e)}")