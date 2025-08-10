# 🌞 Summer — Multi‑Provider Web Page Summarizer

Summer is a **Chrome Extension** + **FastAPI** backend that summarizes any webpage using **Ollama (local)**, **Groq**, **OpenAI**, or **IBM Watsonx** — selected right from the popup.

---

## ✨ Features
- Pick provider & model (**Ollama / Groq / OpenAI / Watsonx**)
- you may create .env file and store the apikeys and project id (for watsonx)
- Extracts page content and summarizes in one click
- Inline summary bubble + **history** view
- Backend built with **FastAPI** (+ CrewAI where applicable)
- Environment‑variable fallbacks for API keys

---

## 📂 Project Structure
```
summer-extension/
├── backend/                # FastAPI API + provider routing
│   ├── agents.py
│   ├── main.py
│   └── requirements.txt
├── extension/              # Chrome extension (MV3)
│   ├── popup.html
│   ├── popup.js
│   ├── history.html
│   ├── history.js
│   ├── content.js
│   ├── styles.css
│   ├── manifest.json
│   └── icon.png
├── .gitignore
└── README.md
```

> The extension expects your backend at **http://localhost:8000** (see `popup.js`).

---

## 🛠 Backend Setup (Python 3.12)

**Mac / Linux**
```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
**Windows (PowerShell)**
```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API will run at: **http://127.0.0.1:8000**

### 🔑 .env (optional, for cloud providers)
Create `backend/.env`:
```
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
WATSONX_API_KEY=your_watsonx_key
WATSONX_PROJECT_ID=your_project_id   # OR use space id (not both required)
WATSONX_SPACE_ID=your_space_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
OLLAMA_HOST=localhost                 # if running Ollama elsewhere, change host
```

---

## 🧩 Load the Extension (Chrome)

1. Open **chrome://extensions**
2. Enable **Developer mode**
3. Click **Load unpacked**
4. Select the `extension/` folder

Click the **Summer** icon, pick a provider/model, and hit **Summarize**.

---

## ⚙️ Changing Default Models

### Frontend (dropdown defaults)
The default **selected model** is just the **first `<option>`** in each select list inside `extension/popup.html`.  
To change it, move your preferred model to the top or add `selected` to the option.

**Ollama example (popup.html):**
```html
<select id="ollama-model">
  <!-- make your choice the first option or add selected -->
  <option value="llama3.1:8b" selected>llama3.1:8b</option>
  <option value="granite3.3:8b">granite3.3:8b</option>
  <option value="gemma3:4b">gemma3:4b</option>
  <!-- ... -->
</select>
```

You can also set a **default provider** programmatically in `popup.js`:
```js
// Force a specific default provider on popup open
providerSelect.value = "groq";           // "ollama" | "openai" | "groq" | "watsonx"
providerSelect.dispatchEvent(new Event('change'));
```

### Backend (optional fallbacks)
`backend/agents.py` uses the model you send from the popup. If you want a **server‑side fallback** when the client doesn’t provide a model, you can add this near the top:

```python
DEFAULT_MODELS = {
    "ollama":  "llama3.1:8b",
    "groq":    "qwen/qwen3-32b",
    "openai":  "gpt-4o-mini",
    "watsonx": "ibm/granite-3-3-8b-instruct"
}
```

…and then before using `model`:
```python
if not model:
    model = DEFAULT_MODELS.get(provider)
```
> Note: Current UI **always** sends a model; the backend fallback is purely optional.

---

## 🧪 Quick Test

With the backend running:
```bash
curl -X POST http://localhost:8000/summarize   -H "Content-Type: application/json"   -d '{"provider":"ollama","model":"llama3.1:8b","text":"Your text here"}'
```

You should get back JSON like:
```json
{"summary":"..."}
```

---

## 📜 License
MIT
